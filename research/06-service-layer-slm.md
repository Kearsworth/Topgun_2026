# 06 — Service Layer + SLM: คู่มือออกแบบและสร้าง (Chumphon Robusta AIoT Platform)

> เอกสารวิจัยสำหรับทีม TESA Top Gun Rally #20 (15–21 พ.ย. 2026, สจล. ชุมพร)
> ค้นคว้า ณ วันที่ 10 ต.ค. 2026 · โค้ดทั้งหมดในเอกสารนี้ **ยังไม่ได้ทดสอบ (UNTESTED)** ต้องรันทดสอบบนเครื่องจริงก่อนวันแข่ง
> ส่วนที่เป็น "ตัวเลขประมาณ" หรือ "ยังไม่ยืนยัน" จะมีป้ายกำกับไว้ชัดเจน

---

## 0. Executive Summary (สรุปสำหรับผู้บริหารทีม)

**เป้าหมาย:** ระบบต้องรันได้ 100% แบบออฟไลน์บนแล็ปท็อปเครื่องเดียว + Wi-Fi router ของทีมเอง ทำเดโมเต็มรูปแบบ (sensor สด → AI vision → เกรด → passport/QR → ราคา → จับคู่ผู้ซื้อ → PDF certificate → SLM อธิบายเป็นภาษาไทย) ภายในเวลาสร้างจำกัด

**หลักการออกแบบ 3 ข้อ**
1. **"Code computes, SLM narrates"** — ตัวเลขทุกตัว (เกรด, ราคา, % match, ค่าผิดปกติ) คำนวณด้วย Python ที่อธิบายได้ แล้วส่งเป็น JSON ให้ SLM *เขียนบรรยาย* เท่านั้น SLM ไม่เคยคิดตัวเลขเอง → ลด hallucination และตอบกรรมการได้ทุกคำถาม "ตัวเลขนี้มาจากไหน"
2. **Broker เดียว ฐานข้อมูลไฟล์เดียว process น้อยที่สุด** — Mosquitto + FastAPI + SQLite + Ollama ไม่มี Docker บังคับ (Docker เป็นทางเลือกสำรอง)
3. **Fail-soft** — ถ้า SLM ช้า/ล่ม ทุกฟีเจอร์ยังทำงานได้ (มีข้อความ template สำรอง) ถ้า sensor หลุด dashboard แสดงสถานะ offline จาก LWT

### Recommended Default Stack (ค่าเริ่มต้นที่แนะนำ)

| ชั้น | เลือกใช้ | เหตุผลสั้น ๆ |
|---|---|---|
| Broker | **Mosquitto 2.x บนแล็ปท็อป** (listener 1883 MQTT + 9001 WebSockets), `allow_anonymous true` บน LAN ปิด | มาตรฐาน, เบา, browser ต่อได้ตรงผ่าน WS |
| Ingest | **paho-mqtt 2.x** (`CallbackAPIVersion.VERSION2`) thread ภายใน FastAPI lifespan | ควบคุมได้, ไม่พึ่ง lib wrapper |
| Backend | **FastAPI + SQLModel + SQLite (WAL mode)** | ไฟล์เดียว, backup ง่าย, เร็วพอสำหรับ <100 msg/s |
| Time-series DB | **ไม่ใช้** (SQLite + index พอ) | InfluxDB/Timescale เพิ่มความเสี่ยงโดยไม่จำเป็นในสเกลเดโม |
| Frontend หลัก (operator/judge) | **Streamlit** (`st.fragment(run_every=2)`) — ทางเลือกที่ 2: NiceGUI | สร้างเร็วที่สุดด้วย Python ล้วน, ทีม 5 คนแบ่งหน้าได้ |
| Live wow-screen (option) | **HTML+JS หน้าเดียว + mqtt.js over WS** | กราฟขยับแบบ real-time จริง ไม่กระพริบ |
| Public passport (สแกน QR) | **FastAPI + Jinja2 HTML** (`/p/{batch_code}`) | เปิดบนมือถือกรรมการได้ทันทีผ่าน Wi-Fi ทีม |
| QR | `qrcode[pil]` | ง่าย |
| PDF | **WeasyPrint (HTML→PDF) + ฟอนต์ Sarabun ฝังไฟล์** — สำรอง: ReportLab 4.4+ พร้อม `shaping` extra | WeasyPrint ใช้ Pango จัดภาษาไทยได้ดี; บน Windows ต้องติดตั้ง Pango (MSYS2) |
| SLM | **Ollama + `qwen2.5:1.5b`** (ตาม organizer) + `format=<JSON schema>`, `temperature=0`, `keep_alive=-1`, `num_ctx=4096` | ภาษาไทยดีที่สุดในกลุ่ม ~1.5B, รองรับ tools |
| SLM สำรอง/เทียบ | `scb10x/llama3.2-typhoon2-1b-instruct` (808MB), `qwen3:1.7b` (think=false), ถ้าไม่ถูกบังคับขนาด: `scb10x/typhoon2.5-qwen3-4b` (2.5GB) | ดูหัวข้อ 5.4 |
| Embedding (RAG เล็ก) | `bge-m3` (multilingual, ~1.2GB) หรือไม่ใช้ embedding เลย (keyword/BM25 บน FAQ ~30 ข้อ) | ข้อมูลน้อย → BM25 ก็พอ |
| Network | Router ของทีม, static/DHCP-reservation IP, laptop = NTP server (chrony/w32time) | ไม่พึ่ง Wi-Fi สถานที่ |

**ความเสี่ยงอันดับต้น**
1. WeasyPrint บน Windows (ต้องมี Pango) → ทดสอบตั้งแต่สัปดาห์แรก หรือใช้ WeasyPrint standalone `.exe` / ReportLab สำรอง
2. SLM 1.5B ภาษาไทยเพี้ยน/หลุด schema → ใช้ structured output + validate + retry 1 ครั้ง + fallback template
3. ไม่มีอินเทอร์เน็ต → ทำ "offline dress rehearsal" ถอดสาย LAN/ปิด Wi-Fi ภายนอก แล้วรันระบบทั้งหมดก่อนเดินทาง
4. กรรมการอาจกำหนดโมเดลเฉพาะ → ออกแบบ `MODEL_NAME` เป็น env var เปลี่ยนได้ใน 1 บรรทัด (ยังไม่พบประกาศทางการของ TGR#20 ทางออนไลน์ — ดู 5.5)

---

## 1. สถาปัตยกรรมภาพรวม

```
 [ESP32 sensing node] --MQTT 1883--\
                                     >-- [Mosquitto @ laptop 192.168.50.10] --WS 9001--> [Browser live page (mqtt.js)]
 [Raspberry Pi 5 vision] --MQTT----/            |
                                                | paho subscriber (thread)
                                                v
                                   [FastAPI service :8000] <--> [SQLite topgun.db (WAL)]
                                     |  grading / pricing / matching (pure Python)
                                     |  QR, passport page /p/{code}, PDF /reports/{id}.pdf
                                     |  /api/llm/*  --> [Ollama :11434  qwen2.5:1.5b]
                                     v
                         [Streamlit :8501 dashboard]  (อ่านผ่าน REST ของ FastAPI)
                         [มือถือกรรมการ สแกน QR → http://192.168.50.10:8000/p/CPN-2026-001]
```

ทุกอย่างรันบนแล็ปท็อปเครื่องเดียว Pi 5 ทำเฉพาะ vision inference แล้ว publish ผลเป็น JSON (ไม่ส่งรูปเต็มผ่าน MQTT — ส่งเป็น HTTP upload หรือ thumbnail เล็ก base64 ถ้าจำเป็น)

---

## 2. MQTT Broker

### 2.1 Mosquitto เวอร์ชันและสิ่งที่เปลี่ยน

- **2.0+**: ถ้าไม่ประกาศ `listener` เลย broker จะรับเฉพาะ localhost; ถ้ามี listener ต้องตั้ง `allow_anonymous` เอง (default = `false`) — นี่คือสาเหตุอันดับ 1 ที่ "ESP32 ต่อไม่ติด" [mosquitto.conf man](https://mosquitto.org/man/mosquitto-conf-5.html)
- **2.1 (ม.ค. 2026)**: มี WebSockets แบบ built-in (ไม่พึ่ง libwebsockets อีกต่อไป เร็วขึ้นมาก), client tools (`mosquitto_pub/sub`) รองรับ websockets, เพิ่ม listener ชนิด `http_api` (experimental — ไม่แนะนำใช้ในงานแข่ง), ล่าสุด 2.1.2 เป็น bugfix [release 2.1.0](https://mosquitto.org/blog/2026/01/version-2-1-0-released/), [Eclipse 2.1 review](https://projects.eclipse.org/projects/iot.mosquitto/releases/2.1/review)
- บน **Windows installer** และ **Raspberry Pi OS** (apt) WebSockets ใช้งานได้ทั้ง 2.0.x และ 2.1.x (config เหมือนกัน)

### 2.2 `mosquitto.conf` แนะนำ (UNTESTED)

```conf
# ===== mosquitto.conf — TGR#20 (LAN ปิด ไม่มีอินเทอร์เน็ต) =====
per_listener_settings false
allow_anonymous true          # LAN ปิดของทีมเท่านั้น! ถ้ากรรมการให้ทำ security ค่อยเปิด password_file

# MQTT ปกติสำหรับ ESP32 / Pi / Python
listener 1883 0.0.0.0
protocol mqtt

# WebSockets สำหรับหน้าเว็บ (mqtt.js) — ws://192.168.50.10:9001
listener 9001 0.0.0.0
protocol websockets

# Persistence: เก็บ retained + QoS1 queue ข้าม restart
persistence true
persistence_location C:/topgun/mosquitto/data/     # Linux: /var/lib/mosquitto/
autosave_interval 60          # default 1800s — ลดให้เซฟถี่ขึ้น
max_queued_messages 1000      # default 1000 (ต่อ client)

# Log
log_dest file C:/topgun/mosquitto/mosquitto.log    # Linux: /var/log/mosquitto/mosquitto.log
log_dest stdout
log_type error
log_type warning
log_type notice
connection_messages true
sys_interval 10               # $SYS/# ใช้โชว์ "broker health" บน dashboard ได้
```

ทดสอบ: `mosquitto -c mosquitto.conf -v` แล้ว `mosquitto_sub -h 192.168.50.10 -t "tgr/#" -v`
**Windows:** ต้องเปิด Windows Firewall inbound TCP 1883, 9001, 8000, 8501, 11434(ถ้าจำเป็น) — และตั้ง network profile เป็น *Private*

### 2.3 Broker บนแล็ปท็อป vs บน Pi 5

| | Laptop (แนะนำ) | Raspberry Pi 5 |
|---|---|---|
| ข้อดี | ทุก service อยู่เครื่องเดียว debug ง่าย; latency ต่ำสุดถึง DB | Pi เปิดตลอด ไม่โดนปิดฝาพับ/Windows update/sleep |
| ข้อเสีย | Windows sleep/firewall/update; ต้องตั้ง power plan "never sleep" | ถ้า Pi ร้อน/vision กิน CPU, broker ได้รับผล; อีกจุดที่ต้อง ssh |
| สรุป | ใช้ laptop เป็นหลัก **และติดตั้ง Mosquitto บน Pi ไว้เป็นสำรอง** (config เดียวกัน) — ESP32 เก็บ broker IP 2 ตัวใน firmware สลับได้ |

### 2.4 Topic design

ใช้ prefix คงที่ + ระดับ site/device แบบ hierarchical ห้ามใส่ข้อมูลใน topic ที่เปลี่ยนทุกครั้ง (เช่น timestamp)

```
tgr/v1/{site}/{device_id}/status            # "online"/"offline"  retained=true, QoS1 (LWT)
tgr/v1/{site}/{device_id}/telemetry         # sensor JSON         retained=false, QoS0 (ทุก 2–5 วิ)
tgr/v1/{site}/{device_id}/telemetry/last    # (optional) ค่าล่าสุด retained=true ให้หน้าเว็บเปิดมาเห็นทันที
tgr/v1/{site}/{device_id}/vision            # ผล AI vision        retained=false, QoS1
tgr/v1/{site}/{device_id}/cmd               # คำสั่งจาก server → device (เช่น capture) QoS1
tgr/v1/{site}/{device_id}/cmd/ack           # device ตอบรับคำสั่ง
tgr/v1/svc/batch/{batch_code}/event         # service publish เหตุการณ์ (grade_done, price_updated) ให้หน้า live
tgr/v1/svc/alert                            # anomaly alert      QoS1
```

ตัวอย่าง `site = dryyard1`, `device_id = esp32-01`, `pi5-cam-01`

**Payload (JSON, ต้องมี schema version + batch + seq)**

```json
// telemetry จาก ESP32
{"v":1,"dev":"esp32-01","batch":"CPN-2026-001","seq":1532,
 "ts":1763190000,           // epoch วินาที (อาจ 0 ถ้ายังไม่ sync เวลา → server ใช้เวลาตัวเอง)
 "bean_moist_pct":14.8,"air_temp_c":31.2,"air_rh_pct":72.5,"bean_temp_c":38.1,"lux":52000}

// vision จาก Pi 5
{"v":1,"dev":"pi5-cam-01","batch":"CPN-2026-001","seq":88,"ts":1763190012,
 "model":"yolov8n-defect-v3","n_beans":412,
 "defects":{"black":3,"broken":11,"insect":2,"sour":1,"foreign":0},
 "size_dist":{"s18":0.31,"s16":0.44,"s14":0.19,"lt14":0.06},
 "color_uniformity":0.87,"image_id":"img_000088.jpg"}
```

### 2.5 QoS / Retained / LWT — กฎที่ใช้

- **Telemetry → QoS 0** (ข้อมูลถี่ หายบ้างไม่เป็นไร ประหยัด ESP32)
- **Vision result, cmd, alert → QoS 1** (ต้องถึง; ฝั่ง ingest ต้อง *idempotent* โดยใช้ `(dev, seq)` เป็น unique key เพราะ QoS1 อาจซ้ำ)
- **QoS 2 ไม่จำเป็น** (ช้าและซับซ้อนกว่า)
- **Retained** เฉพาะ `status` และ `.../last` — ห้าม retain telemetry stream
- **LWT**: ทุก device ตั้ง will = `tgr/v1/{site}/{dev}/status` payload `offline`, retain=true, QoS1 แล้วเมื่อเชื่อมต่อสำเร็จ publish `online` retain=true → dashboard แสดงจุดเขียว/แดงได้ทันที
- **keepalive** 15–30 วินาที (LWT จะยิงหลัง ~1.5×keepalive เมื่อ device หายเงียบ)
- client_id ต้อง **unique** ทุกตัว (ซ้ำ = เตะกันหลุดวนลูป — บั๊กคลาสสิก)

### 2.6 paho-mqtt 2.x — การเปลี่ยนแปลงที่ต้องรู้

ตั้งแต่ 2.0 ต้องระบุ `CallbackAPIVersion` ตอนสร้าง client (VERSION1 deprecated แต่ยังใช้ได้) และ signature callback เปลี่ยน [paho migration guide](https://eclipse.dev/paho/files/paho.mqtt.python/html/migrations.html):

| callback | VERSION2 signature |
|---|---|
| `on_connect` | `(client, userdata, flags, reason_code, properties)` — `flags.session_present`, `reason_code` เป็นอ็อบเจกต์ `ReasonCode` (ใช้ `reason_code.is_failure` หรือ `== 0`) |
| `on_disconnect` | `(client, userdata, flags, reason_code, properties)` |
| `on_subscribe` | `(client, userdata, mid, reason_codes, properties)` — `reason_codes` เป็น list |
| `on_publish` | `(client, userdata, mid, reason_code, properties)` |
| `on_message` | `(client, userdata, message)` (ไม่เปลี่ยน) |

โค้ดตัวอย่างอยู่ในหัวข้อ 7.3 (ไฟล์ `ingest.py`)

### 2.7 ทางเลือก aMQTT / อื่น ๆ

- **aMQTT** (Python asyncio broker+client, MQTT 3.1.1, QoS0–2, TCP+WebSocket listener, plugin auth) — ยังพัฒนาต่อเนื่อง ล่าสุด 0.12.x (ก.ย. 2026) [amqtt docs](https://amqtt.readthedocs.io/), [piwheels](https://www.piwheels.org/project/amqtt) — ข้อดี: `pip install` ได้ ไม่ต้องลง Mosquitto; ข้อเสีย: performance/ความนิ่งต่ำกว่า, ไม่มี MQTT5 → **ใช้เป็นแผนสำรองฉุกเฉินเท่านั้น** (เช่น Windows ลง Mosquitto ไม่ได้)
- **fastapi-mqtt** (ห่อ gmqtt, รองรับ MQTT5, มี decorator `@fast_mqtt.subscribe("topic/#", qos=1)` + lifespan `mqtt_startup()/mqtt_shutdown()`) [GitHub](https://github.com/sabuhish/fastapi-mqtt) — สะดวกแต่เพิ่ม dependency (gmqtt) และไม่ชัดว่าดูแลต่อเนื่องแค่ไหน → **แนะนำ paho thread** ซึ่งเป็น lib หลักที่ทุกคนในทีมเจอใน tutorial
- **aiomqtt** (async wrapper ของ paho) — ทางเลือกที่ดีถ้าทีมถนัด asyncio
- **EMQX / NanoMQ** — เกินความจำเป็น

---

## 3. Backend: FastAPI + SQLite

### 3.1 ทำไม SQLite (ไม่ใช่ InfluxDB/Timescale)

ปริมาณข้อมูลจริง: สมมติ 3 device × 1 msg/2 วิ × 7 วัน ≈ 900k แถว — SQLite รับสบายเมื่อมี index `(batch_id, ts)` และเปิด **WAL mode** (อ่านพร้อมเขียนได้)
- **InfluxDB/TimescaleDB**: ได้ downsampling/retention และ Grafana สวย แต่ต้องรัน service เพิ่ม (Timescale = PostgreSQL), เรียนรู้ query ใหม่, เสี่ยงพังวันแข่ง → **ไม่คุ้มสำหรับเดโม**
- ถ้าอยากได้กราฟแบบ Grafana: Grafana อ่าน SQLite ได้ผ่าน plugin `frser-sqlite-datasource` (ต้องดาวน์โหลด plugin ล่วงหน้า) — ทางเลือก ไม่ใช่ค่าเริ่มต้น
- Downsample ใน SQL ง่าย ๆ: `GROUP BY ts/60` ได้ค่าเฉลี่ยรายนาที

### 3.2 Schema (SQLModel) — ตารางหลัก

| ตาราง | คอลัมน์สำคัญ | หมายเหตุ |
|---|---|---|
| `farm` | id, name, district, lat, lon, gap_certified(bool), owner_name | ข้อมูล passport |
| `batch` | id, code (unique, เช่น `CPN-2026-001`), farm_id, variety, process (`natural/washed/honey/wet-hulled`), harvest_date, weight_kg, target_moisture_pct (ค่าเริ่ม 12.5 — **ต้องยืนยันกับมาตรฐาน มกษ./ข้อกำหนดผู้ซื้อ**), status (`drying/sorting/graded/listed/sold`), created_at | หัวใจของ traceability |
| `sensor_reading` | id, batch_id, device_id, seq, ts, bean_moist_pct, air_temp_c, air_rh_pct, bean_temp_c, lux; UNIQUE(device_id, seq) | time-series |
| `vision_result` | id, batch_id, device_id, seq, ts, n_beans, defects_json, size_dist_json, color_uniformity, defect_rate, image_path | |
| `grade` | id, batch_id, ts, moisture_pct, defect_rate, screen_ge16_pct, score (0–100), grade (`A/B/C/Reject`), breakdown_json, rule_version | เก็บ breakdown เพื่ออธิบาย |
| `price_quote` | id, batch_id, ts, base_price_thb_kg, adjustments_json, final_price_thb_kg, rule_version | dynamic pricing ทุกครั้งเก็บประวัติ |
| `buyer` | id, name, type (`roaster/exporter/cafe`), contact | |
| `buyer_request` | id, buyer_id, min_grade, max_moisture_pct, max_defect_rate, min_screen16_pct, qty_kg, max_price_thb_kg, preferred_process, deadline, weights_json | ความต้องการผู้ซื้อ |
| `match` | id, request_id, batch_id, score_pct, feasible(bool), breakdown_json, explanation_th, status (`proposed/accepted/rejected`) | % match |
| `event` | id, batch_id, ts, type (`harvest/drying_start/moisture_reached/graded/certified/sold`), data_json, prev_hash, hash | ledger แบบ hash-chain (ทำ "tamper-evident passport" ได้ภายใน 20 บรรทัด — ปังสำหรับกรรมการ) |
| `report` | id, batch_id, ts, pdf_path, llm_model, llm_text | |

### 3.3 MQTT ingest ในพื้นหลัง — 2 ทางเลือก

1. **(แนะนำ) paho `loop_start()` thread ภายใน FastAPI lifespan** — callback เขียน DB ผ่าน session ใหม่ทุกครั้ง (SQLite + `check_same_thread=False`), ใช้ batch insert ทุก 1 วิ ถ้าข้อมูลถี่
2. **แยก process `ingest.py`** — รันเป็นโปรแกรมแยก เขียน SQLite เดียวกัน (WAL) → ข้อดี: API restart ไม่ทำ ingest หลุด; ข้อเสีย: 1 process เพิ่ม
   ทีมเลือกได้ — โค้ดใน 7.3 เขียนให้ใช้ได้ทั้งสองแบบ

### 3.4 Docker vs venv (ความน่าเชื่อถือแบบออฟไลน์)

| | plain venv + wheels (แนะนำ) | Docker Compose |
|---|---|---|
| Windows + GTX1650 | Ollama native ใช้ GPU ทันที | Docker Desktop + WSL2 + NVIDIA toolkit → จุดพังเพิ่ม, Docker Desktop บางเวอร์ชันพยายามเช็ค login/update |
| ออฟไลน์ | `pip install --no-index --find-links wheels/` | ต้อง `docker save` image ไว้ล่วงหน้า (หลาย GB) |
| debug หน้างาน | ง่าย | ยากกว่า |
| สรุป | **ใช้ venv** + สคริปต์ `start_all.bat` / `start_all.sh` เปิดทุก service | ใช้เฉพาะถ้าแล็ปท็อปเป็น Linux และทีมถนัด |

---

## 4. Frontend

### 4.1 เปรียบเทียบ (สำหรับ "สร้างเร็ว + กรรมการว้าว")

| ตัวเลือก | ความเร็วสร้าง | Real-time | ความสวย/ปรับแต่ง | ภาษา | ข้อควรระวัง |
|---|---|---|---|---|---|
| **Streamlit** | ★★★★★ | polling ด้วย `@st.fragment(run_every=2)` (rerun เฉพาะส่วน) [docs](https://docs.streamlit.io/develop/api-reference/execution-flow/st.fragment) | ★★★ (ดูเป็น "Streamlit") | Python | rerun model; ไม่เหมาะ push ทุก 100ms |
| **NiceGUI** | ★★★★ | push จริงผ่าน websocket, `ui.timer`, ECharts ในตัว | ★★★★ (Quasar/Tailwind) | Python | เอกสารน้อยกว่า Streamlit |
| **Node-RED + Dashboard 2.0** (`@flowfuse/node-red-dashboard`) | ★★★★ สำหรับ IoT ล้วน | MQTT node ในตัว | ★★★ | flow/JS | logic ซับซ้อน (matching/PDF/LLM) เขียนใน flow ยาก; Dashboard 1 deprecated แล้ว [FlowFuse](https://flowfuse.com/blog/2024/01/dashboard-2-ga/) |
| **Grafana** | ★★★ (เฉพาะกราฟ) | ดี | ★★★★★ สำหรับกราฟ | config | ไม่เหมาะกับฟอร์ม buyer/market; plugin ต้องโหลดล่วงหน้า |
| **HTML + JS (mqtt.js over WS)** | ★★ | ★★★★★ (ตรงจาก broker) | ★★★★★ | JS | ต้องเขียนเอง; ต้องเก็บ JS lib ไว้ local (ไม่ใช้ CDN!) |

**คำแนะนำ:**
- **Operator/Market dashboard = Streamlit** (หลายหน้า: Live Sensors, Vision, Batch & Grade, Market & Matching, Passport/Reports, AI Assistant) — ทีม 5 คนแบ่งกันทำคนละไฟล์ใน `pages/`
- **"Big screen" สำหรับพิธีเปิด/บูธ = หน้า HTML เดียว** เสิร์ฟจาก FastAPI static ใช้ `mqtt.min.js` + Chart.js (ไฟล์ local) subscribe `tgr/v1/+/+/telemetry` ผ่าน `ws://<laptop>:9001` → กราฟวิ่งสด, จุด online/offline จาก LWT
- ถ้าทีมไม่มีใครถนัด JS → ใช้ NiceGUI แทนทั้งสองอย่าง

### 4.2 QR + Public Passport page

- QR ชี้ไป `http://192.168.50.10:8000/p/CPN-2026-001` (IP ของแล็ปท็อปบน Wi-Fi ทีม) — มือถือกรรมการต้องต่อ Wi-Fi ทีม (ทำป้าย "ต่อ Wi-Fi: TGR-Robusta / pass xxxx" + QR Wi-Fi แบบ `WIFI:T:WPA;S:TGR-Robusta;P:xxxx;;` คู่กัน)
- ใช้ hostname สั้นถ้า router รองรับ local DNS (เช่น `http://robusta.lan/p/...`) — สวยกว่าแต่ทดสอบให้แน่ใจ
- หน้า passport: ฟาร์ม, แผนที่ (รูป static ไม่ใช่ online tiles!), timeline event, กราฟความชื้นลดลงถึง target, เกรด + breakdown, ราคาแนะนำ, hash chain "Verified ✓", ปุ่มดาวน์โหลด PDF certificate
- โค้ด QR:

```python
import qrcode
img = qrcode.make(f"{PUBLIC_BASE}/p/{batch.code}", box_size=8, border=2)
img.save(f"static/qr/{batch.code}.png")
```

### 4.3 PDF + ฟอนต์ไทย (Sarabun) — ข้อควรระวัง

**WeasyPrint (แนะนำ: เขียน HTML/CSS แล้วแปลงเป็น PDF ใช้ template เดียวกับหน้า passport)**
- ใช้ Pango ในการจัดข้อความ → สระลอย/วรรณยุกต์ไทยวางถูก และตัดคำไทยผ่าน library ระดับ Pango (libthai/ICU — ตัดคำได้แต่ไม่สมบูรณ์ 100%) [W3C Thai line-breaking](https://www.w3.org/International/tutorials/css3-text/en/slides/Slide0090.html)
- เวอร์ชันปัจจุบัน 70.0; **บน Windows ต้องติดตั้ง MSYS2 แล้ว `pacman -S mingw-w64-ucrt-x86_64-pango`** หรือใช้ standalone executable จาก GitHub releases (antivirus บางตัวแจ้งเตือนผิด) [WeasyPrint first steps](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html)
- **ฝังฟอนต์ด้วย `@font-face` ชี้ไฟล์ local** (`Sarabun-Regular.ttf`, `Sarabun-Bold.ttf` จาก Google Fonts — ดาวน์โหลดเก็บใน repo, license OFL) ห้ามใช้ `<link>` Google Fonts เพราะออฟไลน์
- ตั้ง `base_url` ให้ WeasyPrint หารูป/ฟอนต์เจอ: `HTML(string=html, base_url=str(BASE_DIR)).write_pdf(path)`
- ตัวเลขยาว/ข้อความไทยไม่มีช่องว่างยาวมาก ๆ อาจล้นช่องตาราง → ใส่ `word-break: break-word; overflow-wrap: anywhere;`
- PDF ใหญ่ถ้าฝังฟอนต์ทั้งไฟล์ — WeasyPrint subset ให้อัตโนมัติ (ปกติ)

**ReportLab (สำรอง)**
- ReportLab รุ่นเก่า **ไม่ shape ภาษาไทย** → สระบน/วรรณยุกต์ซ้อนทับหรือลอยผิดตำแหน่ง (ปัญหาคลาสสิก)
- ReportLab **4.4+** มี shaping ด้วย HarfBuzz แบบ *experimental* (`pip install "reportlab[shaping]"` → uharfbuzz) และทีมผู้พัฒนาระบุว่าเพิ่มรองรับอักษรไทยแล้ว แต่ "ยังต้องปรับปรุง" [whats-new-4.4](https://docs.reportlab.com/releases/notes/whats-new-44/), [rl-arabic](https://docs.reportlab.com/rl-arabic), [Review of 2025](https://reportlab.substack.com/p/review-of-2025)
- ReportLab ไม่ตัดคำไทยเอง → ต้องตัดคำด้วย `pythainlp.word_tokenize` แล้วแทรก zero-width space (`\u200b`) ก่อนใส่ `Paragraph`
- สรุป: **WeasyPrint ถ้าลง Pango สำเร็จ; ไม่สำเร็จใช้ ReportLab+shaping+pythainlp; ทางสุดท้าย = เปิดหน้า HTML แล้ว "Print to PDF" จาก browser** (Chrome/Edge ใช้ HarfBuzz จัดไทยสมบูรณ์ — แผน C ที่ไม่มีวันพัง)

---

## 5. SLM (Ollama)

### 5.1 การตั้งค่าที่ยืนยันจากเอกสารทางการ

ข้อมูลจาก [Ollama FAQ](https://docs.ollama.com/faq):
- **num_ctx default = 4096** — ตั้งทั้ง server ด้วย `OLLAMA_CONTEXT_LENGTH=4096` หรือส่งต่อคำขอใน `options={"num_ctx": 4096}` (สำหรับงานเรา 4096 พอ ถ้าทำ RAG อาจ 6144–8192 แต่กิน VRAM/เวลา prefill มากขึ้น)
- **keep_alive default = 5 นาที** — ตั้ง `OLLAMA_KEEP_ALIVE=-1` (ค้างตลอด) หรือส่ง `keep_alive=-1` ในคำขอ เพื่อไม่ให้ตอนกรรมการถามแล้วต้องรอโหลดโมเดลใหม่ (cold start หลายวินาที) — ทำ "warm-up call" ตอนเปิดระบบ
- **ตรวจ GPU/CPU**: `ollama ps` คอลัมน์ PROCESSOR ต้องเป็น `100% GPU`
- **OLLAMA_HOST** default `127.0.0.1:11434` → ไม่ต้องเปิด 0.0.0.0 ถ้า FastAPI อยู่เครื่องเดียวกัน (ปลอดภัยกว่า)
- **OLLAMA_MODELS** ที่เก็บโมเดล: Windows `C:\Users\<user>\.ollama\models`, macOS `~/.ollama/models`, Linux `/usr/share/ollama/.ollama/models` → copy โฟลเดอร์นี้ไปเครื่องอื่นได้ (สำรองออฟไลน์)
- **Flash attention** เปิดอัตโนมัติถ้า hardware รองรับ; **KV cache quantization** `OLLAMA_KV_CACHE_TYPE=q8_0` ลด VRAM ของ context ครึ่งหนึ่ง (ไม่จำเป็นสำหรับ 1.5B)

### 5.2 Structured outputs (JSON schema)

ส่ง JSON schema ใน `format` ของ `/api/chat` แนะนำ: ใช้ Pydantic สร้าง schema + validate กลับ, ตั้ง `temperature 0`, **ใส่ schema เป็นข้อความใน prompt ด้วย** เพื่อ "ground" โมเดล [Structured outputs docs](https://docs.ollama.com/capabilities/structured-outputs)

```python
from ollama import chat
from pydantic import BaseModel
class Country(BaseModel):
    name: str; capital: str; languages: list[str]
resp = chat(model="qwen2.5:1.5b", messages=[...],
            format=Country.model_json_schema(), options={"temperature": 0})
country = Country.model_validate_json(resp.message.content)
```

(Structured output = constrained decoding ด้วย grammar → รับประกัน *รูปแบบ* JSON แต่ **ไม่รับประกันความถูกต้องของเนื้อหา** — จึงต้องให้ code คำนวณตัวเลข)

### 5.3 Tool / function calling

- `qwen2.5` บน Ollama มี capability **tools** [library/qwen2.5](https://ollama.com/library/qwen2.5); `llama3.2`, `qwen3`, และโมเดล Typhoon ของ scb10x ทุกตัว (ยกเว้น translate รุ่นแรก/OCR) ก็มี tools [ollama.com/scb10x](https://ollama.com/scb10x)
- Python SDK ส่งฟังก์ชัน Python ตรง ๆ ใน `tools=[fn]` ได้ (สร้าง schema จาก signature+docstring) → อ่าน `response.message.tool_calls` → รันฟังก์ชัน → ส่งกลับเป็น `{"role":"tool","tool_name":name,"content":str(result)}` → เรียก `chat` อีกครั้ง [Tool calling docs](https://docs.ollama.com/capabilities/tool-calling)
- **ความเป็นจริงกับโมเดล 1–1.5B:** การเลือก tool และกรอก argument ผิดบ่อย (Typhoon2-1B รายงาน function-calling 34.96% ภาษาไทย / 45.60% อังกฤษ [model page](https://ollama.com/scb10x/llama3.2-typhoon2-1b-instruct)) → **แนะนำ "router แบบ structured output" แทน tool calling อิสระ**: ให้โมเดลตอบ JSON `{"intent": "price|grade|match|moisture|general", "batch_code": "..."}` ด้วย `format=` schema ที่มี `enum` จำกัด แล้ว code เป็นคนเรียกฟังก์ชันเอง ถ้า regex เจอ batch code ในคำถามแล้วก็ไม่ต้องให้ LLM หาเลย

### 5.4 เลือกโมเดล: ภาษาไทย ~1–2B บน Ollama

| โมเดล (Ollama tag) | ขนาดไฟล์ | Context | Tools | ภาษาไทย | หมายเหตุ |
|---|---|---|---|---|---|
| **`qwen2.5:1.5b`** | 986MB | 32K | ✓ | ระบุรองรับไทยใน 29+ ภาษา | **ค่าเริ่มต้น** (organizer ยกตัวอย่าง) — รายงานของ SCB10X ระบุว่าในกลุ่มขนาดเล็ก Qwen2.5-1.5B นำ Typhoon2-1B ใน ThaiExam/TGAT/TPAT (อ้างอิงทุติยภูมิ: [บทความ Typhoon 2](https://medium.com/scb10x/introducing-typhoon-2-0806fb040c45) — เข้าถึงฉบับเต็มไม่ได้ ตัวเลขยังไม่ยืนยัน) |
| `qwen3:1.7b` | 1.4GB | 40K | ✓ + thinking | ดี (multilingual) | **ต้องส่ง `think=False`** มิฉะนั้นจะ "คิด" ยาวก่อนตอบ ช้ามากบนเครื่องเล็ก [thinking docs](https://docs.ollama.com/capabilities/thinking) |
| `scb10x/llama3.2-typhoon2-1b-instruct` | 808MB (Q4_K_M) | 128K | ✓ | ฝึกไทยเฉพาะ; IFEval-TH 52.46% | ภาษาไทยเป็นธรรมชาติ แต่ reasoning อ่อน [ollama](https://ollama.com/scb10x/llama3.2-typhoon2-1b-instruct) |
| `gemma3:1b` | 806MB | 32K | ไม่ระบุบนหน้า | รองรับ 140+ ภาษา | text-only; ไทยใช้ได้แต่สั้น [library/gemma3](https://ollama.com/library/gemma3) |
| `llama3.2:1b` | 1.3GB | 128K | ✓ | ไทยเป็นภาษาที่ "officially supported" | คุณภาพไทยด้อยกว่า Typhoon2 ตามรายงาน SCB10X [library/llama3.2](https://ollama.com/library/llama3.2) |
| `scb10x/llama3.2-typhoon2-3b-instruct` | ~2GB | 128K | ✓ | ดีขึ้นชัด | ถ้ากติกาอนุญาต >1.5B |
| `scb10x/typhoon2.5-qwen3-4b` | 2.5GB (Q4_K_M) | 256K | ✓ | ดีที่สุดในงบ 4GB VRAM | ใหญ่กว่าเกณฑ์ ~1.5B; พอดี GTX 1650 4GB แต่ context ใหญ่จะล้น [ollama](https://ollama.com/scb10x/typhoon2.5-qwen3-4b) |
| `scb10x/typhoon2.1-gemma3-4b` | ~2.6GB | — | ✓ | ดี | เช่นเดียวกัน |

**ข้อสรุป:** ใช้ `qwen2.5:1.5b` เป็นหลัก (ปลอดภัยต่อกติกา + ดีที่สุดในงบขนาด) แต่ **ทำ eval ภาษาไทยเองภายใน 1 ชั่วโมง**: เตรียม 20 prompt จริง (เขียนรายงาน 5, Q&A เกษตรกร 10, อธิบาย match 5) รันกับ 3–4 โมเดลด้านบน ให้สมาชิกทีม 2 คนให้คะแนน 1–5 (ความถูกต้อง/ความเป็นธรรมชาติ/ทำตาม schema) — ใช้ผลนั้นตัดสินและนำเสนอกรรมการเป็นหลักฐานการเลือกโมเดล (กรรมการชอบ)

> เกร็ด: ดึงโมเดลจาก HF GGUF ตรงได้ด้วย `ollama pull hf.co/<user>/<repo>:<quant>` แต่โมเดล scb10x มีบน Ollama registry แล้ว ไม่จำเป็น

### 5.5 กรรมการอาจบังคับโมเดลหรือไม่?

- ไม่พบประกาศ/กติกาทางการของ TGR#20 บนเว็บ ณ วันที่ค้น (ค้นแล้วพบเพียงข่าว TGR ครั้งก่อน ๆ เช่น [TGR2025 ICT Mahidol](https://news.ict.mahidol.ac.th/?p=64444)) — ข้อมูลที่ทีมมีคือ poster ของผู้จัดที่ยกตัวอย่าง `ollama qwen2.5:1.5b` และสเปก i5/16GB/GTX1650
- **สมมติฐานที่ปลอดภัย:** อาจถูกกำหนดให้ใช้โมเดล/ขนาดใดขนาดหนึ่ง หรือกรรมการอาจเปลี่ยนโมเดลหน้างาน → (1) `MODEL_NAME` อ่านจาก env/config, (2) prompt ทุกตัวต้องทำงานกับ qwen2.5:1.5b ได้ดี, (3) pull โมเดลสำรองไว้ทั้งหมดล่วงหน้า, (4) ยืนยันกติกาในวันงาน (ทีมไม่ติดต่อผู้จัดล่วงหน้า)

### 5.6 ประสิทธิภาพบน GTX 1650 4GB / CPU (ตัวเลขประมาณการ — ต้องวัดเอง)

- qwen2.5:1.5b Q4_K_M (~1GB) + KV cache 4K ใส่ 4GB VRAM ได้สบาย → ควรเป็น `100% GPU`
- เว็บประมาณการ (ไม่ใช่ benchmark จริง) ให้ ~21 tok/s สำหรับ qwen2.5-1.5B บน GTX 1650 [willitrunai](https://willitrunai.com/de/can-run/qwen-2.5-1.5b-on-gtx-1650-4gb) — ตัวเลขนี้ดูต่ำเกินจริงสำหรับโมเดล 1GB บนการ์ดแบนด์วิดท์ ~128 GB/s (ขีดจำกัดทางทฤษฎีหลายสิบ–ราว 100 tok/s); **ให้วัดจริงด้วย `ollama run qwen2.5:1.5b --verbose`** ดู `eval rate` และ `prompt eval rate`
- CPU-only (i5 รุ่นใหม่, 16GB): คาดว่า ~10–25 tok/s สำหรับ 1.5B Q4 (ประมาณการ — วัดจริง)
- รายงาน 1 หน้า ~300 token ภาษาไทย (ไทยกิน token มากกว่าอังกฤษ ~2–3 เท่า) → GPU: ไม่กี่วินาที, CPU: 15–30 วินาที → **ใช้ streaming แสดงทีละคำบน UI** และ pre-generate รายงานของ batch เดโมไว้ล่วงหน้า (cache ใน `report.llm_text`)
- GTX 1650 ไม่มี Tensor core แบบ RTX แต่ Ollama (CUDA, compute capability 7.5) รองรับ — ตรวจ driver NVIDIA ล่าสุดก่อนเดินทาง

### 5.7 Prompt patterns กัน hallucination

1. **Compute facts in code, pass JSON** — prompt มีบล็อก `FACTS (JSON)` ที่คำนวณแล้วเท่านั้น
2. **บังคับรูปแบบด้วย `format=schema`** + ฟิลด์สั้น ๆ (`summary_th`, `strengths[]`, `risks[]`, `recommendation_th`) — ยิ่งสั้นยิ่งเพี้ยนน้อย
3. **ห้ามตัวเลขใหม่:** ระบุใน system prompt "ห้ามสร้างตัวเลขที่ไม่อยู่ใน FACTS" + **post-check ด้วย code**: ดึงตัวเลขทุกตัวจากข้อความ (regex) ต้องพบใน FACTS (tolerance) ไม่งั้น retry 1 ครั้ง → ไม่ผ่านใช้ template
4. **ตัวเลขใน PDF ใส่โดย template ไม่ใช่โดย LLM** — LLM เขียนเฉพาะย่อหน้าบรรยาย
5. **temperature 0–0.3, num_predict จำกัด (เช่น 400)**
6. **Few-shot 1 ตัวอย่าง** ภาษาไทยที่ดี (โมเดลเล็กเลียนแบบสไตล์ได้ดีมาก)
7. **ให้ "ไม่ทราบ" เป็นคำตอบที่ถูกต้อง** — Q&A: "ถ้าข้อมูลใน CONTEXT ไม่พอ ให้ตอบว่า 'ไม่มีข้อมูลในระบบ'"
8. ให้ prompt เป็นอังกฤษ (instruction) แต่สั่งให้ตอบไทย — โมเดลเล็กทำตามคำสั่งอังกฤษได้แม่นกว่า (ทดสอบทั้งสองแบบใน eval)

### 5.8 RAG เล็ก ๆ แบบออฟไลน์

- เอกสาร: มาตรฐานสารกาแฟ (มกษ./ICO/SCA), คู่มือกรมวิชาการเกษตร "เทคโนโลยีการผลิตกาแฟโรบัสตา" [DOA 2567](https://doa.go.th/hort/wp-content/uploads/2024/10/คู่มือเทคโนโลยีการผลิตกาแฟโรบัสตา.pdf), FAQ ทีมเขียนเอง ~30–50 ข้อ
- **ขนาดเล็กขนาดนี้ BM25 (`rank_bm25` + `pythainlp` ตัดคำ) ก็พอและไม่กิน VRAM** — แนะนำเริ่มจากนี้
- ถ้าอยากโชว์ "semantic search": `bge-m3` (multilingual 100+ ภาษา, ~1.2GB) ดีกว่า `nomic-embed-text` v1.5 (เน้นอังกฤษ, 274MB) สำหรับภาษาไทย; `nomic-embed-text-v2-moe` เป็น multilingual ที่เล็กกว่า แต่ max 512 tokens [เปรียบเทียบ](https://www.promptquorum.com/prompt-bites/best-embedding-model-local-rag), [nomic v2 moe](https://huggingface.co/nomic-ai/nomic-embed-text-v2-moe) — **ยังไม่มี benchmark ไทยโดยตรง ต้องทดสอบเอง**
- embedding ล่วงหน้าทั้งหมด เก็บเป็น numpy `.npy` + cosine similarity (ไม่ต้องใช้ vector DB) — 500 chunks ค้นได้ใน ms
- ระวัง VRAM: bge-m3 + qwen2.5:1.5b โหลดพร้อมกันบน 4GB — น่าจะพอ แต่ตรวจด้วย `ollama ps`; หรือรัน embedding เฉพาะตอน build index แล้ว query embedding ใช้ CPU
- chunk 300–500 ตัวอักษร, top-k=3, num_ctx 4096 พอ

### 5.9 Use-cases SLM และรูปแบบ I/O

| Use-case | Input (จาก code) | Output schema | หมายเหตุ |
|---|---|---|---|
| Quality report writer | grade breakdown, moisture curve summary, vision defects, price | `{summary_th, strengths[], risks[], recommendation_th}` | ใส่ใน PDF |
| Thai Q&A (เกษตรกร/ผู้ซื้อ) | intent router → ดึงข้อมูล batch/RAG chunks | ข้อความ (stream) | เปิด chat บน Streamlit |
| Match explanation | match breakdown JSON | `{headline_th, reasons_th[], gaps_th[]}` | "ทำไม 87%" |
| Anomaly narrative | rule-based anomaly (เช่น RH>85% 30 นาที, ความชื้นเพิ่มขึ้น) | `{severity, message_th, action_th}` | แจ้งเตือนบน dashboard |

---

## 6. Offline readiness (Checklist)

**Python**
```bash
# บนเครื่องที่มีเน็ต, OS/Python เวอร์ชันเดียวกับเครื่องแข่ง!
pip download -r requirements.txt -d wheels/                       # Windows/x86_64
pip download -r requirements-pi.txt -d wheels-pi/ --platform manylinux2014_aarch64 --only-binary=:all: --python-version 3.11
# ติดตั้งออฟไลน์
pip install --no-index --find-links wheels/ -r requirements.txt
```
- pin เวอร์ชันทุกตัว (`pip freeze > requirements.lock`) และ **ทดสอบติดตั้งบนเครื่องเปล่าที่ปิดเน็ต**
- Pi: piwheels มี wheel arm; หรือเก็บ `.deb` ด้วย `apt-get download` / ทำ image SD card สำรองทั้งใบ (แนะนำที่สุด: `dd`/Raspberry Pi Imager backup 2 ใบ)

**Ollama**
- ติดตั้ง Ollama installer เก็บไว้ใน USB, `ollama pull` ทุกโมเดล (qwen2.5:1.5b, qwen3:1.7b, typhoon2-1b, typhoon2.5-qwen3-4b, bge-m3) แล้ว **copy โฟลเดอร์ models** ไว้ USB/SSD
- ปิด auto-update ของ Ollama/Windows ช่วงแข่ง

**Docker (ถ้าใช้)**: `docker save -o images.tar img1 img2` → `docker load -i images.tar`

**Node / npm (ถ้าใช้ Node-RED หรือหน้า HTML)**
- เก็บ `mqtt.min.js`, `chart.umd.min.js` ไว้ใน `static/vendor/` (ห้าม CDN)
- Node-RED: ติดตั้ง palette ครบแล้ว copy `~/.node-red` ทั้งโฟลเดอร์; หรือ `npm pack`/`npm ci --offline` กับ cache ที่ populate แล้ว

**Arduino/ESP32**
- Arduino IDE: copy โฟลเดอร์ `Arduino15` (boards package esp32) + `Documents/Arduino/libraries` (PubSubClient/ArduinoJson ฯลฯ) หรือใช้ PlatformIO แล้ว copy `.platformio` (มี toolchain ครบ)
- เก็บไฟล์ `.bin` firmware ที่ build แล้ว + `esptool` เพื่อแฟลชซ้ำโดยไม่ต้อง compile

**ฟอนต์/สินทรัพย์**: Sarabun TTF, รูปแผนที่ static, โลโก้, Bootstrap/Tailwind CSS (ถ้าใช้) — local ทั้งหมด

**เครือข่าย**
- **นำ Wi-Fi router ของทีมไปเอง** (2.4 GHz เปิดไว้เสมอ — ESP32 ใช้ได้เฉพาะ 2.4 GHz), ตั้ง SSID/รหัสเดียวกับที่ใช้ซ้อม
- ตั้ง **DHCP reservation** (ผูก MAC→IP) ที่ router: laptop `.10`, Pi `.20`, ESP32 `.31–.39` — ง่ายและเสถียรกว่าตั้ง static ในตัวเครื่อง
- ระวังช่องสัญญาณชนกับทีมอื่น (หลายสิบทีมในห้องเดียว) → ใช้แอป Wi-Fi analyzer เลือก channel 1/6/11 ที่ว่าง; เตรียม **สาย LAN** ให้แล็ปท็อป↔router และ Pi↔router
- ปิด "client isolation/AP isolation" บน router มิฉะนั้นอุปกรณ์มองไม่เห็นกัน

**เวลา (ไม่มีอินเทอร์เน็ต)**
- ให้ **laptop เป็น NTP server**: Linux/Pi ใช้ `chrony` (`local stratum 8` + `allow 192.168.50.0/24`); Windows เปิด W32Time NTP server (`w32tm` + registry `NtpServer Enabled=1`) — ทดสอบล่วงหน้า
- Pi 5 มี RTC ในตัวแต่ต้องต่อแบตเตอรี่ที่ขั้ว J5 ถึงจะจำเวลาตอนปิดเครื่อง — มิฉะนั้นให้ sync จาก laptop (`server 192.168.50.10 iburst`)
- ESP32: `configTime(7*3600, 0, "192.168.50.10")` (SNTP ไป laptop) — **และ server ใส่ `received_at` ของตัวเองเสมอ** ใช้เป็นเวลาหลักถ้า `ts` ของ device เป็น 0/ผิดปกติ
- ตั้ง timezone `Asia/Bangkok` ทุกเครื่อง; เก็บใน DB เป็น UTC epoch แล้วแปลงตอนแสดงผล

**ซ้อมใหญ่:** 2 สัปดาห์ก่อนแข่ง ทำ "offline day" — ปิดเน็ตทั้งหมด เปิดเครื่องจาก cold boot ด้วย `start_all` แล้วเดโมครบ flow 3 รอบ จดเวลาและปัญหา

---

## 7. Reference repo + Code skeletons (ทั้งหมด UNTESTED)

### 7.1 โครงสร้าง repo

```
robusta-aiot/
├── README.md
├── .env.example                 # MODEL_NAME, MQTT_HOST, PUBLIC_BASE, DB_PATH
├── requirements.txt / requirements.lock
├── start_all.bat / start_all.sh # เปิด mosquitto, api, streamlit, warm-up ollama
├── infra/
│   ├── mosquitto/mosquitto.conf
│   ├── chrony/chrony.conf
│   └── router-notes.md          # SSID, IP table
├── firmware/esp32-node/         # (อยู่ในเอกสารอื่น)
├── vision-pi/                   # (อยู่ในเอกสารอื่น) publish -> tgr/v1/.../vision
├── service/
│   ├── config.py
│   ├── db.py                    # engine, WAL, session
│   ├── models.py                # SQLModel tables
│   ├── ingest.py                # paho subscriber
│   ├── domain/
│   │   ├── grading.py
│   │   ├── pricing.py
│   │   ├── matching.py
│   │   ├── anomaly.py
│   │   └── ledger.py            # hash chain events
│   ├── llm/
│   │   ├── client.py            # ollama + schema + validation + fallback
│   │   ├── prompts.py
│   │   └── rag.py               # BM25 / bge-m3
│   ├── reports/
│   │   ├── pdf.py
│   │   └── templates/certificate.html, passport.html
│   ├── main.py                  # FastAPI app + routes
│   └── static/{fonts/Sarabun-*.ttf, vendor/mqtt.min.js, chart.umd.min.js, qr/, live.html}
├── dashboard/
│   ├── Home.py                  # Streamlit
│   └── pages/1_Live.py, 2_Vision.py, 3_Batches.py, 4_Market.py, 5_AI_Assistant.py
├── data/seed/                   # farms.json, buyers.json, demo batches
├── docs/kb/                     # เอกสาร RAG
├── eval/slm_th_eval.py          # สคริปต์ทดสอบโมเดลภาษาไทย
└── tests/test_domain.py
```

`requirements.txt` (pin เวอร์ชันจริงตอน freeze):
```
fastapi
uvicorn[standard]
sqlmodel
paho-mqtt>=2.1
ollama
pydantic>=2
jinja2
qrcode[pil]
weasyprint          # หรือ reportlab[shaping]
streamlit
plotly
pandas
requests
pythainlp
rank-bm25
numpy
```

### 7.2 `service/models.py` + `db.py`

```python
# service/db.py  (UNTESTED)
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import event
from .config import settings

engine = create_engine(f"sqlite:///{settings.DB_PATH}",
                       connect_args={"check_same_thread": False})

@event.listens_for(engine, "connect")
def _sqlite_pragmas(dbapi_conn, _):
    cur = dbapi_conn.cursor()
    cur.execute("PRAGMA journal_mode=WAL;")
    cur.execute("PRAGMA synchronous=NORMAL;")
    cur.execute("PRAGMA busy_timeout=5000;")
    cur.close()

def init_db():
    from . import models  # noqa: register tables
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as s:
        yield s
```

```python
# service/models.py  (UNTESTED)
from datetime import date
from typing import Optional
from sqlmodel import SQLModel, Field, JSON, Column, UniqueConstraint, Index
import time

def now() -> float: return time.time()

class Farm(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str; district: str
    lat: Optional[float] = None; lon: Optional[float] = None
    gap_certified: bool = False

class Batch(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True, unique=True)          # CPN-2026-001
    farm_id: int = Field(foreign_key="farm.id")
    variety: str = "Robusta"
    process: str = "natural"                             # natural/washed/honey
    harvest_date: Optional[date] = None
    weight_kg: float = 0
    target_moisture_pct: float = 12.5                    # TODO ยืนยันกับมาตรฐาน/ผู้ซื้อ
    status: str = "drying"
    created_at: float = Field(default_factory=now)

class SensorReading(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("device_id", "seq"),
                      Index("ix_sr_batch_ts", "batch_id", "ts"))
    id: Optional[int] = Field(default=None, primary_key=True)
    batch_id: Optional[int] = Field(default=None, foreign_key="batch.id")
    device_id: str; seq: int
    ts: float                     # device ts (หรือ received_at ถ้า device ts ใช้ไม่ได้)
    received_at: float = Field(default_factory=now)
    bean_moist_pct: Optional[float] = None
    air_temp_c: Optional[float] = None
    air_rh_pct: Optional[float] = None
    bean_temp_c: Optional[float] = None
    lux: Optional[float] = None

class VisionResult(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("device_id", "seq"),)
    id: Optional[int] = Field(default=None, primary_key=True)
    batch_id: Optional[int] = Field(default=None, foreign_key="batch.id")
    device_id: str; seq: int; ts: float
    n_beans: int
    defects: dict = Field(sa_column=Column(JSON))
    size_dist: dict = Field(sa_column=Column(JSON))
    color_uniformity: float = 0
    defect_rate: float = 0         # คำนวณตอน ingest
    image_path: Optional[str] = None

class Grade(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    batch_id: int = Field(foreign_key="batch.id", index=True)
    ts: float = Field(default_factory=now)
    score: float; grade: str
    breakdown: dict = Field(sa_column=Column(JSON))
    rule_version: str = "g-1.0"

class PriceQuote(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    batch_id: int = Field(foreign_key="batch.id", index=True)
    ts: float = Field(default_factory=now)
    base_price: float; final_price: float
    adjustments: dict = Field(sa_column=Column(JSON))
    rule_version: str = "p-1.0"

class Buyer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str; type: str = "roaster"

class BuyerRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    buyer_id: int = Field(foreign_key="buyer.id")
    min_grade: str = "B"
    max_moisture_pct: float = 12.5
    max_defect_rate: float = 0.08
    min_screen16_pct: float = 0.5
    qty_kg: float = 100
    max_price: float = 200
    preferred_process: Optional[str] = None
    weights: dict = Field(default_factory=dict, sa_column=Column(JSON))

class Match(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    request_id: int = Field(foreign_key="buyerrequest.id")
    batch_id: int = Field(foreign_key="batch.id")
    score_pct: float; feasible: bool
    breakdown: dict = Field(sa_column=Column(JSON))
    explanation_th: Optional[str] = None
    status: str = "proposed"

class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    batch_id: int = Field(foreign_key="batch.id", index=True)
    ts: float = Field(default_factory=now)
    type: str
    data: dict = Field(sa_column=Column(JSON))
    prev_hash: str = ""; hash: str = ""
```

### 7.3 `service/ingest.py` — paho-mqtt v2

```python
# service/ingest.py  (UNTESTED) — ใช้ได้ทั้ง import ใน FastAPI lifespan หรือ `python -m service.ingest`
import json, logging, time, threading
import paho.mqtt.client as mqtt
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from .db import engine
from .models import SensorReading, VisionResult, Batch
from .config import settings

log = logging.getLogger("ingest")
SUBS = [("tgr/v1/+/+/telemetry", 0), ("tgr/v1/+/+/vision", 1), ("tgr/v1/+/+/status", 1)]
device_status: dict[str, str] = {}          # cache ให้ API อ่าน
_batch_cache: dict[str, int] = {}

def _batch_id(s: Session, code: str | None) -> int | None:
    if not code: return None
    if code not in _batch_cache:
        b = s.exec(select(Batch).where(Batch.code == code)).first()
        if not b: return None
        _batch_cache[code] = b.id
    return _batch_cache[code]

def _ts(p: dict) -> float:
    ts = float(p.get("ts") or 0)
    # device ยังไม่ sync เวลา (ปี < 2025) หรือคลาดเกิน 10 นาที → ใช้เวลา server
    return ts if ts > 1.7e9 and abs(ts - time.time()) < 600 else time.time()

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        log.error("connect failed: %s", reason_code); return
    log.info("connected (session_present=%s)", flags.session_present)
    client.subscribe(SUBS)                    # subscribe ใหม่ทุกครั้งที่ reconnect

def on_disconnect(client, userdata, flags, reason_code, properties):
    log.warning("disconnected: %s (paho จะ reconnect เอง)", reason_code)

def on_message(client, userdata, msg):
    parts = msg.topic.split("/")              # tgr/v1/{site}/{dev}/{kind}
    if len(parts) < 5: return
    dev, kind = parts[3], parts[4]
    try:
        if kind == "status":
            device_status[dev] = msg.payload.decode(); return
        p = json.loads(msg.payload)
        with Session(engine) as s:
            bid = _batch_id(s, p.get("batch"))
            if kind == "telemetry":
                s.add(SensorReading(batch_id=bid, device_id=dev, seq=int(p["seq"]), ts=_ts(p),
                    bean_moist_pct=p.get("bean_moist_pct"), air_temp_c=p.get("air_temp_c"),
                    air_rh_pct=p.get("air_rh_pct"), bean_temp_c=p.get("bean_temp_c"), lux=p.get("lux")))
            elif kind == "vision":
                n = max(int(p.get("n_beans", 0)), 1)
                s.add(VisionResult(batch_id=bid, device_id=dev, seq=int(p["seq"]), ts=_ts(p),
                    n_beans=n, defects=p.get("defects", {}), size_dist=p.get("size_dist", {}),
                    color_uniformity=p.get("color_uniformity", 0),
                    defect_rate=sum(p.get("defects", {}).values()) / n,
                    image_path=p.get("image_id")))
            s.commit()
    except IntegrityError:
        pass                                   # QoS1 duplicate (dev, seq) → ข้าม
    except Exception:
        log.exception("bad message on %s", msg.topic)

def build_client() -> mqtt.Client:
    c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="svc-ingest-laptop")
    c.on_connect, c.on_disconnect, c.on_message = on_connect, on_disconnect, on_message
    c.reconnect_delay_set(min_delay=1, max_delay=10)
    c.will_set("tgr/v1/svc/ingest/status", "offline", qos=1, retain=True)
    c.connect_async(settings.MQTT_HOST, settings.MQTT_PORT, keepalive=20)
    return c

def start() -> mqtt.Client:
    c = build_client(); c.loop_start()        # thread พื้นหลัง
    c.publish("tgr/v1/svc/ingest/status", "online", qos=1, retain=True)
    return c

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    c = build_client(); c.loop_forever()
```

> หมายเหตุ: `publish` ก่อนเชื่อมต่อสำเร็จจะถูก queue ไว้ — ถ้าต้องการชัวร์ให้ย้ายไป publish ใน `on_connect`

### 7.4 `service/domain/grading.py`, `pricing.py`, `matching.py`

แนวคิด: **กฎชัด + น้ำหนักชัด + breakdown ทุกขั้น** (กรรมการถาม "ทำไมได้ B" → เปิด breakdown ได้ทันที) ค่าทุกตัวเป็น **ค่าตัวอย่าง** — ต้องปรับให้ตรงมาตรฐานที่ทีมอ้างอิงในเอกสารอื่น (มกษ./SCA/ICO) และราคาตลาดจริง

```python
# service/domain/grading.py  (UNTESTED — thresholds เป็นตัวอย่าง)
from dataclasses import dataclass, asdict

@dataclass
class GradeInput:
    moisture_pct: float        # ค่าเฉลี่ย 10 นาทีล่าสุด
    target_moisture_pct: float
    defect_rate: float         # 0..1 จาก vision
    screen16_up: float         # สัดส่วนเมล็ดขนาด >= screen 16
    color_uniformity: float    # 0..1

# (ชื่อเกณฑ์, น้ำหนัก, ฟังก์ชันให้คะแนน 0..1)
def _moist_score(m, t):
    if m <= t: return 1.0 if m >= t - 2.5 else 0.6          # แห้งเกินไปก็เสียน้ำหนัก/คุณภาพ
    return max(0.0, 1 - (m - t) / 3)                          # เกิน target 3% → 0
CRITERIA = [
    ("moisture",   0.30, lambda g: _moist_score(g.moisture_pct, g.target_moisture_pct)),
    ("defects",    0.35, lambda g: max(0.0, 1 - g.defect_rate / 0.15)),   # 15% defect → 0
    ("size",       0.20, lambda g: min(1.0, g.screen16_up / 0.8)),
    ("uniformity", 0.15, lambda g: g.color_uniformity),
]
GRADE_BANDS = [(85, "A"), (70, "B"), (55, "C"), (0, "Reject")]
HARD_RULES = [  # ข้อห้ามที่ทำให้ตกเกรดทันที ไม่ว่าคะแนนจะเท่าไร
    (lambda g: g.moisture_pct > g.target_moisture_pct + 2.0, "C", "ความชื้นสูงเกิน target > 2% เสี่ยงเชื้อรา"),
    (lambda g: g.defect_rate > 0.20, "Reject", "เมล็ดเสีย > 20%"),
]

def grade(g: GradeInput) -> dict:
    parts = [{"criterion": n, "weight": w, "score": round(f(g), 3),
              "points": round(100 * w * f(g), 1)} for n, w, f in CRITERIA]
    total = round(sum(p["points"] for p in parts), 1)
    letter = next(l for th, l in GRADE_BANDS if total >= th)
    caps = []
    order = ["A", "B", "C", "Reject"]
    for cond, cap, reason in HARD_RULES:
        if cond(g):
            caps.append(reason)
            if order.index(cap) > order.index(letter): letter = cap
    return {"score": total, "grade": letter, "breakdown": parts, "caps": caps,
            "inputs": asdict(g), "rule_version": "g-1.0"}
```

```python
# service/domain/pricing.py  (UNTESTED — ตัวเลขเป็นตัวอย่าง)
GRADE_PREMIUM = {"A": 0.20, "B": 0.08, "C": 0.0, "Reject": -0.35}
PROCESS_PREMIUM = {"washed": 0.05, "honey": 0.07, "natural": 0.0}

def price(base_thb_kg: float, grade: dict, process: str, gap_certified: bool,
          moisture_pct: float, target_moisture: float, demand_index: float = 1.0) -> dict:
    """
    base_thb_kg: ราคาอ้างอิงตลาด (ป้อนมือ/ไฟล์ CSV ล่าสุด — ออฟไลน์)
    demand_index: (จำนวนคำขอซื้อที่ยังเปิด / จำนวน batch ที่ขายได้) clip 0.9–1.1
    """
    adj = []
    def add(name, pct, why): adj.append({"name": name, "pct": round(pct, 3), "why_th": why})
    add("grade", GRADE_PREMIUM[grade["grade"]], f"เกรด {grade['grade']}")
    add("process", PROCESS_PREMIUM.get(process, 0), f"กระบวนการ {process}")
    if gap_certified: add("gap", 0.03, "ฟาร์มได้ GAP")
    if moisture_pct > target_moisture:
        # ปรับตามน้ำหนักน้ำส่วนเกิน (shrink) — ผู้ซื้อต้องตากต่อ
        add("moisture_shrink", -(moisture_pct - target_moisture) / 100, "ความชื้นเกิน target")
    d = max(0.9, min(1.1, demand_index))
    add("demand", d - 1, "ภาวะอุปสงค์ในตลาดของแพลตฟอร์ม")
    total_pct = sum(a["pct"] for a in adj)
    final = round(base_thb_kg * (1 + total_pct), 2)
    return {"base_price": base_thb_kg, "final_price": final, "adjustments": adj,
            "total_pct": round(total_pct, 3), "rule_version": "p-1.0"}
```

```python
# service/domain/matching.py  (UNTESTED)
ORDER = {"A": 3, "B": 2, "C": 1, "Reject": 0}
DEFAULT_W = {"grade": 0.30, "moisture": 0.20, "defects": 0.20, "size": 0.10,
             "price": 0.15, "process": 0.05}

def match(req: dict, lot: dict) -> dict:
    """
    req: buyer_request (min_grade, max_moisture_pct, max_defect_rate, min_screen16_pct,
         qty_kg, max_price, preferred_process, weights)
    lot: {grade, moisture_pct, defect_rate, screen16_up, available_kg, price, process}
    คืน: score_pct (0..100), feasible, hard_fail[], breakdown[]
    """
    w = {**DEFAULT_W, **(req.get("weights") or {})}
    s = sum(w.values()); w = {k: v / s for k, v in w.items()}     # normalize
    # 1) Hard constraints — ไม่ผ่าน = ไม่ feasible (แต่ยังแสดง % เพื่อให้เห็นว่าห่างแค่ไหน)
    hard = []
    if lot["available_kg"] < req["qty_kg"]: hard.append("ปริมาณไม่พอ")
    if ORDER[lot["grade"]] < ORDER[req["min_grade"]]: hard.append("เกรดต่ำกว่าที่ต้องการ")
    # 2) Soft scores 0..1 (ยิ่งดีกว่าเกณฑ์ยิ่งได้มาก มีเพดาน 1)
    def ratio_le(val, limit, slack):   # ค่าน้อยดี: <=limit ได้ 1, เกินลดเชิงเส้นถึง limit+slack = 0
        return 1.0 if val <= limit else max(0.0, 1 - (val - limit) / slack)
    sc = {
        "grade": min(1.0, 0.5 + 0.5 * (ORDER[lot["grade"]] - ORDER[req["min_grade"]] + 1) / 2)
                 if ORDER[lot["grade"]] >= ORDER[req["min_grade"]] else 0.0,
        "moisture": ratio_le(lot["moisture_pct"], req["max_moisture_pct"], 2.0),
        "defects": ratio_le(lot["defect_rate"], req["max_defect_rate"], 0.05),
        "size": min(1.0, lot["screen16_up"] / max(req["min_screen16_pct"], 1e-6)),
        "price": ratio_le(lot["price"], req["max_price"], req["max_price"] * 0.15),
        "process": 1.0 if not req.get("preferred_process")
                   else (1.0 if lot["process"] == req["preferred_process"] else 0.3),
    }
    breakdown = [{"criterion": k, "weight": round(w[k], 3), "score": round(v, 3),
                  "points": round(100 * w[k] * v, 1)} for k, v in sc.items()]
    score = round(sum(b["points"] for b in breakdown), 1)
    return {"score_pct": score, "feasible": not hard, "hard_fail": hard, "breakdown": breakdown}

def rank(req: dict, lots: list[dict], top_k=5):
    res = [{"lot": l, **match(req, l)} for l in lots]
    return sorted(res, key=lambda r: (r["feasible"], r["score_pct"]), reverse=True)[:top_k]
```

**ทำไมเลือกแบบนี้ (สำหรับตอบกรรมการ):** weighted-sum + hard constraints = Multi-Criteria Decision Analysis แบบพื้นฐาน อธิบายได้ทุกคะแนน ผู้ซื้อปรับน้ำหนักเองได้ (slider บน UI) — ต่อยอดได้เป็น assignment แบบ global (Hungarian / `scipy.optimize.linear_sum_assignment`) ถ้ามีหลายผู้ซื้อแย่ง lot เดียวกัน

```python
# service/domain/ledger.py  (UNTESTED) — passport แบบ tamper-evident
import hashlib, json
def chain_hash(prev_hash: str, batch_code: str, ts: float, type_: str, data: dict) -> str:
    body = json.dumps({"p": prev_hash, "b": batch_code, "t": round(ts, 3), "e": type_, "d": data},
                      sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(body.encode()).hexdigest()
# verify: วน event ตาม ts คำนวณ hash ใหม่เทียบกับที่เก็บ → แสดง "Verified ✓" บนหน้า passport
```

### 7.5 `service/llm/client.py` — Ollama + JSON schema + guard + fallback

```python
# service/llm/client.py  (UNTESTED)
import json, re, logging
from pydantic import BaseModel, Field, ValidationError
from ollama import Client
from ..config import settings

log = logging.getLogger("llm")
_client = Client(host=settings.OLLAMA_HOST, timeout=60)     # http://127.0.0.1:11434
OPTS = {"temperature": 0.2, "num_ctx": 4096, "num_predict": 450}

class QualityReport(BaseModel):
    summary_th: str = Field(max_length=500)
    strengths: list[str] = Field(max_length=4)
    risks: list[str] = Field(max_length=4)
    recommendation_th: str = Field(max_length=400)

class MatchExplain(BaseModel):
    headline_th: str
    reasons_th: list[str]
    gaps_th: list[str]

SYSTEM = (
    "You are a coffee quality assistant for Chumphon Robusta. "
    "Answer ONLY in Thai. Use ONLY numbers that appear in FACTS. "
    "Never invent numbers, standards, prices or names. "
    "If FACTS are insufficient, say 'ไม่มีข้อมูลในระบบ'. "
    "Return JSON that matches the given schema exactly."
)

_num = re.compile(r"-?\d+(?:\.\d+)?")
def _numbers_grounded(text: str, facts: dict, tol=0.051) -> bool:
    fact_nums = {float(x) for x in _num.findall(json.dumps(facts, ensure_ascii=False))}
    for x in _num.findall(text):
        v = float(x)
        if v in (0, 1, 2, 3, 4, 5, 100): continue          # ลำดับข้อ/ค่าทั่วไป
        if not any(abs(v - f) <= tol or abs(v - f * 100) <= tol for f in fact_nums):
            return False
    return True

def generate(schema: type[BaseModel], task_th: str, facts: dict, example: str | None = None,
             model: str | None = None, retries: int = 1) -> BaseModel | None:
    user = (f"TASK: {task_th}\nFACTS (JSON):\n{json.dumps(facts, ensure_ascii=False)}\n"
            f"SCHEMA:\n{json.dumps(schema.model_json_schema(), ensure_ascii=False)}")
    msgs = [{"role": "system", "content": SYSTEM}]
    if example:
        msgs.append({"role": "user", "content": "ตัวอย่างรูปแบบคำตอบที่ดี"})
        msgs.append({"role": "assistant", "content": example})
    msgs.append({"role": "user", "content": user})
    for attempt in range(retries + 1):
        try:
            r = _client.chat(model=model or settings.MODEL_NAME, messages=msgs,
                             format=schema.model_json_schema(), options=OPTS,
                             keep_alive=-1, stream=False)
            obj = schema.model_validate_json(r.message.content)
            if _numbers_grounded(r.message.content, facts):
                return obj
            log.warning("ungrounded number, retry %d", attempt)
            msgs.append({"role": "user", "content": "มีตัวเลขที่ไม่อยู่ใน FACTS ให้เขียนใหม่โดยใช้ตัวเลขจาก FACTS เท่านั้น"})
        except (ValidationError, Exception) as e:
            log.warning("llm failed (%s), retry %d", e, attempt)
    return None   # caller ใช้ template fallback

def warmup():
    try:
        _client.generate(model=settings.MODEL_NAME, prompt="สวัสดี", keep_alive=-1,
                         options={"num_predict": 1})
    except Exception as e:
        log.error("ollama warmup failed: %s", e)

# ---- fallback templates (ไม่ใช้ LLM) ----
def report_fallback(f: dict) -> QualityReport:
    return QualityReport(
        summary_th=f"ล็อต {f['batch_code']} ได้เกรด {f['grade']} คะแนน {f['score']} "
                   f"ความชื้น {f['moisture_pct']}% (เป้าหมาย {f['target_moisture_pct']}%)",
        strengths=[b["criterion"] for b in f["breakdown"] if b["score"] >= 0.8],
        risks=f.get("caps", []) or [b["criterion"] for b in f["breakdown"] if b["score"] < 0.5],
        recommendation_th="ตรวจสอบรายละเอียดคะแนนแต่ละเกณฑ์ในตาราง")
```

**Intent router (แทน tool calling อิสระ):**

```python
from typing import Literal
class Intent(BaseModel):
    intent: Literal["moisture", "grade", "price", "match", "how_to", "other"]
    batch_code: str | None = None
# ถ้า regex r"CPN-\d{4}-\d{3}" เจอในข้อความ ใช้เลย ไม่ต้องพึ่ง LLM
# intent → ฟังก์ชัน Python ดึง FACTS → generate(... ) หรือ stream คำตอบสั้น
```

**ถ้าอยากโชว์ native tool calling** (ทำเป็นโหมดเสริม):
```python
def get_batch_moisture(batch_code: str) -> str:
    """คืนค่าความชื้นล่าสุดและเป้าหมายของล็อตกาแฟ (batch_code เช่น CPN-2026-001)"""
    ...
r = _client.chat(model=settings.MODEL_NAME, messages=msgs, tools=[get_batch_moisture])
for call in (r.message.tool_calls or []):
    out = {"get_batch_moisture": get_batch_moisture}[call.function.name](**call.function.arguments)
    msgs += [r.message, {"role": "tool", "tool_name": call.function.name, "content": out}]
final = _client.chat(model=settings.MODEL_NAME, messages=msgs)
```

### 7.6 `service/main.py` — FastAPI endpoints

```python
# service/main.py  (UNTESTED)
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from .db import init_db, get_session
from .models import *
from . import ingest
from .domain import grading, pricing, matching
from .llm import client as llm
from .reports.pdf import render_certificate
from .config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    mqtt_client = ingest.start() if settings.INGEST_IN_API else None
    llm.warmup()
    yield
    if mqtt_client: mqtt_client.loop_stop(); mqtt_client.disconnect()

app = FastAPI(title="Chumphon Robusta AIoT", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="service/static"), name="static")
tpl = Jinja2Templates(directory="service/reports/templates")

def _batch(s, code):
    b = s.exec(select(Batch).where(Batch.code == code)).first()
    if not b: raise HTTPException(404, "batch not found")
    return b

@app.get("/api/health")
def health(): return {"ok": True, "devices": ingest.device_status}

@app.get("/api/batches")
def batches(s: Session = Depends(get_session)): return s.exec(select(Batch)).all()

@app.get("/api/batches/{code}/readings")
def readings(code: str, minutes: int = 120, s: Session = Depends(get_session)):
    import time
    b = _batch(s, code)
    q = select(SensorReading).where(SensorReading.batch_id == b.id,
                                    SensorReading.ts >= time.time() - minutes * 60).order_by(SensorReading.ts)
    return s.exec(q).all()

@app.post("/api/batches/{code}/grade")
def do_grade(code: str, s: Session = Depends(get_session)):
    b = _batch(s, code)
    # ... ดึง moisture เฉลี่ย 10 นาทีล่าสุด + vision ล่าสุด → GradeInput
    gi = grading.GradeInput(moisture_pct=..., target_moisture_pct=b.target_moisture_pct,
                            defect_rate=..., screen16_up=..., color_uniformity=...)
    g = grading.grade(gi)
    s.add(Grade(batch_id=b.id, score=g["score"], grade=g["grade"], breakdown=g)); s.commit()
    return g

@app.post("/api/batches/{code}/price")
def do_price(code: str, base: float, s: Session = Depends(get_session)): ...

@app.post("/api/requests/{req_id}/match")
def do_match(req_id: int, s: Session = Depends(get_session)): ...   # matching.rank(...) → บันทึก Match

@app.post("/api/matches/{match_id}/explain")
def explain(match_id: int, s: Session = Depends(get_session)):
    m = s.get(Match, match_id)
    out = llm.generate(llm.MatchExplain, "อธิบายเหตุผลของคะแนนการจับคู่ให้ผู้ซื้อเข้าใจ", m.breakdown)
    return out or {"headline_th": f"ตรงความต้องการ {m.score_pct}%", "reasons_th": [], "gaps_th": m.breakdown.get("hard_fail", [])}

@app.get("/api/batches/{code}/report.pdf")
def report(code: str, s: Session = Depends(get_session)):
    path = render_certificate(s, _batch(s, code))   # LLM text + template numbers → WeasyPrint
    return FileResponse(path, media_type="application/pdf", filename=f"{code}.pdf")

@app.get("/p/{code}", response_class=HTMLResponse)       # public passport (QR target)
def passport(code: str, request: Request, s: Session = Depends(get_session)):
    b = _batch(s, code)
    return tpl.TemplateResponse(request, "passport.html", {"b": b, "...": "..."})

@app.post("/api/chat")
def chat(q: dict):
    # intent router → facts → stream
    def gen():
        for chunk in llm._client.chat(model=settings.MODEL_NAME, stream=True, keep_alive=-1,
                                      messages=[{"role": "system", "content": llm.SYSTEM},
                                                {"role": "user", "content": q["text"]}]):
            yield chunk.message.content
    return StreamingResponse(gen(), media_type="text/plain; charset=utf-8")
```

รัน: `uvicorn service.main:app --host 0.0.0.0 --port 8000` (ใช้ worker เดียว — ถ้าหลาย worker ingest จะ subscribe ซ้ำ)

### 7.7 `service/reports/pdf.py` (WeasyPrint)

```python
# (UNTESTED)
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
BASE = Path(__file__).resolve().parents[1]
env = Environment(loader=FileSystemLoader(BASE / "reports/templates"))

def render_certificate(s, batch) -> Path:
    facts = ...            # grade, price, moisture, vision, events → dict
    text = llm.generate(llm.QualityReport, "เขียนสรุปคุณภาพล็อตกาแฟสำหรับใบรับรอง", facts) \
           or llm.report_fallback(facts)
    html = env.get_template("certificate.html").render(b=batch, f=facts, t=text,
                                                        qr=f"static/qr/{batch.code}.png")
    out = BASE / "static/reports" / f"{batch.code}.pdf"
    HTML(string=html, base_url=str(BASE)).write_pdf(out)
    return out
```

`certificate.html` (ส่วน CSS สำคัญ):
```html
<style>
@font-face { font-family: "Sarabun"; src: url("static/fonts/Sarabun-Regular.ttf"); }
@font-face { font-family: "Sarabun"; font-weight: bold; src: url("static/fonts/Sarabun-Bold.ttf"); }
@page { size: A4; margin: 18mm; @bottom-right { content: "หน้า " counter(page); font-family: Sarabun; } }
body { font-family: "Sarabun", sans-serif; font-size: 13pt; line-height: 1.5; }
td { overflow-wrap: anywhere; }
</style>
```

### 7.8 Streamlit dashboard (`dashboard/pages/1_Live.py`)

```python
# (UNTESTED)
import requests, pandas as pd, plotly.express as px, streamlit as st
API = "http://127.0.0.1:8000"
st.set_page_config(page_title="Live Drying Monitor", layout="wide")
code = st.selectbox("ล็อต", [b["code"] for b in requests.get(f"{API}/api/batches", timeout=3).json()])

@st.fragment(run_every=2)
def live():
    h = requests.get(f"{API}/api/health", timeout=2).json()
    cols = st.columns(max(len(h["devices"]), 1))
    for c, (dev, stt) in zip(cols, h["devices"].items()):
        c.metric(dev, "🟢 online" if stt == "online" else "🔴 offline")
    df = pd.DataFrame(requests.get(f"{API}/api/batches/{code}/readings", params={"minutes": 120}, timeout=3).json())
    if df.empty: st.info("ยังไม่มีข้อมูล"); return
    df["time"] = pd.to_datetime(df["ts"], unit="s").dt.tz_localize("UTC").dt.tz_convert("Asia/Bangkok")
    last = df.iloc[-1]
    target = 12.5   # ดึงจาก batch จริง
    a, b, c, d = st.columns(4)
    a.metric("ความชื้นเมล็ด", f"{last.bean_moist_pct:.1f}%", f"{last.bean_moist_pct - target:+.1f} จากเป้า",
             delta_color="inverse")
    b.metric("อุณหภูมิอากาศ", f"{last.air_temp_c:.1f}°C")
    c.metric("RH", f"{last.air_rh_pct:.0f}%")
    d.metric("แสง", f"{last.lux:,.0f} lux")
    fig = px.line(df, x="time", y="bean_moist_pct", title="ความชื้นเมล็ด vs เป้าหมาย")
    fig.add_hline(y=target, line_dash="dash", annotation_text="Target")
    st.plotly_chart(fig, use_container_width=True)

live()
```

หน้าอื่น: `4_Market.py` — ฟอร์ม buyer request + slider น้ำหนัก → เรียก `/api/requests/{id}/match` → ตาราง % match + ปุ่ม "ให้ AI อธิบาย"; `5_AI_Assistant.py` — `st.chat_input` + `st.write_stream` จาก `/api/chat`

### 7.9 หน้า live HTML (mqtt.js over WebSockets) — โครง

```html
<!-- service/static/live.html (UNTESTED) -->
<script src="/static/vendor/mqtt.min.js"></script>
<script src="/static/vendor/chart.umd.min.js"></script>
<canvas id="c"></canvas>
<script>
const client = mqtt.connect(`ws://${location.hostname}:9001`, {clientId: "web-" + Math.random().toString(16).slice(2)});
client.on("connect", () => client.subscribe(["tgr/v1/+/+/telemetry", "tgr/v1/+/+/status"]));
const chart = new Chart(document.getElementById("c"), {type: "line",
  data: {labels: [], datasets: [{label: "Bean moisture %", data: []}]}, options: {animation: false}});
client.on("message", (topic, buf) => {
  if (topic.endsWith("/status")) { /* อัปเดตจุดเขียว/แดง */ return; }
  const p = JSON.parse(buf.toString());
  chart.data.labels.push(new Date().toLocaleTimeString("th-TH"));
  chart.data.datasets[0].data.push(p.bean_moist_pct);
  if (chart.data.labels.length > 300) { chart.data.labels.shift(); chart.data.datasets[0].data.shift(); }
  chart.update();
});
</script>
```

### 7.10 `start_all.bat` (Windows) — โครง

```bat
@echo off
set MODEL_NAME=qwen2.5:1.5b
set OLLAMA_KEEP_ALIVE=-1
set OLLAMA_CONTEXT_LENGTH=4096
start "mosquitto" "C:\Program Files\mosquitto\mosquitto.exe" -c C:\topgun\infra\mosquitto\mosquitto.conf -v
start "ollama" ollama serve
timeout /t 3
start "api" .venv\Scripts\uvicorn service.main:app --host 0.0.0.0 --port 8000
start "dash" .venv\Scripts\streamlit run dashboard\Home.py --server.address 0.0.0.0 --server.port 8501 --server.headless true
```
(ถ้า Ollama ติดตั้งเป็น app ที่รันอยู่แล้ว ไม่ต้อง `ollama serve` ซ้ำ — แต่ env var ต้องตั้งเป็น *System environment variable* แล้ว restart Ollama)

---

## 8. แผนงานแนะนำ (5 คน, ~5 สัปดาห์ถึงวันแข่ง)

| สัปดาห์ | Service/SLM lead | Dashboard lead | Market/PDF lead |
|---|---|---|---|
| 1 | Mosquitto + ingest + schema + seed data; **ทดสอบ WeasyPrint/Pango บนแล็ปท็อปจริง** | Streamlit skeleton 5 หน้า | grading/pricing/matching + unit tests |
| 2 | Ollama eval ภาษาไทย 4 โมเดล → เลือก; llm client + guards | Live page + กราฟ moisture vs target | QR + passport page + hash chain |
| 3 | RAG (BM25) + chat; anomaly rules + narrative | Market page + slider weights + explain | PDF certificate ไทย |
| 4 | Integration กับ ESP32/Pi จริง; offline wheel bundle | ขัดเกลา UI, โหมด big screen | demo data story (3 ล็อต: A/B/C) |
| 5 | **Offline dress rehearsal ×3**, backup USB/SD | สคริปต์เดโม 5 นาที | Q&A กรรมการ: "ตัวเลขนี้มาจากไหน" |

---

## 9. แหล่งอ้างอิง

- Mosquitto config man page: https://mosquitto.org/man/mosquitto-conf-5.html
- Mosquitto 2.1.0 release: https://mosquitto.org/blog/2026/01/version-2-1-0-released/ · Eclipse review: https://projects.eclipse.org/projects/iot.mosquitto/releases/2.1/review
- paho-mqtt 2.0 migration: https://eclipse.dev/paho/files/paho.mqtt.python/html/migrations.html
- aMQTT: https://amqtt.readthedocs.io/ · https://www.piwheels.org/project/amqtt
- fastapi-mqtt: https://github.com/sabuhish/fastapi-mqtt
- Streamlit `st.fragment`: https://docs.streamlit.io/develop/api-reference/execution-flow/st.fragment
- Node-RED Dashboard 2.0 GA: https://flowfuse.com/blog/2024/01/dashboard-2-ga/
- WeasyPrint install: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html
- ReportLab 4.4 notes (shaping): https://docs.reportlab.com/releases/notes/whats-new-44/ · https://docs.reportlab.com/rl-arabic · https://reportlab.substack.com/p/review-of-2025
- W3C Thai line breaking: https://www.w3.org/International/tutorials/css3-text/en/slides/Slide0090.html
- Ollama FAQ: https://docs.ollama.com/faq
- Ollama structured outputs: https://docs.ollama.com/capabilities/structured-outputs
- Ollama tool calling: https://docs.ollama.com/capabilities/tool-calling
- Ollama thinking: https://docs.ollama.com/capabilities/thinking
- qwen2.5: https://ollama.com/library/qwen2.5 · qwen3: https://ollama.com/library/qwen3 · gemma3: https://ollama.com/library/gemma3 · llama3.2: https://ollama.com/library/llama3.2
- SCB10X Typhoon on Ollama: https://ollama.com/scb10x · https://ollama.com/scb10x/llama3.2-typhoon2-1b-instruct · https://ollama.com/scb10x/typhoon2.5-qwen3-4b · https://ollama.com/scb10x/typhoon2.1-gemma3-4b
- Typhoon 2 tech report: https://arxiv.org/abs/2412.13702 · บทความ: https://medium.com/scb10x/introducing-typhoon-2-0806fb040c45 (เข้าถึงฉบับเต็มไม่ได้ขณะค้น)
- GTX 1650 estimate (ไม่ใช่ benchmark จริง): https://willitrunai.com/de/can-run/qwen-2.5-1.5b-on-gtx-1650-4gb
- Embedding comparison: https://www.promptquorum.com/prompt-bites/best-embedding-model-local-rag · https://huggingface.co/nomic-ai/nomic-embed-text-v2-moe
- คู่มือกาแฟโรบัสตา กรมวิชาการเกษตร: https://doa.go.th/hort/wp-content/uploads/2024/10/คู่มือเทคโนโลยีการผลิตกาแฟโรบัสตา.pdf
- TGR ครั้งก่อน (บริบท): https://news.ict.mahidol.ac.th/?p=64444

### สิ่งที่ยังไม่ยืนยัน / ต้องทดสอบเอง
1. tok/s จริงบน GTX 1650 และ CPU — วัดด้วย `ollama run <model> --verbose`
2. คุณภาพภาษาไทยของแต่ละโมเดลในงานของเรา — ทำ eval 20 prompts
3. ค่าความชื้นเป้าหมาย/เกณฑ์เกรดตามมาตรฐาน มกษ. สารกาแฟโรบัสตา — ยืนยันกับเอกสาร ACFS (ไม่พบตัวเลขจากการค้นครั้งนี้)
4. กติกา SLM ของ TGR#20 (บังคับโมเดล/ขนาดหรือไม่) — ยืนยันวันงาน; ระหว่างนี้ใช้ qwen2.5:1.5b เป็นหลัก
5. ReportLab Thai shaping ใน `Paragraph` — experimental
6. `gemma3:1b` tool support — หน้า Ollama ไม่ระบุ
