"""Single source of truth for MQTT topics and payload validation.

Topic layout and schemas are provisional (see contracts/CONTRACT.md); change
them here and in contracts/schemas/ only, so every component follows.
"""
import json
import os
import re
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator

CONTRACT_VERSION = 1
TEAM = os.environ.get("TOPGUN_TEAM", "team01")
ROOT = f"topgun/{TEAM}"
SCHEMA_DIR = Path(__file__).resolve().parent.parent / "contracts" / "schemas"


def esp32_data(node_id: str) -> str:
    return f"{ROOT}/esp32/{node_id}/data"


def vision_result(node_id: str) -> str:
    return f"{ROOT}/vision/{node_id}/result"


def status(kind: str, node_id: str) -> str:
    return f"{ROOT}/{kind}/{node_id}/status"


def cmd(kind: str, node_id: str) -> str:
    return f"{ROOT}/{kind}/{node_id}/cmd"


ALERTS = f"{ROOT}/service/alerts"

_TOPIC_SCHEMAS = [
    (re.compile(r"^topgun/[^/]+/esp32/[^/]+/data$"), "esp32_data"),
    (re.compile(r"^topgun/[^/]+/vision/[^/]+/result$"), "vision_result"),
    (re.compile(r"^topgun/[^/]+/(esp32|vision)/[^/]+/status$"), "node_status"),
    (re.compile(r"^topgun/[^/]+/(esp32|vision)/[^/]+/cmd$"), "command"),
    (re.compile(r"^topgun/[^/]+/service/alerts$"), "alert"),
]


def schema_for_topic(topic: str) -> str | None:
    for pattern, name in _TOPIC_SCHEMAS:
        if pattern.match(topic):
            return name
    return None


@lru_cache(maxsize=None)
def _validator(name: str) -> Draft202012Validator:
    schema = json.loads((SCHEMA_DIR / f"{name}.schema.json").read_text())
    return Draft202012Validator(schema)


def validate(name: str, payload: dict) -> list[str]:
    """Return a list of human-readable errors (empty = valid)."""
    errors = sorted(_validator(name).iter_errors(payload), key=lambda e: list(e.path))
    return [f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors]
