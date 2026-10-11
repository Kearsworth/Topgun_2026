"""Simulated ESP32 sensing node: a drying pile of coffee beans.

Publishes contract-valid readings, honours fan commands (closed loop), and
registers an 'offline' Last Will so dashboards can detect node loss.

    python -m sim.sim_esp32 --scenario rainy --speed 720
    mosquitto_pub -t topgun/team01/esp32/esp32-sim/cmd -m '{"v":1,"outputs":{"fan_pct":80}}'
"""
import argparse
import json
import math
import os
import random
import time
from datetime import datetime

from topgun import contract
from topgun.mqtt import connect, make_client, publish_json

SCENARIOS = {
    # rain_prob: chance per sim-hour that it is raining; fault: sensor glitch probability
    "sunny": {"rain_prob": 0.02, "fault": 0.0},
    "rainy": {"rain_prob": 0.6, "fault": 0.0},
    "mixed": {"rain_prob": 0.25, "fault": 0.0},
    "faulty": {"rain_prob": 0.1, "fault": 0.08},
}

# Capacitive probe calibration used to fake raw ADC counts (two-point, see firmware notes).
ADC_DRY, ADC_WET, M_DRY, M_WET = 3200, 1400, 8.0, 30.0


class DryingPile:
    """Very simple dry-process model: moisture decays toward an RH-dependent equilibrium."""

    def __init__(self, weight_kg: float, moisture: float, rain_prob: float):
        self.dry_mass = weight_kg * (1 - moisture)
        self.moisture = moisture
        self.rain_prob = rain_prob
        self.raining = False

    def step(self, sim_dt: datetime, dt_h: float, fan_pct: float) -> dict:
        hour = sim_dt.hour + sim_dt.minute / 60
        sun = max(0.0, math.sin(math.pi * (hour - 6) / 12))
        if random.random() < dt_h:  # re-roll weather roughly once per sim-hour
            self.raining = random.random() < self.rain_prob
        if self.raining:
            sun *= 0.15
        air_temp = 25 + 8 * sun + random.gauss(0, 0.3)
        air_rh = min(99.0, (95 if self.raining else 88) - 30 * sun + random.gauss(0, 1.5))
        equilibrium = 0.06 + 0.12 * (air_rh / 100) ** 2
        k = 0.015 + 0.09 * sun + 0.05 * fan_pct / 100  # per hour
        if self.moisture > equilibrium:
            self.moisture -= k * (self.moisture - equilibrium) * dt_h
        else:  # re-absorbs water slowly in humid air
            self.moisture += 0.01 * (equilibrium - self.moisture) * dt_h
        fermenting = self.moisture > 0.25 and air_rh > 85
        return {
            "air_temp_c": round(air_temp, 2),
            "air_rh_pct": round(max(0.0, air_rh), 1),
            "pile_temp_c": round(air_temp + 3 * sun + (2.5 if fermenting else 0) + random.gauss(0, 0.2), 2),
            "weight_kg": round(self.dry_mass / (1 - self.moisture) + random.gauss(0, 0.005), 3),
            "light_lux": round(sun * 90000 + random.uniform(0, 300)),
            "rain": self.raining,
        }


def moisture_reading(true_pct: float) -> tuple[float, int]:
    measured = true_pct + random.gauss(0, 0.4)
    adc = ADC_DRY + (measured - M_DRY) * (ADC_WET - ADC_DRY) / (M_WET - M_DRY)
    return round(measured, 2), int(adc)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--node-id", default="esp32-sim")
    ap.add_argument("--batch-id", default="CRB-2026-001")
    ap.add_argument("--scenario", choices=SCENARIOS, default="mixed")
    ap.add_argument("--speed", type=float, default=720, help="sim seconds per real second (720 = 1 real s is 12 sim min)")
    ap.add_argument("--interval", type=float, default=5, help="real seconds between messages")
    ap.add_argument("--weight", type=float, default=10.0, help="initial wet weight kg")
    ap.add_argument("--moisture", type=float, default=50.0, help="initial moisture %% (fresh cherries ~50-60)")
    ap.add_argument("--crash-after", type=float, default=0, help="drop the connection abruptly after N real seconds (tests LWT)")
    ap.add_argument("--seed", type=int)
    args = ap.parse_args()
    if args.seed is not None:
        random.seed(args.seed)

    scen = SCENARIOS[args.scenario]
    pile = DryingPile(args.weight, args.moisture / 100, scen["rain_prob"])
    state = {"batch_id": args.batch_id, "interval": args.interval, "fan_pct": 0.0}

    status_topic = contract.status("esp32", args.node_id)
    cmd_topic = contract.cmd("esp32", args.node_id)
    client = make_client(args.node_id, status_topic, {"v": 1, "node_id": args.node_id, "state": "offline"})

    def on_connect(c, userdata, flags, reason_code, properties):
        print(f"[{args.node_id}] connected ({reason_code}); scenario={args.scenario}")
        publish_json(c, status_topic, {"v": 1, "node_id": args.node_id, "state": "online", "ts": time.time(), "fw": "sim-0.1"}, qos=1, retain=True)
        c.subscribe(cmd_topic, qos=1)

    def on_message(c, userdata, msg):
        try:
            command = json.loads(msg.payload)
        except json.JSONDecodeError:
            print(f"[{args.node_id}] ignored non-JSON command")
            return
        if errs := contract.validate("command", command):
            print(f"[{args.node_id}] invalid command: {errs}")
            return
        state["batch_id"] = command.get("batch_id", state["batch_id"])
        state["interval"] = command.get("interval_s", state["interval"])
        state["fan_pct"] = command.get("outputs", {}).get("fan_pct", state["fan_pct"])
        print(f"[{args.node_id}] cmd applied -> {state}")

    client.on_connect = on_connect
    client.on_message = on_message
    connect(client)

    sim_now = time.time()
    started = time.monotonic()
    seq = 0
    try:
        while True:
            time.sleep(state["interval"])
            if args.crash_after and time.monotonic() - started > args.crash_after:
                print(f"[{args.node_id}] simulating crash (no clean disconnect) -> broker should publish LWT")
                client.socket().close()
                os._exit(1)
            dt_s = state["interval"] * args.speed
            sim_now += dt_s
            readings = pile.step(datetime.fromtimestamp(sim_now), dt_s / 3600, state["fan_pct"])
            moist, adc = moisture_reading(pile.moisture * 100)
            readings["bean_moisture_pct"] = moist
            if random.random() < scen["fault"]:  # glitch: spike or missing value
                if random.random() < 0.5:
                    readings["bean_moisture_pct"] = min(100.0, moist + random.uniform(10, 25))
                else:
                    readings.pop("air_rh_pct")
            payload = {"v": 1, "node_id": args.node_id, "batch_id": state["batch_id"], "ts": round(sim_now, 1),
                       "seq": seq, "readings": readings, "raw": {"adc_moisture": adc}}
            publish_json(client, contract.esp32_data(args.node_id), payload)
            print(f"[{args.node_id}] {datetime.fromtimestamp(sim_now):%m-%d %H:%M} moisture={moist:5.2f}% "
                  f"rh={readings.get('air_rh_pct', '--')} rain={readings['rain']} fan={state['fan_pct']:.0f}%")
            seq += 1
    except KeyboardInterrupt:
        publish_json(client, status_topic, {"v": 1, "node_id": args.node_id, "state": "offline", "ts": time.time()}, qos=1, retain=True).wait_for_publish(2)
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
