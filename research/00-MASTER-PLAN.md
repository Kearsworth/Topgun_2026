# 00 — MASTER PLAN: TESA Top Gun Rally #20 (Chumphon Robusta AIoT)

> สร้าง 10 ต.ค. 2569 · แข่ง 15–21 พ.ย. 2569 · ทีม 5 คน มหาวิทยาลัยเดียว · ใช้โค้ดที่เตรียมไว้ได้
> ทุกอย่างในนี้ **provisional** — แก้ได้เมื่อได้ข้อมูลใหม่ (บันทึกการเปลี่ยนใน "Decision Log" ท้ายไฟล์)

## 1. รายงานอ้างอิง (อ่านตามบทบาท)
| ไฟล์ | เรื่อง | ใครต้องอ่าน |
|---|---|---|
| [01-training-datasets.md](01-training-datasets.md) | Dataset เมล็ดเสีย/ความสุก + data strategy | Vision |
| [02-vision-pi5.md](02-vision-pi5.md) | กล้อง, light box, OpenCV, classifier บน Pi 5 CPU, โค้ดตั้งต้น | Vision |
| [03-esp32-sensing.md](03-esp32-sensing.md) | เซ็นเซอร์ ~25 ตัว, pitfalls, core 3.x, MQTT, calibration, drills | ESP32 |
| [04-competition-intel.md](04-competition-intel.md) | รูปแบบการแข่ง, หมวดคะแนน, ตารางคาดการณ์, คำถามถามผู้จัด | **ทุกคน** |
| [05-coffee-domain.md](05-coffee-domain.md) | มกษ. 5700, ICE/ICO, ความชื้น/รา, ราคา, EUDR, สูตรเกรด/ราคา | Service, SLM/Pitch |
| [06-service-layer-slm.md](06-service-layer-slm.md) | Mosquitto, FastAPI+SQLite, Streamlit, PDF ไทย, Ollama, offline | Service, Dashboard, SLM |
| [../contracts/CONTRACT.md](../contracts/CONTRACT.md) | Topic + JSON schema กลางของทีม | **ทุกคน** |

## 2. ข้อเท็จจริงสำคัญ (แก้ความเข้าใจเดิมแล้ว)
- **ความชื้นสารกาแฟ ≤ 12.5%** (มกษ. 5700-2561 และ ICO 8–12.5%) — ไม่ใช่ 11–13%
- **มกษ. 5700 (โรบัสตา)**: ตัวอย่าง ≥350 g, % โดยน้ำหนัก — ดำ ≤2, ขึ้นรา ≤0.5, แตก ≤2, แมลง ≤4, ผลแห้ง ≤0.5, สิ่งแปลกปลอม ≤0.5, รวม ≤7; OTA ≤10 µg/kg; **ไม่มีเกรด 1/2** → ระดับเกรดของระบบต้องออกแบบเอง (อิง ICE Robusta Class P/1–4)
- ราคาสารกาแฟคละชุมพร ~110–134 ฿/kg (ก.พ.–มี.ค. 69); ช่องทางคุณภาพได้ 1.3–2.7 เท่า → **เรื่องเล่า pitch: คัดเกรดด้วยข้อมูล = ราคาสูงขึ้น**
- **EUDR บังคับใช้ 30 ธ.ค. 2026** → ต้องมีพิกัดแปลงใน passport (จุดขายตลาดส่งออก)
- Vision: **ห้ามพื้นหลังดำ** (เมล็ดดำหาย), ห้าม IMX500 AI Camera (มี NPU), ใช้ Camera Module 3 + ไฟ CRI≥90 5000–5600K
- Dataset โรบัสต้าไทยสาธารณะ **ไม่มี** → ต้องถ่ายเอง ≥300–500 crop/คลาส
- ESP32: ADC1 เท่านั้นเมื่อเปิด WiFi, core 3.x (`ledcAttach`), PubSubClient publish QoS0 + ต้อง `setBufferSize`
- หมวดคะแนนปีก่อน ๆ: PM, Presentation, Hardware, Server/Viz, AI, **Integration** — แชมป์มักชนะ **PM + Integration**

## 3. บทบาท 5 คน (ทุกคนมีตัวสำรองข้ามสาย)
| # | บทบาท | รับผิดชอบหลัก | สำรองของ |
|---|---|---|---|
| A | **ESP32 / Hardware** | firmware, เซ็นเซอร์, calibration, PWM, drills | Vision (กล้อง/ไฟ) |
| B | **Vision** | light box, dataset, OpenCV, classifier, Pi image | ESP32 |
| C | **Backend / Integration** | Mosquitto, ingest, DB, grading/pricing/matching, contract | Dashboard |
| D | **Dashboard / Market** | Streamlit/เว็บ, passport+QR, PDF, หน้า market | Backend |
| E | **SLM + PM + Pitch (หัวหน้า)** | Ollama, prompts, domain กาแฟ, Trello, pitch deck, ถามผู้จัด | ทุกสาย (ภาพรวม) |

## 4. แผนรายสัปดาห์
### W1 (10–17 ต.ค.) — ท่อครบเส้น + สิ่งที่ต้องทำในโลกจริง
- [x] Contract v1 + simulator + monitor + tests (เสร็จแล้ว)
- [ ] **E**: ส่งคำถามถึงผู้จัด (04 §6) — โดยเฉพาะ: กล้องใครเตรียม, **ใช้ AI coding assistant/cloud LLM ระหว่างแข่งได้ไหม**, ผู้จัดตั้ง broker ให้หรือไม่, เซ็นเซอร์รุ่นอะไร, ใช้ SLM รุ่นอื่นได้ไหม
- [ ] **B**: ส่งอีเมลขอ dataset (AL-ViT: มหิดล/มจธ.; MFU: sujitra.arw@mfu.ac.th), สั่งซื้อเมล็ดโรบัสต้าดิบชุมพร 1–2 kg (ขอแบบมีเมล็ดเสีย/ตกเกรด), สั่ง Camera Module 3 + ไฟ LED CRI≥90
- [ ] **A**: ESP32 จริง → Mosquitto ตาม contract (แทน sim_esp32), LWT + reconnect
- [ ] **C**: FastAPI + SQLite ingest จาก MQTT (ใช้ sim ทดสอบ)
- [ ] **D**: Streamlit dashboard อ่าน DB/MQTT แสดง live
- [ ] **E**: ติดตั้ง Ollama, วัด tok/s `qwen2.5:1.5b` vs `typhoon2-1b` vs `qwen3:1.7b` (think=False) ด้วยชุดคำถามไทย 20 ข้อ (06)
- **DoD**: ESP32 จริง + sim_vision → dashboard แสดงผลภายใน 1 วินาที ไม่ต่อเน็ต

### W2 (18–24 ต.ค.) — ความเสถียร + ข้อมูล
- [ ] **A**: drills 1–5 (03 §9), calibration ความชื้น (ขวดเมล็ดอ้างอิง + น้ำหนัก), PWM พัดลมจากคำสั่ง MQTT
- [ ] **B**: สร้าง light box, ล็อกค่ากล้อง, `crop_beans.py` (segmentation + วัด mm) ทดสอบกับเมล็ดจริง; โหลด dataset สาธารณะ (01) + map เป็น 9 คลาสกลาง
- [ ] **C**: grading (มกษ. 5700 → คะแนน/เกรด), alert rules (รา/แห้งเสร็จ/node offline) → publish `service/alerts`
- [ ] **D**: หน้า passport + QR ต่อ batch
- [ ] **E**: prompt รายงานคุณภาพ (JSON schema output + ตรวจตัวเลข), Trello backlog, โครง pitch
- **DoD**: แจ้งเตือน MOLD_RISK เกิดเองจาก `sim_esp32 --scenario rainy` และสั่งพัดลมกลับอัตโนมัติ

### W3 (25–31 ต.ค.) — Vision + โมเดล
- [ ] **B**: ถ่าย dataset ของเอง (1 คลาส/ถาด), pre-train บน dataset สาธารณะ → fine-tune บนของเอง, export NCNN, วัด ms บน Pi 5; Golden SD image + สำรอง
- [ ] **A**: drills 6–10 (เซ็นเซอร์ที่ไม่เคยใช้ ≤60 นาที); ช่วย B เรื่องไฟ/ขาตั้งกล้อง
- [ ] **C**: pricing + buyer matching (05 §6), API ให้ D และ E
- [ ] **D**: หน้า market (offer/match %), PDF certificate ภาษาไทย (Sarabun) — ทดสอบบนทุกโน้ตบุ๊ก
- [ ] **E**: chatbot ไทยแบบ intent list + เรียก API จริง; RAG เล็กจาก 05 (ถ้าทันเวลา)
- **DoD**: ถ่ายถาดจริง → ผลเกรด/defect บน dashboard ภายใน 5 วินาที

### W4 (1–7 พ.ย.) — Integration เต็มระบบ + ฟีเจอร์ทำคะแนน
- [ ] ทุกคน: เส้นทาง "กาแฟ 1 ล็อต" ครบ: สร้าง batch → ตาก (ESP32) → วิเคราะห์ (Pi) → เกรด → passport/QR → match ผู้ซื้อ → รายงาน SLM
- [ ] ฟีเจอร์เพิ่มแต้ม: ทำนายเวลาตากเสร็จ, Mold Risk Index, ภาพ defect overlay, human-in-the-loop (เมล็ด conf ต่ำ), passport แบบ hash-chain, พิกัด EUDR
- [ ] **E**: pitch deck v1 + ซ้อม 5 นาที
- **DoD**: demo เต็ม 5 นาทีไม่สะดุด 3 ครั้งติด

### W5 (8–14 พ.ย.) — ซ้อมเหมือนจริง + offline
- [ ] Mock rally จับเวลา (ใช้ตารางคาดการณ์ 04 §4.2): โจทย์รายสายบ่าย → ส่งเย็น; integration 1 วัน
- [ ] Offline pack: pip wheels, Ollama models, Arduino libs/core, Docker images, datasheets, research/ ทั้งหมด (06 §6) → ทดสอบบนเครื่องที่ปิด WiFi
- [ ] Fallback: สคริปต์รันแบบ native (ไม่ใช้ Docker), simulator สำรองถ้า hardware พัง, วิดีโอ demo สำรอง
- [ ] Packing list (04 §5) + router ของทีม
- **DoD**: เปิดเครื่องจากศูนย์ → ระบบพร้อม demo ภายใน 15 นาที โดยไม่มีอินเทอร์เน็ต

## 5. สิ่งที่ต้องทำในโลกจริง (Claude ทำแทนไม่ได้)
- [ ] ถามผู้จัด (04 §6) — **สำคัญสุด: ใช้ AI assistant/cloud LLM ระหว่างแข่งได้ไหม**
- [ ] อีเมลขอ dataset AL-ViT และ MFU
- [ ] ซื้อเมล็ดโรบัสต้าดิบชุมพร (มีเมล็ดเสียปน), Camera Module 3, ไฟ LED CRI≥90, gray card, Pi 5 active cooler + PSU 27W, ESP32 สำรอง ≥2
- [ ] ตรวจสเปกโน้ตบุ๊กทุกเครื่อง (อย่างน้อย 2 เครื่องรัน SLM ได้)

## 6. ยังไม่รู้ / ต้องยืนยัน
- เซ็นเซอร์ที่ผู้จัดให้, ใครเตรียมกล้อง, broker ของใคร, starter code ผู้จัด
- เกณฑ์สี Lab สำหรับเมล็ดดำ/เปรี้ยว/ซีด (ยังไม่มีงานวิจัย → ต้องจูนกับเมล็ดจริง)
- ความเร็วจริงของ classifier บน Pi 5 และ SLM บนโน้ตบุ๊กของทีม (ต้องวัดเอง)
- ISO 6673 ยังใช้อยู่หรือถูกแทนแล้ว, ตาราง TCVN 4193, GI โรบัสต้าชุมพร (ที่พบคือ ถ้ำสิงห์ / เขาทะลุ)

## 7. Decision Log (แก้ได้ — จดเหตุผลทุกครั้ง)
| วันที่ | การตัดสินใจ | เหตุผล |
|---|---|---|
| 2026-10-10 | Contract v1: topic `topgun/<team>/<node-type>/<node_id>/<data\|result\|status\|cmd>` | แยก node ชัด, เปลี่ยนเซ็นเซอร์ไม่ต้องแก้ schema |
| 2026-10-10 | Vision = OpenCV crop + classifier เล็ก (ไม่ใช้ detector ทั้งถาด) | เมล็ดเล็กเกินที่ 640px; เร็วกว่าบน CPU |
| 2026-10-10 | Backend = FastAPI + SQLite, Dashboard = Streamlit | เร็วสุดในเวลาจำกัด, ไม่ต้องพึ่ง Docker |
| 2026-10-10 | SLM แค่ "เล่าตัวเลข" ไม่คำนวณ | โมเดล 1.5B คิดเลข/แต่งข้อมูลผิดบ่อย |
