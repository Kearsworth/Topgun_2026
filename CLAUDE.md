# TESA Top Gun Rally #20 — Chumphon Robusta AIoT Platform

Competition 15–21 Nov 2026 at KMITL Chumphon. Team of 5 from one university; pre-written code is allowed.
Brief: the `*.jpg` files in this folder (local only, gitignored — ask the team lead) (poster, pain points, tech gaps, system diagram, equipment rules).
Everything here is a provisional PoC — designs may change; keep pieces small and swappable.
No purchases (use existing gear only; no real coffee beans before the event → vision trains on public datasets). GitHub is public for teammates to read; no collaborators yet.
No contact with organizers before the event: unknowns are handled as assumptions + fallbacks in research/00-MASTER-PLAN.md §6, confirmed on day 1.

## User
- Answer in Thai; keep technical terms/code in English.

## Architecture
Green beans → ESP32 sensing node (sensors given by organizers on the day) + Raspberry Pi 5 vision node
→ MQTT (Mosquitto) → service layer → "Next-Gen Market" (buyer/supplier). Laptop runs a local SLM (~1.5B, Ollama).

Hard constraints:
- Pi 5: **no AI HAT / accelerator** — vision runs on CPU (OpenCV + tiny classifier, NCNN/ONNX).
- Vision capture: never a black background (black beans vanish) — backlight + top-light, or matte blue. Don't use the IMX500 AI Camera (on-board NPU likely violates the no-accelerator rule). Details: research/02.
- Must work **offline** on a team LAN.
- ESP32 needs WiFi + digital I/O + ADC + PWM; Arduino-ESP32 core 3.x API (`ledcAttach`/`ledcWrite(pin, …)`).
  Main board: **ESP32-S3 N16R8** (16MB flash, 8MB octal PSRAM). Analog only on ADC1 = GPIO1–10 (ADC2 clashes with WiFi).
  Don't use GPIO35–37 (octal PSRAM), 26–32 (flash), 19/20 (USB), strapping 0/3/45/46. Arduino: "ESP32S3 Dev Module", Flash 16MB, PSRAM "OPI PSRAM".
  Backup board: classic ESP32 DevKit (ADC1 = GPIO32–39).
- Moisture target for green beans: ICO export ≤12.5% (we use ~10–12.5%; confirm against research/05).

## Contract (the seam between components)
`contracts/CONTRACT.md` — topics, payloads, QoS. Schemas in `contracts/schemas/`, topic builders + `validate()` in `topgun/contract.py`. New sensor = new key in `readings`, no schema change.

## Layout
- `topgun/` shared Python: `contract.py`, `mqtt.py` (paho-mqtt v2 helpers)
- `sim/` simulated ESP32 (`sim_esp32.py`, drying model + fan closed loop + LWT crash test) and Pi (`sim_vision.py`)
- `tools/monitor.py` — validates all `topgun/#` traffic live
- `infra/mosquitto.conf` — ports 1883 (MQTT) + 9001 (websockets), anonymous
- `tests/` — pytest for contract + simulators
- `research/` — start with `00-MASTER-PLAN.md` (weekly plan, roles, decision log); Thai research reports 01–06 (datasets, vision, ESP32, competition intel, coffee domain, service+SLM). Read the relevant one before designing a component.
- Planned: `firmware/` (ESP32), `vision/` (Pi), `service/` (FastAPI+SQLite), `dashboard/`

## Commands
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -q
mosquitto -c infra/mosquitto.conf -v
.venv/bin/python -m tools.monitor
.venv/bin/python -m sim.sim_esp32 --scenario rainy|sunny|mixed|faulty [--crash-after 10]
.venv/bin/python -m sim.sim_vision --quality good|average|poor
```
Use `127.0.0.1` rather than `localhost` if a client fails to connect (macOS resolves IPv6 first; broker listens IPv4).
