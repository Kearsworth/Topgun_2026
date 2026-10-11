# 04 — ข่าวกรองการแข่งขัน TESA Top Gun Rally #20 (TGR2026)

> ค้นคว้าเมื่อ 10 ต.ค. 2569 (2026-10-10) · แหล่งข้อมูล: เว็บ tesa.or.th, ข่าวมหาวิทยาลัย, บล็อกผู้เข้าแข่งขัน และ**ภาพเอกสารประกาศ TGR2026 ที่อยู่ในโฟลเดอร์โปรเจกต์** (`/Users/kearsworth/Desktop/Topgun_2026/*.jpg`)
> หลักการ: **[VERIFIED]** = มีแหล่งอ้างอิง · **[INFERENCE]** = ทีมวิจัยอนุมานเอง ไม่ใช่กติกาทางการ

---

## 0. บทสรุปผู้บริหาร (Executive Summary)

1. **ข้อมูลทางการ TGR2026 บนเว็บแทบไม่มี**: tesa.or.th (ณ 10 ต.ค. 2569) ยังไม่มีโพสต์ TGR2026 เลย ข้อมูลทางการที่มีคือ**โปสเตอร์และภาพเอกสารโจทย์ในโฟลเดอร์โปรเจกต์** ซึ่งยืนยันชื่อธีม วันที่ สถานที่ ผู้จัด ฮาร์ดแวร์ และ System Diagram (ESP32 Sensing Node + Raspberry Pi 5 Vision Node → MQTT Broker → Service Layer → Next-Gen Market)
2. **รูปแบบการแข่งค่อนข้างคงที่ทุกปี** (#14–#19): ค่าย 7 วัน (มาถึง 1 วัน + แข่ง ~5 วัน + ประกาศผล) **ทีมละ 5 คนจากสถาบันเดียวกัน** ช่วงเช้าเป็น workshop แยกสาย ช่วงบ่ายทำโจทย์รายวันแล้วส่ง (บางปีส่งเช้าวันถัดไป) ประกาศคะแนนรายหมวด ช่วงท้ายมี**โจทย์ Integration** 1–1.5 วัน แล้วปิดด้วย **Pitching + Demo** ต่อกรรมการ
3. **การคละทีมข้ามมหาวิทยาลัย: ไม่พบหลักฐานในรอบ #14–#19** ทุกแหล่งระบุทีมจากสถาบันเดียว (เช่น See-It2025 มข., Baan Lae Suan มหิดล, Vertiz มธ.) ดังนั้น **การเตรียมทีมล่วงหน้าคุ้มค่ามาก** (ยืนยันแล้วโดยทีม: ไม่คละทีม)
4. **หมวดคะแนนเกือบทุกปีมี**: Project Management, Presentation/Pitching, สายฮาร์ดแวร์/AIoT, สาย Server/Visualization, สาย AI/ข้อมูลเฉพาะโจทย์, System/Battlefield Integration และ Friendship Award (โหวตกันเอง)
5. **คาดการณ์สำหรับ 2026** [INFERENCE]: สาย (a) ESP32 sensing (ความชื้น/อุณหภูมิ/สภาพการตาก) (b) Raspberry Pi 5 vision (ความสุก/คัดเกรด/ตำหนิเมล็ด แบบไม่มี AI HAT → โมเดลเล็กบน CPU) (c) Server/MQTT/Dashboard/Traceability (d) Local SLM บนโน้ตบุ๊ก (qwen2.5:1.5b — สรุปรายงานคุณภาพ, ตอบผู้ซื้อ, matching/pricing) (e) Integration + Pitch แบบ "ขายให้ตลาด/ผู้ซื้อ" (Next-Gen Market)
6. **เตรียมตัวเร่งด่วน**: (1) ท่อ ESP32→MQTT→Pi/Server→Dashboard ที่รันได้แบบ offline ในวงแลนเดียว (2) โมเดล vision เบาบน Pi 5 CPU (3) Ollama + qwen2.5:1.5b + prompt/structured output + RAG เล็ก ๆ (4) Docker compose ที่ทดสอบซ้ำแล้ว + แผนสำรองตอน demo (5) แม่แบบ pitch deck + Trello/Agile สำหรับ PM

---

## 1. ข้อมูลทางการ TGR2026 (#20) — [VERIFIED]

### 1.1 จากโปสเตอร์ทางการ (`841465765_...jpg` ในโฟลเดอร์โปรเจกต์)
| หัวข้อ | รายละเอียด |
|---|---|
| ชื่องาน | The Best of the Best Embedded System Developers — **TESA Top Gun Rally #20** |
| ธีม | **CHUMPHON ROBUSTA AIoT PLATFORM — Toward the Next-Gen Market** |
| วันที่ | **15–21 พฤศจิกายน 2569** |
| สถานที่ | สถาบันเทคโนโลยีพระจอมเกล้าเจ้าคุณทหารลาดกระบัง **วิทยาเขตชุมพรเขตรอุดมศักดิ์** จ.ชุมพร |
| ผู้จัด | TESA ร่วมกับ คณะวิศวกรรมศาสตร์ สจล., วิทยาเขตชุมพรฯ สจล., สำนักงานนวัตกรรมแห่งชาติ (NIA) |
| รางวัล | ชิงถ้วยพระราชทาน สมเด็จพระกนิษฐาธิราชเจ้า กรมสมเด็จพระเทพรัตนราชสุดาฯ |
| Gold Sponsors | Toyota Tsusho Nexty Electronics (Thailand), Deaware |
| Silver Sponsors | Silicon Craft, Design Gateway, Forth, VAAM |
| Bronze Sponsors | Xsense, Abiotich, Inspire Communications, KKT, Aimagin, Zanegrowth, P.G. Intergroup, PTS Combination, Octa Lanes |

ภาพบนโปสเตอร์ (ภาพประกอบ ไม่ใช่กติกา) แสดง dashboard: Ripeness %, Moisture 12.8%, Defect Rate, Bean Size, Quality Grade A, คะแนน cupping (Aroma/Body/Acidity/Balance/Aftertaste), **AI Vision Analysis** (Ripe/Semi/Unripe), **Moisture Monitoring (target 11–13%)**, **Traceability Passport (QR, Batch ID)**, **Dynamic Pricing (AI)** ตามเกรด, **Buyer Request & Matching**, **Quality Certificate / Generate Report**, เซนเซอร์ 28.5°C / 78% RH / Soil

### 1.2 จากภาพเอกสารโจทย์ (ไฟล์ jpg อื่นในโฟลเดอร์)
- **รูป 2 Area-Based Context & Pain Points**: Mixed ripeness → Dry process (ความชื้นสูง) → Moisture variability (ตากไม่สม่ำเสมอ) → Defects (สีผิด/แตก/เสี่ยงรา) → Grading (คัดเกรดแบบ subjective, เกรด A–D, R) → Market value (มูลค่าตลาดจำกัด)
- **รูป 3 Technology Gaps & Application Opportunities**: Enabling tech = Sensing / Data Processing / AI Analysis (quality prediction & anomaly detection) / Connectivity → ผลลัพธ์ Quality Data, Traceable Quality Information (QR), Decision Support (process improvement, quality mgmt, risk alerts), Market Opportunity (buyer-seller matching) — มีข้อความเน้นว่า **"AIoT is an enabling technology, not the main subject"**
- **รูป 4 System Diagram**: Green Beans → **ESP32 Sensing Node** (ไอคอน probe/ความชื้น) และ **Raspberry Pi 5 Vision Node** (กล้อง) → **MQTT Broker** → **Service Layer** → **Next-Gen Market** (Buyer / Supplier)
- ภาพประกอบผลกาแฟโรบัสต้า: ต้น/ช่อ/ผลสุก, เก็บเกี่ยวแบบรูด (ผลสุกไม่เท่ากัน), การตากผลกาแฟ
- **สิ่งที่ผู้จัดเตรียมให้**: เซ็นเซอร์สำหรับ ESP32
- **สิ่งที่ผู้เข้าแข่งขันต้องเตรียม**:
  1. โน้ตบุ๊ก — อย่างน้อย 1 เครื่องรัน Local SLM ~1.5B (ไฟล์ ~1–1.5 GB) เช่น Ollama `qwen2.5:1.5b` ได้; แนะนำ Core i5, RAM 16GB, NVIDIA GTX 1650 หรือ RTX
  2. ESP32 ที่ใช้ WiFi ได้ และมีขา Digital I/O, Analog Input, PWM
  3. Raspberry Pi 5 — **ห้ามใช้ AI Hardware Extension Board แบบ AI HAT+ และรูปแบบอื่น ๆ**
  4. ปลั๊กพ่วง
- **การเตรียมทีม**: C/C++ สำหรับ ESP32 และ Python Programming

### 1.3 สิ่งที่ยัง**ไม่พบ**ในแหล่งออนไลน์ (ไม่ติดต่อผู้จัดล่วงหน้า → คาดการณ์ไว้ใน 00-MASTER-PLAN §6 แล้วยืนยันวันงาน)
- เอกสารรับสมัคร/ค่าสมัคร/กำหนดปิดรับ, กติกาเต็ม, เกณฑ์คะแนนและน้ำหนัก, รายชื่อหมวด Top Score ปี 2026, กล้องใครเตรียม, มีอินเทอร์เน็ตหรือไม่
- tesa.or.th/blog และ tag "TGR"/"TESA Topgun Rally" ยังไม่มีโพสต์ TGR2026 ณ วันค้นคว้า (https://www.tesa.or.th/blog/categories/top-gun-rally)
- หน้า Facebook https://www.facebook.com/TESA.TGR/ ดึงเนื้อหาไม่ได้ (ต้องล็อกอิน) — ผลค้นหาบอกเพียงว่ามีประกาศ TGR2026 เปิดรับนักศึกษาทั่วประเทศ

### 1.4 บริบท TESA ปี 2026 ที่อาจเกี่ยวข้อง — [VERIFIED แต่ความเกี่ยวโยงกับ TGR = INFERENCE]
- 18 มิ.ย. 2569 TESA เปิดตัว **TESAIoT** แพลตฟอร์ม AIoT (MQTTs/HTTPs, mTLS, dashboard, Edge AI, RAG/AI agents; dev kit = Infineon PSoC Edge E84) — https://www.tesa.or.th/post/thailand-secured-edge-ai-summit-on-june-18-2026 , https://www.tesaiot.com/
- โครงการ "AIoT in Action" (ก.ย.) สอน smart farm: วัดสภาพแวดล้อม, คุมปั๊ม, แจ้งเตือน, AI ตรวจความผิดปกติ ผ่าน Smart IoT Gateway + **MQTT** — https://www.tesa.or.th/post/โครงการฝึกทักษะปัญญาประดิษฐ์และเซนเซอร์-aiot-in-action
- [INFERENCE] ทีมงาน TESA กำลังผลักดัน AIoT/Edge AI/MQTT/dashboard/RAG — มีโอกาสที่ workshop TGR2026 จะใช้แนวคิดคล้ายกัน แต่โจทย์ระบุ ESP32+Pi5 ไม่ใช่ TESAIoT board

---

## 2. ประวัติการแข่งย้อนหลัง (#14–#19) — [VERIFIED]

| ครั้ง/ปี | วันที่ · เจ้าภาพ | ธีม/โจทย์ | หมวดคะแนน (Top Score) | แชมป์ | แหล่ง |
|---|---|---|---|---|---|
| #14 / 2020 | 5–11 ม.ค. 2563 · ม.พะเยา | ระบบติดตาม/จัดการสุขภาวะผู้สูงวัยและประชาชน | สาย Hardware, Server, Data Analytics + Pitch | – | https://www.ubu.ac.th/web/eng/news/17590/ |
| #15 / 2021 | 22–26 ก.พ. 2564 · ม.สยาม | Intelligent Production Control (Smart Manufacturing) | Project Management, Hardware Programming ฯลฯ | – | https://engineer.wu.ac.th/en/blog/2021/03/12/students-of-computer-and-electronics-engineering-awarded-at-the-tesa-top-gun-rally-2021/ |
| #16 / 2022 | 5–10 ก.ย. 2565 · สถาบันเทคโนโลยีจิตรลดา | (ไม่ระบุในแหล่ง) | Project Management, Hardware Programming, Server Programming, Cyber Physical System, Integration System, Presentation, Friendship | "เอางานมาอีก" สจล. | https://www.tesa.or.th/post/ประกาศผลรางวัลการประชันทักษะทางด้านระบบสมองกลฝังตัว-ชิงแชมป์ประเทศไทยครั้งที่-16-tgr2022 |
| #17 / 2023 | 19–25 พ.ย. 2566 · ม.อุบลราชธานี · 58 ทีม/30 สถาบัน | ระบบแสดงผล/จัดการน้ำท่วม-น้ำแล้ง (อุบลฯ) | Project Management, **AIoT Development**, Server Programming, Hydrological Modeling, System Integration, Presentation, Friendship | H2O สจล. | https://www.tesa.or.th/post/หัวข้อ-บล็อกของคุณเกี่ยวกับอะไร-7 , https://www.ubu.ac.th/news.php?id=23636 |
| #18 / 2024 | 10/11–16 พ.ย. 2567 · ม.เกษตรฯ ศรีราชา · ~50–52 ทีม/26–27 สถาบัน | Acoustic & AI-Based Predictive Maintenance with Edge Computing (จำแนกเสียง Normal/Faulty/Non-Stamping) | มี Top Score Machine Learning, Project Management, Hardware Programming, Server Programming, Popular Vote | Resonance สจล. (FFT + Random Forest ใน MATLAB, deploy บน **Raspberry Pi**) | https://www.techsource-asia.com/post-event-tgr-2024/ , https://engineer.rmutt.ac.th/news-all/27369/ |
| #19 / 2025 | 9–15 พ.ย. 2568 · รร.จปร. นครนายก · 69 ทีม/37 สถาบัน (~400 คน) | Defense Innovations: ตรวจจับโดรนด้วย YOLO, จำลองโดรนด้วย Simulink, Command Center dashboard (login + face scan, LINE alert), pitch ขาย "ประธานาธิบดีประเทศ Blue" | Project Management, Presentation, Sensor Fusion & Navigation, AI-Based Drone Detection, Command Post Visualization (9 ทีมเต็ม), Battle Fields Integration, Friendship | See-It2025 มข. | https://www.tesa.or.th/post/tesa-top-gun-rally-19 , https://kku.ac.th/?p=258441 |

หมายเหตุ: ปี 2024 ข่าวคณะวิศวะ มข. อ้างชื่อทีม GEAR-DIN-DANG 2024 เกี่ยวกับผลงาน แต่ระบุว่า มข. ได้รองอันดับ 2 ส่วน TechSource ระบุแชมป์คือ Resonance (สจล.) — ถือว่าแชมป์ 2024 = Resonance ตามแหล่ง sponsor

### 2.1 รูปแบบรายวันจากประสบการณ์จริง — [VERIFIED จากบล็อก]

**TGR #17 (2023) — บล็อกทีม Vertiz มธ.** (https://medium.com/@chidsanuphong3/28471c29fe86)
- ลักษณะ "คล้าย Hackathon" ทีมละ 5 คน แบ่ง 3 สาย: **Hardware (AIoT Development), Server, วิเคราะห์ข้อมูล (Hydrological Modeling)** — เช้าแยกไปเรียนตามสาย บ่ายทำโจทย์ส่ง ทีมเลือกเองว่าจะแบ่ง 5 คนอย่างไร (ทีมนี้: server 2, hardware 1, data 2)
- **เจ้าภาพเป็นผู้ออกโจทย์** ตามปัญหาท้องถิ่น
- วันที่ 1: เดินทาง เข้าพัก (นอนในห้องเรียนที่จัดเป็นห้องนอน)
- วันที่ 2: พิธีเปิด + บรรยายที่มาปัญหา + **Project Management (Agile, feedback loop) มีงานส่งและมีคะแนน** (ทีมใช้ Trello)
- วันที่ 3: Server — **FastAPI + MongoDB + MQTT ทั้งหมดใน Docker Compose**, ได้ IP ในวงแลนส่วนตัวของงาน, มี**โค้ดตั้งต้น**ให้, broker/DB ผู้จัดตั้งไว้ให้ เกณฑ์ส่งงานเย็น: ดึงข้อมูลจาก DB ผู้จัด, บันทึก DB ตัวเอง, REST API ใช้ได้, pub/sub MQTT กับเครื่องผู้จัด, ทุกอย่างรันบน docker compose
- วันที่ 4: Server — **Streamlit dashboard** ดึงข้อมูลจาก MongoDB
- วันที่ 5–6 (ถึงเที่ยง): **โจทย์ Integration** — Hardware train และ deploy โมเดลอ่านระดับน้ำจาก**ภาพ gauge** บนบอร์ด + ส่งผ่าน MQTT; Server รับข้อมูลและมี API ให้ MATLAB ดึงไปคำนวณแล้วส่งกลับ; จากนั้นเตรียม slide **pitching** และแบ่งคน pitch กับคน demo
- วันที่ 7: ประกาศผล (ที่ 1–3, Best Server/Hardware/Hydrological Model/Presentation/PM/Pitching/Friendship) — **~1 เดือนหลังงานมีประกาศเหรียญ (ทอง/เงิน ฯลฯ) ให้ทุกทีมตามคะแนน**

**TGR #16 (2022) — บล็อก suphakit.net** (https://blog.suphakit.net/posts/1662392910649/ , /1662665769834/ , /1662725120736/)
- วันแรก: พิธีเปิด + มอบโจทย์ประจำวัน **ส่ง 9 โมงเช้าวันถัดไป**
- วันที่ 4: requirement ใหม่ + integration (ส่วนที่ยากที่สุด) + **ประกาศคะแนนรายหมวด** (Hardware, PM, Server, Cyber Physical) — คะแนนวันหนึ่งหาย ต้องยื่นตรวจสอบ
- ทีมพกโน้ตบุ๊กแค่ 3 เครื่อง (1 เครื่องเสีย) → สาย Hardware ไม่มีเครื่องใช้
- วันที่ 5: นำเสนอต่อกรรมการ ต้องมี **"Pitching Slide"** (รู้ตัวช้า) และ **Docker สตาร์ท MQTT server ไม่ขึ้นตอน demo** ทั้งที่ทดสอบคืนก่อนแล้ว

**TGR #19 (2025)** (https://www.tesa.or.th/post/tesa-top-gun-rally-19): Problem-Based Learning 1 สัปดาห์, **เช้า workshop เข้มข้น กลางวันรับงานไปทำแล้วส่ง, ให้คะแนนรายวันรายหมวด, คะแนนสะสมสูงสุดชนะ**; ทีมละ 5 คน; มีทีมผู้สังเกตการณ์ (observer) ได้ (TU: 57 ทีมแข่ง + 12 ทีม observer — https://engr.tu.ac.th/news/article/news-tesa-top-gun-rally-2025)

**TGR2025 การรับสมัคร** (https://www.tesa.or.th/post/tgr2025-news): ทีมละ 5 คน, ต้องมีความรู้ทั้ง HW/SW, เปิดรับ ~ปลาย ก.ค.–10 ต.ค., ติดต่อ khanistha@tesa.or.th, ค่ายแบบ "5 วัน 5 คืน" (วันจริงในปฏิทิน 7 วัน)

### 2.2 ผู้ชนะทำอะไรต่างจากคนอื่น — [VERIFIED บางส่วน]
- See-It2025 (แชมป์ 2025): ทำ**เกินเกณฑ์** — real-time streaming display, ออกแบบ back-end ใหม่, ออกแบบ workflow สื่อสารชัด, เน้น usability สำหรับผู้ใช้งานจริง; ได้ Top Score PM + AI + Visualization (https://kku.ac.th/?p=258441)
- H2O (แชมป์ 2023): Top Score ทั้ง Hydrological Modeling และ **System Integration**
- "เอางานมาอีก" (แชมป์ 2022): Top Score PM และ **Integration System**
- Resonance (แชมป์ 2024): Top Score ML + PM, deploy บน Raspberry Pi (edge)
- [INFERENCE] **รูปแบบชัดเจน: แชมป์มักได้ Top Score ใน Project Management และ Integration** — ไม่ใช่แค่เก่งสายเดียว

---

## 3. คำถาม: คละทีมข้ามมหาวิทยาลัยหรือไม่?

- **[VERIFIED]** ในปี #14–#19 ทุกแหล่งรายงานทีมเป็น**ทีมของสถาบันเดียว** ส่งในนามมหาวิทยาลัย มีอาจารย์ที่ปรึกษา บางสถาบันส่งหลายทีม + ทีม observer (เช่น มข. 3 ทีม × 5 คนในปี 2024 — https://www.en.kku.ac.th/web/นักศึกษาวิศวกรรมคอมพิว-3/ ; มหิดล ICT ปี 2024 ทีมหลัก 8 รายชื่อ + ทีม observer — https://news.ict.mahidol.ac.th/?p=29720)
- **[VERIFIED]** ไม่พบแหล่งใดที่ระบุการสุ่ม/คละทีมใหม่หน้างานในช่วงปีดังกล่าว (การค้นหาทั้งไทย/อังกฤษไม่พบ)
- **[INFERENCE]** ความเชื่อว่า "Top Gun Rally คละทีม" อาจมาจากยุคแรก ๆ ของงาน (ก่อน #14) — ไม่สามารถยืนยันได้จากแหล่งที่ค้นพบ
- **ผลต่อกลยุทธ์**: เตรียมแบบทีม (แบ่งบทบาท, ทำ integration ล่วงหน้า, ซ้อม pitch) ได้เต็มที่ แต่ควร**ยืนยันในวันงาน** และให้ทุกคนมีทักษะพื้นฐานข้ามสายพอจะสลับงานได้ (เพราะเช้าต้องแยกไปเรียนคนละสาย)

---

## 4. การคาดการณ์สำหรับ 2026 — [INFERENCE ทั้งหมด]

### 4.1 ประเภทภารกิจ (missions) ที่น่าจะเจอ
อิงจาก System Diagram + pain points + โครงสร้างหมวดคะแนนปีก่อน:

| สาย (คาดว่าเป็นหมวด Top Score) | ภารกิจที่เป็นไปได้ | ทักษะ/เครื่องมือ |
|---|---|---|
| **ESP32 Sensing Node** (คล้าย "Hardware Programming"/"AIoT Development") | อ่านเซนเซอร์ที่ผู้จัดให้ (ความชื้นเมล็ด/ดิน ผ่าน ADC, อุณหภูมิ-ความชื้นอากาศ, น้ำหนัก?), calibration, ส่ง JSON ผ่าน MQTT ตาม topic ที่กำหนด, ควบคุม PWM (พัดลม/ฮีตเตอร์ตาก), แจ้งเตือนเมื่อเกิน threshold (ความชื้นเป้า 11–13%) | Arduino/ESP-IDF C/C++, WiFi, PubSubClient, ADC filtering, deep sleep |
| **Raspberry Pi 5 Vision Node** (คล้าย "AI-Based Detection") | จำแนกความสุกผลกาแฟ (ripe/semi/unripe), ตรวจตำหนิเมล็ดสาร (discolored/broken/mold), วัดขนาดเมล็ด, นับเมล็ด, ให้เกรด A–D — **บน CPU เท่านั้น (ห้าม AI HAT)** | OpenCV, YOLO nano/ MobileNet แบบ ONNX/TFLite/NCNN int8, ถ่ายภาพจาก USB/Pi camera, publish ผล MQTT |
| **Server / Service Layer / Visualization** (คล้าย "Server Programming"/"Command Post Visualization") | MQTT broker (Mosquitto), API (FastAPI), DB (MongoDB/SQLite/Influx), dashboard real-time, **Traceability Passport + QR ต่อ batch**, report/certificate | Docker Compose, FastAPI, Streamlit/Grafana/Node-RED, QR generation |
| **Local SLM / AI สายตลาด** (ใหม่ปีนี้) | ใช้ qwen2.5:1.5b สรุปข้อมูลคุณภาพเป็นรายงานภาษาไทย/อังกฤษ, ตอบคำถามผู้ซื้อ (chat + RAG จากข้อมูล batch), Buyer–Seller matching, คำแนะนำ dynamic pricing, decision support/แจ้งเตือนความเสี่ยงรา, แปลงข้อความเป็นคำสั่ง (function calling/JSON) | Ollama REST API, prompt engineering, JSON/structured output, RAG ขนาดเล็ก, guardrails ต่อ hallucination |
| **Integration** | เชื่อมทั้งหมด: เมล็ด → sensing + vision → MQTT → service → market UI ภายในเวลา ~1–1.5 วัน | สัญญา topic/schema ที่ตกลงกันในทีม, health check |
| **Project Management** | งานส่ง: วิเคราะห์ปัญหา, แผน Agile, backlog, feedback loop | Trello/Notion, Gantt/Kanban |
| **Presentation / Pitching** | pitch แบบธุรกิจ "Toward the Next-Gen Market" — ขายให้ผู้ซื้อ/นักลงทุน/สหกรณ์ (ปีก่อนให้ pitch ขาย "ประธานาธิบดี") + live demo | pitch deck, business model, value ต่อเกษตรกร |

### 4.2 ตารางรายวันที่คาดไว้ (15–21 พ.ย. 2569)
อิงโครงสร้าง #17 และ #19 — **ไม่ใช่กำหนดการทางการ**

| วัน | คาดการณ์ |
|---|---|
| อา. 15 พ.ย. | เดินทาง/ลงทะเบียน/เข้าที่พัก ตั้งโต๊ะ ทดสอบไฟ+เน็ต (อาจมี welcome party) |
| จ. 16 พ.ย. | พิธีเปิด, บรรยาย pain point กาแฟโรบัสต้าชุมพร (อาจมีดูงานสวน/โรงตาก), workshop PM + งานส่ง PM |
| อ. 17 พ.ย. | เช้า workshop แยกสาย (ESP32 / Vision / Server-MQTT / SLM) → บ่ายโจทย์รายสาย ส่งเย็นหรือ 9 โมงวันถัดไป |
| พ. 18 พ.ย. | workshop+โจทย์รายสายรอบ 2 (เช่น dashboard, โมเดล vision, SLM) + ประกาศคะแนนบางหมวด |
| พฤ. 19 พ.ย. | ประกาศ**โจทย์ Integration** + requirement ใหม่ ทำยาว (อาจข้ามคืน) |
| ศ. 20 พ.ย. | ส่ง integration (ราวเที่ยง) → เตรียม pitch deck → pitching + demo ต่อกรรมการ |
| ส. 21 พ.ย. | ปิดงาน ประกาศผล/ถ้วยพระราชทาน/Top Score/Friendship |

### 4.3 ความเสี่ยงสำคัญ
- เครือข่ายในงานเป็น LAN ส่วนตัว / อินเทอร์เน็ตอาจช้าหรือไม่มี → **ต้องดึงโมเดล, Docker image, pip/npm packages, datasheet ไว้ล่วงหน้าแบบ offline**
- Demo พังจาก Docker/MQTT (เกิดจริงปี 2022) → มี fallback script รันแบบ native + วิดีโอสำรอง
- Pi 5 ไม่มี AI HAT → inference ช้า → ใช้โมเดลเล็ก, ลด resolution, int8, NCNN/ONNX Runtime; ระวังความร้อน (ใช้ active cooler)
- โน้ตบุ๊กไม่พอ (เกิดจริงปี 2022) → ทุกคนควรมีเครื่อง ติดตั้ง toolchain ครบ
- SLM 1.5B ตอบมั่ว/ช้า → ใช้กับงานสรุป/จัดรูปแบบที่มี context ชัด, บังคับ JSON, ตัวเลขให้มาจาก DB ไม่ใช่จากโมเดล

---

## 5. Checklist การเตรียมตัว (เรียงตามความสำคัญ) — [INFERENCE]

**P0 — ต้องมีก่อนไป (เหลือ ~5 สัปดาห์)**
1. ☐ สมัครเรียบร้อย + เตรียมแผนหลัก/สำรองสำหรับทุกข้อสงสัย (ส่วนที่ 6 → 00-MASTER-PLAN §6)
2. ☐ ท่อ end-to-end ต้นแบบ: ESP32 (เซนเซอร์จำลอง/จริง) → Mosquitto → FastAPI/DB → dashboard real-time บน Pi 5 หรือโน้ตบุ๊ก — รันได้**ไม่มีอินเทอร์เน็ต**
3. ☐ กำหนด MQTT topic/JSON schema มาตรฐานของทีม (เช่น `tgr/{team}/{node}/{sensor}`) + QoS/retain/LWT
4. ☐ Ollama + `qwen2.5:1.5b` บนโน้ตบุ๊กอย่างน้อย 2 เครื่อง (สำรอง), ทดสอบ latency, เรียกผ่าน REST จาก Python, prompt สรุปรายงานคุณภาพ batch ภาษาไทย + output JSON
5. ☐ Vision บน Pi 5 CPU: pipeline กล้อง → OpenCV → โมเดลเล็ก (YOLOv8n/11n ONNX/NCNN หรือ classifier) วัด FPS จริง; ฝึกทำ dataset+train เร็ว ๆ (Roboflow/Ultralytics) เพราะคาดว่าจะได้ dataset หน้างาน
6. ☐ Docker Compose ของ stack ทดสอบ cold start ซ้ำ ๆ + สคริปต์รันแบบไม่ใช้ Docker สำรอง
7. ☐ ทุกคนเขียน C/C++ ESP32 และ Python ระดับพื้นฐานได้ (ตามที่โจทย์ระบุ "การเตรียมทีม")

**P1 — ควรมี**
8. ☐ แบ่งบทบาท: ESP32/HW 1, Vision 1, Server+Dashboard 1–2, SLM/Integration+PM/Pitch 1 — และมีตัวสำรองข้ามสาย
9. ☐ ความรู้โดเมนกาแฟ: ขั้นตอน dry process, ความชื้นเป้าหมายเมล็ดสาร ~11–13%, ตำหนิเมล็ด, การคัดเกรด, ราคาตามเกรด, traceability — ใช้ใน pitch
10. ☐ แม่แบบ pitch deck (Problem → Pain points ชุมพร → Solution AIoT → Demo → Business model/Next-Gen Market → Impact) + ซ้อม 5 นาที
11. ☐ แม่แบบ PM: Trello board, user stories, sprint รายวัน, retrospective
12. ☐ Traceability: สร้าง batch ID + QR → หน้า passport สาธารณะ
13. ☐ Calibration เซนเซอร์ ADC (ค่ากลาง, filter, map เป็น %)

**P2 — เพิ่มแต้ม**
14. ☐ RAG เล็ก ๆ (เอกสารมาตรฐานเกรดกาแฟ) ให้ SLM ตอบผู้ซื้อ
15. ☐ Buyer-seller matching / dynamic pricing แบบ rule + SLM อธิบายเหตุผล
16. ☐ UX ดี, real-time streaming, แจ้งเตือน (LINE Messaging API — LINE Notify ปิดบริการแล้ว)
17. ☐ ทำความรู้จัก MATLAB/Simulink เบื้องต้น (ปี 2023–2025 ใช้ต่อเนื่อง; sponsor MathWorks)

**ของที่ต้องพก**: โน้ตบุ๊ก ≥5 เครื่อง + charger, ปลั๊กพ่วง (กำหนด), ESP32 สำรอง ≥2, Pi 5 + PSU 27W + active cooler + microSD สำรองที่ flash image พร้อมแล้ว, กล้อง (เตรียมเองทั้ง Camera Module 3 + USB webcam สำรอง), สาย USB-C/ไมโคร, breadboard/jumper/ตัวต้านทาน, router/switch พกพา (ถ้าอนุญาต), SSD/แฟลชไดรฟ์บรรจุ installer/โมเดล/Docker image, หูฟัง, ของใช้ส่วนตัว (เคยนอนในห้องเรียน)

---

## 6. สิ่งที่ยังไม่รู้ — ยืนยันในวันงาน (ทีมไม่ติดต่อผู้จัดล่วงหน้า)

> ใช้เป็น Day-1 checklist; ก่อนถึงวันงานให้เตรียมรับทั้งสองทางตามตาราง Assumptions & Contingency ใน `00-MASTER-PLAN.md` §6
1. กำหนดการรายวันอย่างเป็นทางการ และหมวดคะแนน/น้ำหนักคะแนนปี 2026 มีอะไรบ้าง
2. ทีมต้องมาจากสถาบันเดียวกันทั้งหมดหรือไม่ / มีการคละทีมหรือไม่ / ส่งได้กี่ทีมต่อสถาบัน / มีทีม observer ได้ไหม
3. เซ็นเซอร์ที่ผู้จัดให้มีรุ่นอะไร (ความชื้นเมล็ด? load cell? DHT/SHT?) ระดับแรงดัน 3.3V/5V — ขอ datasheet ล่วงหน้าได้หรือไม่
4. **กล้องสำหรับ Vision Node** ผู้จัดเตรียมหรือทีมต้องนำมา / รุ่นที่อนุญาต
5. ข้อห้ามเพิ่มเติม: ใช้ GPU โน้ตบุ๊กทำ vision ได้ไหม (หรือต้องรันบน Pi), ใช้ cloud API/LLM ภายนอก (ChatGPT/Claude) ระหว่างแข่งได้หรือไม่, ใช้ AI coding assistant ได้หรือไม่, อนุญาต USB accelerator (Coral/NCS) หรือไม่ (โจทย์ห้าม "AI HAT+ และรูปแบบอื่น ๆ")
6. มีอินเทอร์เน็ตไหม / MQTT broker และ server ผู้จัดตั้งให้หรือทีมตั้งเอง
7. เตรียมโค้ดล่วงหน้า/นำ template มาเองได้แค่ไหน
8. จะใช้ SLM รุ่นอื่นนอกจาก qwen2.5:1.5b ได้หรือไม่ (ขนาดเพดาน?)
9. รูปแบบ pitching: เวลา, ผู้ฟัง (บทบาทสมมติ?), ภาษา
10. ที่พัก/อาหาร/ปลั๊กไฟต่อโต๊ะ/ค่าใช้จ่าย/การเดินทางไปวิทยาเขตชุมพร (อ.ปะทิว)

---

## 7. แหล่งอ้างอิง
- โปสเตอร์และเอกสารโจทย์ TGR2026: ไฟล์ภาพใน `/Users/kearsworth/Desktop/Topgun_2026/` (841465765_*.jpg, 811373849_*.jpg, 811534043_*.jpg, 812343725_*.jpg, 812535477_*.jpg, 812754970_*.jpg)
- TESA Top Gun Rally #19 สรุป: https://www.tesa.or.th/post/tesa-top-gun-rally-19
- TGR2025 News (รับสมัคร): https://www.tesa.or.th/post/tgr2025-news
- TGR2025 ประกาศ: https://www.tesa.or.th/post/tesa-crma-tgr2025-01
- ผลรางวัล #17: https://www.tesa.or.th/post/หัวข้อ-บล็อกของคุณเกี่ยวกับอะไร-7
- ผลรางวัล #16: https://www.tesa.or.th/post/ประกาศผลรางวัลการประชันทักษะทางด้านระบบสมองกลฝังตัว-ชิงแชมป์ประเทศไทยครั้งที่-16-tgr2022
- TGR2024 โพสต์ TESA: https://www.tesa.or.th/post/การประชันทักษะทางด้านระบบสมองกลฝังตัว-ชิงแชมป์ประเทศไทยครั้งที่-18-tgr2024
- TGR2024 (TechSource/MathWorks): https://www.techsource-asia.com/post-event-tgr-2024/
- มทร.ธัญบุรี 2024: https://engineer.rmutt.ac.th/news-all/27369/
- มข. 2025: https://kku.ac.th/?p=258441 ; มข. 2024: https://www.en.kku.ac.th/web/นักศึกษาวิศวกรรมคอมพิว-3/
- มธ. 2025: https://engr.tu.ac.th/news/article/news-tesa-top-gun-rally-2025
- มหิดล ICT 2024/2025: https://news.ict.mahidol.ac.th/?p=29720 , https://news.ict.mahidol.ac.th/?p=64444
- ม.อุบลฯ #17: https://www.ubu.ac.th/news.php?id=23636 ; #14: https://www.ubu.ac.th/web/eng/news/17590/
- PSU #17: https://nice.eng.psu.ac.th/index.php/component/content/category/workshop?Itemid=101
- มช. 2022: https://www.cmu.ac.th/th/article/9ae0611c-8c91-4b1c-94eb-941f80385d51
- วลัยลักษณ์ 2021: https://engineer.wu.ac.th/en/blog/2021/03/12/students-of-computer-and-electronics-engineering-awarded-at-the-tesa-top-gun-rally-2021/
- บล็อก #17 (Vertiz): https://medium.com/@chidsanuphong3/28471c29fe86
- บล็อก #16 Day1/4/5: https://blog.suphakit.net/posts/1662392910649/ , https://blog.suphakit.net/posts/1662665769834/ , https://blog.suphakit.net/posts/1662725120736/
- MathWorks TGR: https://ch.mathworks.com/academia/student-competitions/tesa-top-gun-rally.html
- TESAIoT: https://www.tesa.or.th/post/thailand-secured-edge-ai-summit-on-june-18-2026 , https://www.tesaiot.com/
- AIoT in Action: https://www.tesa.or.th/post/โครงการฝึกทักษะปัญญาประดิษฐ์และเซนเซอร์-aiot-in-action
- Facebook TESA TGR: https://www.facebook.com/TESA.TGR/ (ดึงเนื้อหาไม่ได้)
