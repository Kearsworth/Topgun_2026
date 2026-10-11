# 00 — MASTER PLAN: TESA Top Gun Rally #20 (Chumphon Robusta AIoT)

> สร้าง 10 ต.ค. 2569 · แข่ง 15–21 พ.ย. 2569 · ทีม 5 คน มหาวิทยาลัยเดียว · ใช้โค้ดที่เตรียมไว้ได้
> ทุกอย่างในนี้ **provisional** — แก้ได้เมื่อได้ข้อมูลใหม่ (บันทึกการเปลี่ยนใน "Decision Log" ท้ายไฟล์)

## 1. รายงานอ้างอิง (อ่านตามบทบาท)
| ไฟล์ | เรื่อง | ใครต้องอ่าน |
|---|---|---|
| [01-training-datasets.md](01-training-datasets.md) | Dataset เมล็ดเสีย/ความสุก + data strategy | Vision |
| [02-vision-pi5.md](02-vision-pi5.md) | กล้อง, light box, OpenCV, classifier บน Pi 5 CPU, โค้ดตั้งต้น | Vision |
| [03-esp32-sensing.md](03-esp32-sensing.md) | เซ็นเซอร์ ~25 ตัว, pitfalls, core 3.x, MQTT, calibration, drills | ESP32 |
| [04-competition-intel.md](04-competition-intel.md) | รูปแบบการแข่ง, หมวดคะแนน, ตารางคาดการณ์, สิ่งที่ต้องยืนยันวันงาน | **ทุกคน** |
| [05-coffee-domain.md](05-coffee-domain.md) | มกษ. 5700, ICE/ICO, ความชื้น/รา, ราคา, EUDR, สูตรเกรด/ราคา | Service, SLM/Pitch |
| [06-service-layer-slm.md](06-service-layer-slm.md) | Mosquitto, FastAPI+SQLite, Streamlit, PDF ไทย, Ollama, offline | Service, Dashboard, SLM |
| [../contracts/CONTRACT.md](../contracts/CONTRACT.md) | Topic + JSON schema กลางของทีม | **ทุกคน** |

## 2. ข้อเท็จจริงสำคัญ (แก้ความเข้าใจเดิมแล้ว)
- **ความชื้นสารกาแฟ ≤ 12.5%** (มกษ. 5700-2561 และ ICO 8–12.5%) — ไม่ใช่ 11–13%
- **มกษ. 5700 (โรบัสตา)**: ตัวอย่าง ≥350 g, % โดยน้ำหนัก — ดำ ≤2, ขึ้นรา ≤0.5, แตก ≤2, แมลง ≤4, ผลแห้ง ≤0.5, สิ่งแปลกปลอม ≤0.5, รวม ≤7; OTA ≤10 µg/kg; **ไม่มีเกรด 1/2** → ระดับเกรดของระบบต้องออกแบบเอง (อิง ICE Robusta Class P/1–4)
- ราคาสารกาแฟคละชุมพร ~110–134 ฿/kg (ก.พ.–มี.ค. 69); ช่องทางคุณภาพได้ 1.3–2.7 เท่า → **เรื่องเล่า pitch: คัดเกรดด้วยข้อมูล = ราคาสูงขึ้น**
- **EUDR บังคับใช้ 30 ธ.ค. 2026** → ต้องมีพิกัดแปลงใน passport (จุดขายตลาดส่งออก)
- Vision: **ห้ามพื้นหลังดำ** (เมล็ดดำหาย), ห้าม IMX500 AI Camera (มี NPU); ใช้กล้อง/ไฟที่ทีมมีอยู่แล้ว (ถ้ามี Camera Module 3 + ไฟแสงขาวสม่ำเสมอจะดีที่สุด)
- Dataset โรบัสต้าไทยสาธารณะ **ไม่มี** และ**ทีมไม่ซื้อของ** → train จาก dataset สาธารณะก่อน แล้ว fine-tune ด้วยเมล็ดจริงถ้าได้ในวันงาน (ซ้อม pipeline ให้เร็ว)
- ESP32: ADC1 เท่านั้นเมื่อเปิด WiFi, core 3.x (`ledcAttach`), PubSubClient publish QoS0 + ต้อง `setBufferSize`
- หมวดคะแนนปีก่อน ๆ: PM, Presentation, Hardware, Server/Viz, AI, **Integration** — แชมป์มักชนะ **PM + Integration**

## 3. บทบาท 5 คน (ทุกคนมีตัวสำรองข้ามสาย)
| # | บทบาท | รับผิดชอบหลัก | สำรองของ |
|---|---|---|---|
| A | **ESP32 / Hardware** | firmware, เซ็นเซอร์, calibration, PWM, drills | Vision (กล้อง/ไฟ) |
| B | **Vision** | light box, dataset, OpenCV, classifier, Pi image | ESP32 |
| C | **Backend / Integration** | Mosquitto, ingest, DB, grading/pricing/matching, contract | Dashboard |
| D | **Dashboard / Market** | Streamlit/เว็บ, passport+QR, PDF, หน้า market | Backend |
| E | **SLM + PM + Pitch (หัวหน้า)** | Ollama, prompts, domain กาแฟ, Trello, pitch deck, ตาราง Assumptions (§6) + ยืนยันวันงาน | ทุกสาย (ภาพรวม) |

## 4. แผนรายสัปดาห์
### W1 (10–17 ต.ค.) — ท่อครบเส้น + สิ่งที่ต้องทำในโลกจริง
- [x] Contract v1 + simulator + monitor + tests (เสร็จแล้ว)
- [ ] **E**: ทีมอ่านตาราง Assumptions & Contingency (§6) ร่วมกัน — ตกลงว่าแต่ละเรื่องเตรียม "แผนหลัก + แผนสำรอง" อะไร (ไม่มีการติดต่อผู้จัดล่วงหน้า)
- [ ] **B**: โหลด dataset สาธารณะ (01) + map เป็นคลาสกลาง; สำรวจกล้อง/ไฟที่ทีมมีอยู่แล้ว (ออปชัน: อีเมลขอ dataset จากผู้วิจัย AL-ViT/MFU — ไม่ใช่ผู้จัด)
- [ ] **A**: ESP32 จริง → Mosquitto ตาม contract (แทน sim_esp32), LWT + reconnect
- [ ] **C**: FastAPI + SQLite ingest จาก MQTT (ใช้ sim ทดสอบ)
- [ ] **D**: Streamlit dashboard อ่าน DB/MQTT แสดง live
- [ ] **E**: ติดตั้ง Ollama, วัด tok/s `qwen2.5:1.5b` vs `typhoon2-1b` vs `qwen3:1.7b` (think=False) ด้วยชุดคำถามไทย 20 ข้อ (06)
- **DoD**: ESP32 จริง + sim_vision → dashboard แสดงผลภายใน 1 วินาที ไม่ต่อเน็ต

### W2 (18–24 ต.ค.) — ความเสถียร + ข้อมูล
- [ ] **A**: drills 1–5 (03 §9) ด้วยเซ็นเซอร์/อุปกรณ์ที่มีอยู่, เขียนขั้นตอน calibration ความชื้นให้พร้อมใช้วันงาน, PWM (LED แทนพัดลมได้) จากคำสั่ง MQTT
- [ ] **B**: `crop_beans.py` (segmentation + วัด mm) ทดสอบกับภาพถาดจาก dataset สาธารณะ (เช่น ชุดเวียดนามแบบทั้งถาด); สคริปต์ตรวจกล้อง/ล็อกค่า/calibrate px→mm (ใช้กับกล้องผู้จัด)
- [ ] **C**: grading (มกษ. 5700 → คะแนน/เกรด), alert rules (รา/แห้งเสร็จ/node offline) → publish `service/alerts`
- [ ] **D**: หน้า passport + QR ต่อ batch
- [ ] **E**: prompt รายงานคุณภาพ (JSON schema output + ตรวจตัวเลข), Trello backlog, โครง pitch
- **DoD**: แจ้งเตือน MOLD_RISK เกิดเองจาก `sim_esp32 --scenario rainy` และสั่งพัดลมกลับอัตโนมัติ

### W3 (25–31 ต.ค.) — Vision + โมเดล
- [ ] **B**: train บน dataset สาธารณะ → export NCNN, วัด ms บน Pi 5; ซ้อม "ได้ภาพใหม่ → fine-tune → NCNN บน Pi" ≤ 1 ชม. (ไว้ใช้กับเมล็ดจริงในวันงาน); Golden SD image + สำรอง
- [ ] **A**: drills 6–10 (เซ็นเซอร์ที่ไม่เคยใช้ ≤60 นาที); ช่วย B เรื่องไฟ/ขาตั้งกล้อง
- [ ] **C**: pricing + buyer matching (05 §6), API ให้ D และ E
- [ ] **D**: หน้า market (offer/match %), PDF certificate ภาษาไทย (Sarabun) — ทดสอบบนทุกโน้ตบุ๊ก
- [ ] **E**: chatbot ไทยแบบ intent list + เรียก API จริง; RAG เล็กจาก 05 (ถ้าทันเวลา)
- **DoD**: ภาพถาด (จาก dataset หรือกล้องที่มี) → ผลเกรด/defect บน dashboard ภายใน 5 วินาที

### W4 (1–7 พ.ย.) — Integration เต็มระบบ + ฟีเจอร์ทำคะแนน
- [ ] ทุกคน: เส้นทาง "กาแฟ 1 ล็อต" ครบ: สร้าง batch → ตาก (ESP32) → วิเคราะห์ (Pi) → เกรด → passport/QR → match ผู้ซื้อ → รายงาน SLM
- [ ] ฟีเจอร์เพิ่มแต้ม: ทำนายเวลาตากเสร็จ, Mold Risk Index, ภาพ defect overlay, human-in-the-loop (เมล็ด conf ต่ำ), passport แบบ hash-chain, พิกัด EUDR
- [ ] **E**: pitch deck v1 + ซ้อม 5 นาที
- **DoD**: demo เต็ม 5 นาทีไม่สะดุด 3 ครั้งติด

### W5 (8–14 พ.ย.) — ซ้อมเหมือนจริง + offline
- [ ] Mock rally จับเวลา (ใช้ตารางคาดการณ์ 04 §4.2): โจทย์รายสายบ่าย → ส่งเย็น; integration 1 วัน
- [ ] Pre-download (เน็ตในงานมีแต่อาจช้า): Ollama models, pip wheels, Arduino core/libs, โมเดล vision ที่ train แล้ว — copy ใส่แฟลชไดรฟ์ไว้สำรอง
- [ ] Fallback: สคริปต์รันแบบ native (ไม่ใช้ Docker), simulator สำรองถ้า hardware พัง, วิดีโอ demo สำรอง
- [ ] Packing list (04 §5) จากของที่ทีมมีอยู่
- **DoD**: เปิดเครื่องจากศูนย์ → ระบบพร้อม demo ภายใน 15 นาที (ทดสอบทั้งมีและไม่มีเน็ต)

## 5. สิ่งที่ต้องทำในโลกจริง (Claude ทำแทนไม่ได้)
> **ไม่มีการติดต่อ/ถามผู้จัดล่วงหน้า** — ทุกเรื่องที่ไม่รู้ใช้วิธี "คาดการณ์ + เตรียมแผนสำรอง" (§6) แล้วยืนยันจริงในวันงาน (§6.1)
- **ไม่มีการซื้อของ** — ใช้อุปกรณ์ที่ทีมมีอยู่ (ESP32-S3 N16R8, Pi 5, โน้ตบุ๊ก, กล้อง/ไฟถ้ามี); สำรวจและจดรายการอุปกรณ์ที่มีจริงในทีม
- [ ] ตรวจสเปกโน้ตบุ๊กทุกเครื่อง (อย่างน้อย 2 เครื่องรัน SLM ได้)
- [ ] (ออปชัน) อีเมลขอ dataset จากผู้วิจัย AL-ViT / MFU

## 6. Assumptions & Contingency (สิ่งที่ไม่รู้ → คาดการณ์ → เตรียมรับทั้งสองทาง)
| # | ไม่รู้ว่า… | คาดการณ์ (แผนหลัก) | ถ้าไม่ใช่ (แผนสำรองที่ต้องเตรียมไว้) |
|---|---|---|---|
| 1 | ใช้ AI coding assistant / cloud LLM ระหว่างแข่งได้ไหม | ✅ **ยืนยันแล้ว: ใช้ได้** | ใช้ Claude Code + CLAUDE.md เร่งงาน; ยังต้องเข้าใจโค้ดพอตอบกรรมการ/debug ได้; เตรียม prompt/งานไว้ล่วงหน้าเพื่อประหยัด token |
| 2 | เซ็นเซอร์ที่ผู้จัดให้ | ความชื้นเมล็ด (analog), temp/RH (I2C/DHT), อาจมี load cell | drills เซ็นเซอร์ ~25 ตัว (03); contract `readings` เปิดรับ key ใหม่; firmware ตั้งขาไว้บนสุดไฟล์ |
| 3 | กล้อง Vision ใครเตรียม | ✅ **ยืนยันแล้ว: ผู้จัดเตรียม** (ไม่รู้รุ่น) | โค้ดรองรับทั้ง Picamera2 และ OpenCV `VideoCapture`; มีสคริปต์ตรวจกล้อง + ล็อกค่า exposure/WB + calibrate px→mm ที่ทำเสร็จใน ≤15 นาทีหน้างาน |
| 4 | Broker / topic / schema ของผู้จัด | ทีมตั้ง Mosquitto เอง | ถ้าผู้จัดกำหนด topic/JSON เอง → topic ทั้งหมดอยู่ใน `topgun/contract.py` ที่เดียว แก้ได้เร็ว; เตรียม "adapter" แปลง payload ของเรา ↔ ของผู้จัด |
| 5 | Starter code ผู้จัด (ปี 2023: FastAPI+MongoDB+MQTT+Docker) | อาจมี | ฝึก MongoDB + Docker Compose พื้นฐานด้วย; โมดูล grading/pricing/matching เขียนเป็น pure Python ย้ายไป stack ไหนก็ได้ |
| 6 | บังคับ SLM รุ่นไหน | `qwen2.5:1.5b` | prompt ทุกตัวต้องผ่านบน qwen2.5:1.5b ก่อน; Typhoon/qwen3 เป็นทางเลือกเมื่อเปิดให้เลือก |
| 7 | ผู้จัดแจก dataset หน้างานไหม | อาจแจก | ซ้อม pipeline "โฟลเดอร์ภาพ → train → NCNN บน Pi" ให้เสร็จ ≤ 1 ชม.; มีโมเดลที่ train ไว้แล้วเป็นสำรอง |
| 8 | อินเทอร์เน็ตในงาน | ✅ **ยืนยันแล้ว: มี** | ยังโหลดโมเดล Ollama/pip ไว้ก่อน (เน็ตอาจช้าเมื่อทุกทีมใช้พร้อมกัน); offline pack เหลือแบบเบา; ถ้าเน็ตล่ม ใช้ hotspot มือถือ |
| 13 | เมล็ดกาแฟจริงสำหรับ vision | ✅ **น่าจะมีในวันงาน** — เป็น dataset ภาพ หรือเมล็ดจริง | เตรียมรับ 2 แบบ: (ก) **ได้ dataset** → สคริปต์ตรวจ/แปลง format (โฟลเดอร์/YOLO/COCO) → train → NCNN ≤1 ชม. (ข) **ได้เมล็ดจริง** → ถ่ายด้วยกล้องผู้จัด → auto-crop/label (1 คลาส/ถาด) → fine-tune; ทั้งสองแบบมีโมเดล pre-train จาก dataset สาธารณะเป็นจุดเริ่ม |
| 9 | Vision ต้องรันบน Pi หรือใช้ GPU โน้ตบุ๊กได้ | ต้องรันบน Pi (ตามผังระบบ) | ไม่ต้องเตรียมเพิ่ม — train บนโน้ตบุ๊กได้อยู่แล้ว |
| 10 | เครื่องมืออื่นที่เคยใช้ (MATLAB/Simulink ปี 2023–25) | อาจมี workshop | ทำความรู้จักพื้นฐาน 1–2 ชม. (ออปชัน) |
| 11 | รูปแบบ pitch (เวลา/ภาษา/ผู้ฟัง) | ~5 นาที ภาษาไทย ขายแนวธุรกิจ | เตรียม deck 3 นาที + 5 นาที, demo สด + วิดีโอสำรอง |
| 12 | ชนิดเซ็นเซอร์ความชื้น | capacitive (analog) | calibration ทั้งแบบ capacitive และแบบน้ำหนัก (load cell) |

### 6.1 Day-1 checklist (ยืนยันในวันงาน ตอนลงทะเบียน/workshop แรก)
ทุกข้อในตาราง §6 → จดคำตอบจริง → อัปเดต Decision Log (§7) แล้วเลือกแผนหลัก/สำรองทันที

### 6.2 ยังไม่รู้ทางเทคนิค (ต้องวัด/จูนเอง)
- เกณฑ์สี Lab สำหรับเมล็ดดำ/เปรี้ยว/ซีด (ยังไม่มีงานวิจัย → ต้องจูนกับเมล็ดจริง)
- ความเร็วจริงของ classifier บน Pi 5 และ SLM บนโน้ตบุ๊กของทีม
- ISO 6673 ยังใช้อยู่หรือถูกแทนแล้ว, ตาราง TCVN 4193, GI โรบัสต้าชุมพร (ที่พบคือ ถ้ำสิงห์ / เขาทะลุ)

## 7. Decision Log (แก้ได้ — จดเหตุผลทุกครั้ง)
| วันที่ | การตัดสินใจ | เหตุผล |
|---|---|---|
| 2026-10-10 | Contract v1: topic `topgun/<team>/<node-type>/<node_id>/<data\|result\|status\|cmd>` | แยก node ชัด, เปลี่ยนเซ็นเซอร์ไม่ต้องแก้ schema |
| 2026-10-10 | Vision = OpenCV crop + classifier เล็ก (ไม่ใช้ detector ทั้งถาด) | เมล็ดเล็กเกินที่ 640px; เร็วกว่าบน CPU |
| 2026-10-10 | Backend = FastAPI + SQLite, Dashboard = Streamlit | เร็วสุดในเวลาจำกัด, ไม่ต้องพึ่ง Docker |
| 2026-10-10 | SLM แค่ "เล่าตัวเลข" ไม่คำนวณ | โมเดล 1.5B คิดเลข/แต่งข้อมูลผิดบ่อย |
| 2026-10-11 | บอร์ดหลัก ESP32-S3 N16R8, สำรอง ESP32 DevKit คลาสสิก | มีอยู่แล้ว, PSRAM สำหรับ offline buffer; คลาสสิกเผื่อโค้ดตัวอย่างผู้จัด |
| 2026-10-11 | ยืนยัน: ใช้ AI assistant/cloud LLM ได้, ผู้จัดเตรียมกล้อง, มีอินเทอร์เน็ต, น่าจะได้ dataset/เมล็ดจริงในงาน | ข้อมูลจากทีม → เน้น pipeline ปรับเข้ากล้อง/ข้อมูลหน้างานให้เร็ว |
| 2026-10-11 | ไม่ซื้ออุปกรณ์/เมล็ด; GitHub public ไว้ให้เพื่อนอ่าน (ยังไม่เพิ่ม collaborator) | ข้อจำกัดของทีม → vision พึ่ง dataset สาธารณะ + fine-tune วันงาน |
| 2026-10-11 | ไม่ติดต่อผู้จัดล่วงหน้า → ใช้ตาราง Assumptions & Contingency (§6) | ข้อจำกัดของทีม; เตรียมรับทั้งสองทาง แล้วยืนยันวันงาน |
