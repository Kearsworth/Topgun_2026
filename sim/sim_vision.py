"""Simulated Raspberry Pi 5 vision node: publishes tray analysis results.

Publishes every --interval seconds, or immediately on a capture command:
    mosquitto_pub -t topgun/team01/vision/pi5-sim/cmd -m '{"v":1,"action":"capture","batch_id":"CRB-2026-002"}'
"""
import argparse
import json
import random
import statistics
import time
import uuid

from topgun import contract
from topgun.mqtt import connect, make_client, publish_json

# Class probabilities per bean (provisional class set; see research/01-training-datasets.md)
QUALITY = {
    "good": {"normal": 0.975, "black": 0.004, "partial_black": 0.004, "sour": 0.004, "broken": 0.008, "insect": 0.003, "moldy": 0.002},
    "average": {"normal": 0.93, "black": 0.012, "partial_black": 0.012, "sour": 0.012, "broken": 0.02, "insect": 0.008, "moldy": 0.006},
    "poor": {"normal": 0.82, "black": 0.04, "partial_black": 0.03, "sour": 0.03, "broken": 0.04, "insect": 0.02, "moldy": 0.02},
}


def analyse_tray(node_id: str, batch_id: str, quality: str, detailed: bool) -> dict:
    probs = QUALITY[quality]
    n = random.randint(120, 180)
    classes = random.choices(list(probs), weights=list(probs.values()), k=n)
    beans = []
    for i, cls in enumerate(classes):
        length = random.gauss(8.3 if cls != "broken" else 6.0, 0.6)
        conf = random.uniform(0.85, 0.99) if random.random() > 0.05 else random.uniform(0.4, 0.6)
        beans.append({"id": i, "x": round(random.uniform(0, 1920)), "y": round(random.uniform(0, 1440)),
                      "length_mm": round(length, 2), "width_mm": round(length * random.uniform(0.7, 0.8), 2),
                      "cls": cls, "conf": round(conf, 3)})
    lengths = [b["length_mm"] for b in beans]
    counts = {c: classes.count(c) for c in probs if classes.count(c)}
    defects = n - counts.get("normal", 0)
    result = {
        "v": 1, "node_id": node_id, "batch_id": batch_id, "ts": round(time.time(), 1),
        "image_id": uuid.uuid4().hex[:12], "bean_count": n,
        "size_mm": {"mean": round(statistics.mean(lengths), 2), "std": round(statistics.stdev(lengths), 2),
                    "min": round(min(lengths), 2), "max": round(max(lengths), 2)},
        "class_counts": counts, "defect_rate_pct": round(100 * defects / n, 2),
        "low_confidence_count": sum(b["conf"] < 0.7 for b in beans),
        "model": "sim", "proc_ms": round(random.uniform(700, 1300)),
    }
    if detailed:
        result["beans"] = beans
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--node-id", default="pi5-sim")
    ap.add_argument("--batch-id", default="CRB-2026-001")
    ap.add_argument("--quality", choices=QUALITY, default="average")
    ap.add_argument("--interval", type=float, default=30, help="real seconds between automatic analyses (0 = only on command)")
    ap.add_argument("--detailed", action="store_true", help="include per-bean list")
    ap.add_argument("--seed", type=int)
    args = ap.parse_args()
    if args.seed is not None:
        random.seed(args.seed)

    state = {"batch_id": args.batch_id, "capture": False}
    status_topic = contract.status("vision", args.node_id)
    cmd_topic = contract.cmd("vision", args.node_id)
    client = make_client(args.node_id, status_topic, {"v": 1, "node_id": args.node_id, "state": "offline"})

    def on_connect(c, userdata, flags, reason_code, properties):
        print(f"[{args.node_id}] connected ({reason_code}); quality={args.quality}")
        publish_json(c, status_topic, {"v": 1, "node_id": args.node_id, "state": "online", "ts": time.time(), "fw": "sim-0.1"}, qos=1, retain=True)
        c.subscribe(cmd_topic, qos=1)

    def on_message(c, userdata, msg):
        try:
            command = json.loads(msg.payload)
        except json.JSONDecodeError:
            return
        if errs := contract.validate("command", command):
            print(f"[{args.node_id}] invalid command: {errs}")
            return
        state["batch_id"] = command.get("batch_id", state["batch_id"])
        if command.get("action") == "capture":
            state["capture"] = True

    client.on_connect = on_connect
    client.on_message = on_message
    connect(client)

    last = 0.0
    try:
        while True:
            time.sleep(0.2)
            due = args.interval and time.monotonic() - last >= args.interval
            if not (due or state["capture"]):
                continue
            state["capture"] = False
            last = time.monotonic()
            result = analyse_tray(args.node_id, state["batch_id"], args.quality, args.detailed)
            publish_json(client, contract.vision_result(args.node_id), result, qos=1)
            print(f"[{args.node_id}] tray {result['image_id']}: {result['bean_count']} beans, "
                  f"defect {result['defect_rate_pct']}% {result['class_counts']}")
    except KeyboardInterrupt:
        publish_json(client, status_topic, {"v": 1, "node_id": args.node_id, "state": "offline", "ts": time.time()}, qos=1, retain=True).wait_for_publish(2)
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
