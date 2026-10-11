"""Watch all topgun/# traffic and check every message against the contract.

    python -m tools.monitor            # one line per message
    python -m tools.monitor --raw      # also print full payloads
"""
import argparse
import json
from datetime import datetime

from topgun import contract
from topgun.mqtt import BROKER_HOST, BROKER_PORT, make_client


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", default="topgun/#")
    ap.add_argument("--raw", action="store_true")
    args = ap.parse_args()

    client = make_client("monitor")

    def on_connect(c, userdata, flags, reason_code, properties):
        print(f"monitor connected to {BROKER_HOST}:{BROKER_PORT}, subscribed {args.topic}")
        c.subscribe(args.topic, qos=1)

    def on_message(c, userdata, msg):
        now = datetime.now().strftime("%H:%M:%S")
        kind = contract.schema_for_topic(msg.topic)
        try:
            payload = json.loads(msg.payload)
            errors = contract.validate(kind, payload) if kind else ["no schema for this topic"]
        except json.JSONDecodeError as e:
            payload, errors = msg.payload[:80], [f"not JSON: {e}"]
        mark = "OK " if not errors else "BAD"
        retained = " (retained)" if msg.retain else ""
        print(f"{now} {mark} {msg.topic}{retained} [{kind}]")
        for err in errors:
            print(f"         - {err}")
        if args.raw:
            print("         " + json.dumps(payload, ensure_ascii=False)[:2000])

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect_async(BROKER_HOST, BROKER_PORT)  # retries until the broker is up
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
