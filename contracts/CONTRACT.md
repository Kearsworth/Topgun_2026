# Data Contract v1 (provisional — เปลี่ยนได้)

ข้อตกลงกลางว่าทุกส่วนคุยกันผ่าน MQTT ด้วย topic และ JSON แบบไหน
**แก้ที่เดียว:** `contracts/schemas/*.schema.json` + `topgun/contract.py` แล้วรัน `pytest`

## Topics
`<root>` = `topgun/<team>` (ตั้งด้วย env `TOPGUN_TEAM`, default `team01`)

| Topic | ใครส่ง → ใครรับ | Schema | QoS / Retain |
|---|---|---|---|
| `<root>/esp32/<node_id>/data` | ESP32 → Service | `esp32_data` | 0 / no |
| `<root>/vision/<node_id>/result` | Pi 5 → Service | `vision_result` | 1 / no |
| `<root>/<esp32\|vision>/<node_id>/status` | node → ทุกคน (LWT = offline) | `node_status` | 1 / **yes** |
| `<root>/<esp32\|vision>/<node_id>/cmd` | Service → node | `command` | 1 / no |
| `<root>/service/alerts` | Service → Dashboard | `alert` | 1 / no |

ตัวอย่างทุกแบบอยู่ใน `contracts/examples/` (ถูก validate ใน `tests/`)

## กฎสำคัญ
- ทุก payload มี `"v": 1` (เวอร์ชัน contract) — ถ้าเปลี่ยนแบบไม่ backward-compatible ให้ขึ้นเป็น 2
- **เซ็นเซอร์ใหม่ = key ใหม่ใน `readings`** ไม่ต้องแก้ schema; ใส่หน่วยท้ายชื่อ: `_pct _c _kg _lux _ppm`
  key ที่รู้จักแล้ว (`bean_moisture_pct`, `air_rh_pct`, ...) มีช่วงค่าที่ถูกตรวจ
- `ts` = Unix seconds; ESP32 ที่ไม่มี NTP ละได้ แล้ว Service ใส่เวลาตอนรับ
- `batch_id` ผูกข้อมูลทั้งหมดเข้ากับกาแฟ 1 ล็อต (รูปแบบเสนอ: `CRB-<ปี>-<เลข>`)
- `class_counts`: key `normal` = เมล็ดดี, key อื่นทั้งหมด = เมล็ดเสีย
- คำสั่ง `outputs` เป็น % 0–100 (PWM duty) เช่น `fan_pct`, `led_pct`; node ต้องเพิกเฉยฟิลด์ที่ไม่รู้จัก
- ESP32 ใช้ PubSubClient จะ publish ได้แค่ QoS 0 และ buffer default 256 bytes → เรียก `setBufferSize(1024)`

## ทดสอบ
```bash
mosquitto -c infra/mosquitto.conf -v           # terminal 1
python -m tools.monitor                         # terminal 2: ตรวจทุกข้อความ OK/BAD
python -m sim.sim_esp32 --scenario rainy        # terminal 3
python -m sim.sim_vision                        # terminal 4
```
