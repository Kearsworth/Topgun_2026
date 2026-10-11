import json
from datetime import datetime
from pathlib import Path

import pytest

from sim.sim_esp32 import DryingPile, moisture_reading
from sim.sim_vision import QUALITY, analyse_tray
from topgun import contract

EXAMPLES = Path(__file__).resolve().parent.parent / "contracts" / "examples"


@pytest.mark.parametrize("path", sorted(EXAMPLES.glob("*.json")), ids=lambda p: p.name)
def test_examples_are_valid(path):
    schema = path.name.split(".")[0]
    assert contract.validate(schema, json.loads(path.read_text())) == []


@pytest.mark.parametrize("topic,expected", [
    ("topgun/team01/esp32/esp32-01/data", "esp32_data"),
    ("topgun/team01/vision/pi5-01/result", "vision_result"),
    ("topgun/team01/esp32/esp32-01/status", "node_status"),
    ("topgun/team01/vision/pi5-01/cmd", "command"),
    ("topgun/team01/service/alerts", "alert"),
    ("topgun/team01/esp32/esp32-01/unknown", None),
])
def test_topic_routing(topic, expected):
    assert contract.schema_for_topic(topic) == expected


def test_invalid_payload_reports_errors():
    errors = contract.validate("esp32_data", {"v": 1, "node_id": "x", "readings": {"air_rh_pct": 150}})
    assert errors and "air_rh_pct" in errors[0]


def test_simulated_esp32_payload_is_valid():
    pile = DryingPile(10, 0.5, rain_prob=0.3)
    readings = pile.step(datetime(2026, 11, 15, 12), 1.0, fan_pct=50)
    readings["bean_moisture_pct"], adc = moisture_reading(pile.moisture * 100)
    payload = {"v": 1, "node_id": "t", "ts": 0, "seq": 0, "readings": readings, "raw": {"adc_moisture": adc}}
    assert contract.validate("esp32_data", payload) == []


def test_drying_reaches_target_in_sunny_weather():
    pile = DryingPile(10, 0.5, rain_prob=0.0)
    for h in range(24 * 14):
        pile.step(datetime(2026, 11, 15 + h // 24 % 10, h % 24), 1.0, fan_pct=0)
    assert pile.moisture < 0.13


@pytest.mark.parametrize("quality", QUALITY)
def test_simulated_vision_payload_is_valid(quality):
    result = analyse_tray("pi5-test", "CRB-T", quality, detailed=True)
    assert contract.validate("vision_result", result) == []
    assert sum(result["class_counts"].values()) == result["bean_count"]
