# 01 — Training Data สำหรับ Vision Node (Green Coffee Bean Defect + Cherry Ripeness)

> สำหรับทีม TESA Top Gun Rally #20 (KMITL Chumphon, 15–21 พ.ย. 2026) · จัดทำ 10 ต.ค. 2026
> Pipeline เป้าหมาย: ถ่ายภาพถาดความละเอียดสูง → OpenCV segment ทีละเมล็ด → crop → tiny classifier (YOLO-cls nano / MobileNetV3, 96–224 px, NCNN/ONNX) บน Pi 5 CPU

## Executive Summary (5 บรรทัด)

1. **ไม่พบ dataset ภาพสารกาแฟ Robusta จากไทยที่เปิดให้ดาวน์โหลด** งาน AL-ViT (Mahidol/KMUTT, 2,098 ภาพ Robusta) ไม่ได้ระบุว่าเปิดข้อมูล ต้องอีเมลขอผู้เขียน
2. **ชุดที่ดีที่สุดที่โหลดได้ทันทีมาจากไทย:** `sujitraarw/coffee-green-bean-with-17-defects-original` (Mae Fah Luang Univ., Arabica, 979 ภาพ, ภาพละ 1 เมล็ด, 17 คลาสตาม SCA) ส่วน `vicanadya/coffee-defect-16-classes` (CC0, ≥40k crop เล็ก) เหมาะใช้ pretrain
3. **ชุดที่ใกล้ Robusta/เอเชียที่สุด:** `hongdanhthai/coffeebeans` (เวียดนาม ปี 2020–22 คาดว่าเป็น Robusta แต่ยังไม่ยืนยัน มีคลาส BLACK/BROKEN/BROWN/INSECT/MOLD/PartlyBlack/IMMATURE เป็นภาพทั้งถาดพร้อม bbox) และ Roboflow "Renies Workspace" ที่ชื่อ ROBUSTA (ยืนยันได้แค่จาก search index)
4. **ด้าน cherry ripeness:** `cienciacafeto/coffee-fruit-maturity` (859 ภาพ, 5 ระดับ, CC BY-NC) และ Roboflow `RipeningCoffee` / `coffee-cherry-mtae4` ใช้ได้ แต่ทั้งหมดเป็นผลบนต้น ไม่ใช่ผลที่รูดกองรวม
5. **กลยุทธ์:** pretrain ด้วย public data ที่ map เข้า 9 คลาสกลาง แล้ว fine-tune และ **ทดสอบด้วยภาพ Robusta ชุมพรที่ทีมถ่ายเองบน rig จริงเท่านั้น** เป้าคือ ≥300–500 crop ต่อคลาส (รวมราว 3–5k crop) โดยถ่ายถาดที่คัดคลาสไว้ก่อนแล้ว เพื่อให้ label ได้อัตโนมัติ

---

## 1. ตารางเปรียบเทียบ

สถานะการตรวจสอบมี 3 แบบ: **V** = ตรวจหน้า/metadata ผ่าน API หรือ WebFetch แล้ว · **V-search** = เห็นใน search index แต่หน้าเว็บบล็อก automated fetch (Roboflow ตอบ HTTP 403) · **paper** = มีแค่ใน paper ไม่มีลิงก์ดาวน์โหลด

| # | Dataset | ชนิดเมล็ด | #ภาพ | รูปแบบภาพ | คลาส | Format | License | สถานะ | คะแนน (1–5) |
|---|---|---|---|---|---|---|---|---|---|
| A1 | Kaggle `sujitraarw/coffee-green-bean-with-17-defects-original` (MFU, ไทย) | Arabica green | 979 | ภาพละ 1 เมล็ด, 500×500 | 17 (SCA) | folders | Unknown (ต้องอ้าง paper) | V | **5** |
| A2 | Kaggle `vicanadya/coffee-defect-16-classes` | green (ไม่ระบุพันธุ์) | ≥40,000 ไฟล์ (API list ถูก cap) | crop เล็กมาก (เฉลี่ย ~1.7 KB/ไฟล์) | 16 (SCA) | folders train/test | CC0 | V | **4** |
| A3 | Kaggle `hongdanhthai/coffeebeans` ("DataCoffee_2022", ชื่อเจ้าของเป็นชาวเวียดนาม) | น่าจะ Robusta เวียดนาม (ยังไม่ยืนยัน) | ~1,160 ภาพ + ชุด train/valid | ทั้งถาด, ~287 KB/ไฟล์ | BLACK, BROKEN, BigBroken, BROWN, IMMATURE, INSECT, MOLD, PartlyBlack, MIXED | Pascal VOC xml + YOLO txt | MIT | V | **4** |
| A4 | Roboflow `renies-workspace` (ROBUSTA DATASET ×หลาย version, "Robusta Coffee Bean Defects" 627 ภาพ seg) | Robusta (ตามชื่อ) | 2.36k / 2.9k / 627 ฯลฯ | มีทั้ง cropped/uncropped | ไม่ทราบ | Roboflow export (YOLO/COCO) | CC BY 4.0 (บางหน้า) | V-search | **4** (ถ้าคลาสใช้ได้) |
| A5 | USK-Coffee (Kaggle mirror `berglingmurphy/coffeebean-usk`, `mfaisalriftiarrasyid/duardata`; HF `duvdar/usk-coffee`; Roboflow mirrors) | Arabica green (อินโดนีเซีย) | 8,000 | ภาพละ 1 เมล็ด, 256×256 | defect / longberry / peaberry / premium | folders | ไม่ระบุ | V (mirrors) | **3** |
| A6 | Telkom Univ. "Green Coffee Bean Defects Classification Dataset" | green | 3,315 (195/คลาส) | ? | 17 (SCAA) | ? | จดลิขสิทธิ์, ไม่มีลิงก์ | V (หน้า IP) / ไม่มีดาวน์โหลด | **2** (ต้องขอ) |
| A7 | Bangladesh — Gope et al., AIMS Agric. Food 2025 | **Arabica + Robusta** | 4,367 | ถาด 40 เมล็ด (5×8) บนกระดาษขาว, 640×640 | black, sour, faded, broken, normal, peaberry | YOLO bbox | ขอผู้เขียน | paper | **3** (ถ้าได้มา = 4) |
| A8 | Bangladesh — Gope et al., Sci. Rep. 2024 | green | >5,000 | ถาด, Nikon D5100, ไฟ 3 ดวง | black, broken, faded, sour | YOLO | "upon reasonable request" | paper | **3** |
| A9 | Kaggle `patopucho/lojano-arabica-coffee` (Ecuador) | Arabica green | (ไม่ได้นับ, 726 MB) | RAW ทั้งถาด + crop 256×256 | good / defective | folders | CC BY-NC 4.0 | V | **3** |
| A10 | Kaggle `vinsentoothpaste/coffee-beans-defect-detection` | green (?) | 1,388 | ทั้งถาด (~1.5 MB) | ไม่ทราบ | YOLO txt | MIT | V | **2–3** |
| A11 | Kaggle `danielmejiar/green-coffee-beans` | green | 600 | ภาพ hi-res (~7.4 MB) ไม่มี label | – | flat folder | Unknown | V | **2** (เอาไว้ทำ segmentation/augment) |
| A12 | Kaggle `j4ckdev/green-coffee-beans-dataset` (Colombia) | green | 11 | ภาพตัวอย่างต่อ defect | 11 defect (ภาษาสเปน) | folder | CC BY-NC-SA | V | **1** |
| A13 | Kaggle `bangsul12/data-fiks` | Arabica (ภาพจาก A1 + normal) | – | – | polygon ที่ SAM สร้างอัตโนมัติ | YOLO-seg | Unknown | V | **3** (ใช้ทดสอบ segmentation) |
| A14 | Roboflow `mfechos-coffee-workspace/coffee-beans-defects-4mnhd` | green | (model v1 = 362 ภาพ) | ถาด | good, dried_pod, foreign_matter, full_black, full_sour | YOLO/COCO | CC BY 4.0 | V-search | **2–3** |
| A15 | Roboflow อื่นๆ: `intern-2024/fyp_` (insect, blackened, green_bean, sour), `hackathon-vgjem/coffee-beans-d2to6`, `bean-defects/defect_detect_ex` (1,766), `coffeebean-3icss/green_coffee_beans` (BY-NC-SA), `ws-kfoki/green_beans-9dpn9` (1,389, CC BY 4.0), `greencoffeebean/greencoffeebeandefectdetection_excelsa` | green | ต่างกันไป | ถาด | ดูในวงเล็บ | Roboflow | ส่วนใหญ่ CC BY 4.0 | V-search | **2** |
| C1 | Kaggle `cienciacafeto/coffee-fruit-maturity` | Arabica cherry บนต้น | 859 ภาพ / 11,044 mask | ภาพธรรมชาติ | unripe, ripe, semi_dry, dry, overripe | seg mask | CC BY-NC 4.0 | V | **3** (ripeness) |
| C2 | Roboflow `naromu-eskfw/ripeningcoffee` | cherry | 859 (v2) | – | ripe, overripe, dry, semi_ripe, unripe | Roboflow | CC BY 4.0 | V-search | **3** |
| C3 | Roboflow `mckenzhie/coffee-cherry-mtae4` | cherry | ? | – | ripe, overripe, semi-ripe, unripe | Roboflow | CC BY 4.0 | V-search | **3** |
| C4 | Kaggle `harisyunanda/dataset-coffee-cherry` | cherry บนต้น | คำอธิบายบอก 1,000 แต่ listing เห็น 432 | ~2 MB/ภาพ | unripe, half-ripe, ripe | YOLO bbox | ODbL | V | **2–3** |
| C5 | Kaggle `luisdanielc/coffee-cherry-maturity-instance-segmentation` | cherry | 675 | – | (ดู data.yaml) | YOLO-seg | CC BY-NC-SA | V | **2–3** |
| C6 | Zenodo 4914786 "Dataset coffee 15 Channels" | cherry | 640 | 224×224×**15 ช่อง (multispectral)** | immature 130, semi-mature 160, mature 160, overripe 112, dry 78 | .rar | CC BY 4.0 | V | **1** (ไม่ใช่ RGB) |
| C7 | HF `pjramg/colombian_coffee` "Coffee fruits in branches" | cherry บนกิ่ง | ~1,594 | – | (COCO) | COCO json | Apache-2.0 | V | **2** |
| C8 | Kaggle `andressac/analyzing-coffe-maturity` (บราซิล) | cherry | ? (16 GB, 7z หลายไฟล์) | hi-res | ระดับสุก แยกตามพันธุ์ | folders | CC BY 4.0 | V | **2** (ใหญ่เกิน) |
| R1 | Kaggle `sot2542/coffee-bean-dataset-v1/v2` + `gpiosenka/...-224-x-224` (ไทย, Bona Coffee JJ Mall) | **คั่วแล้ว** (Arabica) | 4,800 | ภาพ 1 เมล็ด | green / light / medium / dark | folders | CC BY-SA 4.0 | V | **1** (ใช้ได้แค่ pretrain ⚠️ roasted) |
| R2 | GitHub `dont-text-me/roastedcoffeedefectdataset` | **คั่วแล้ว** | ? | – | roasted defects | – | ? | V-search | **1** ⚠️ |

---

## 2. รายละเอียดราย dataset

### 2.1 Robusta / งานวิจัยไทย

**AL-ViT (Mahidol / KMUTT) — ไม่เปิดข้อมูล ต้องติดต่อผู้เขียน**
- Vachmanus S., Pridasawas W., Kusakunniran W., Thamrongaphichartkul K., Phinklao N. "AL-ViT: Label-efficient Robusta coffee-bean defect detection in Thailand using active learning vision transformers", *Intelligent Systems with Applications* 29 (2026), DOI [10.1016/j.iswa.2025.200612](https://doi.org/10.1016/j.iswa.2025.200612)
- ภาพ Robusta 2,098 ภาพ ถ่ายใต้ "controlled lighting ที่เลียนแบบเครื่องคัดเกรด" เริ่มจาก label เพียง 5% ผลลัพธ์ hybrid uncertainty-diversity ได้ acc 97.1% และ F1(defective) 0.956 ด้วย 850 label และต้องใช้แค่ **407 label ก็ถึง 95%** ส่วน MixUp/CutMix ไม่ช่วย (จาก abstract ที่ [KMUTT KIRIM](https://kirim.kmutt.ac.th/converis/portal/detail/Publication/1532355937?lang=en_GB) และ [Mahidol IR](https://repository.li.mahidol.ac.th/handle/123456789/114424))
- ผลรายงานเป็นคลาส "defective" ซึ่งดูเหมือนเป็น **binary (normal vs defective)** แต่ยังไม่ได้อ่าน full text จึงไม่ยืนยัน และ**ยังยืนยันไม่ได้**ว่าเมล็ดมาจาก "ภาคใต้/ภาคตะวันตก" ตามที่ brief ระบุ
- ไม่พบ data availability statement ในหน้า metadata
- **ผู้ที่ควรติดต่อ:** Sirawich Vachmanus และ Worapan Kusakunniran (คณะ ICT ม.มหิดล) กับ Wimolsiri Pridasawas (KMUTT) ให้หาอีเมลจากหน้า paper บน ScienceDirect หรือ [MUREx ICT Mahidol](https://murex.mahidol.ac.th/en/organisations/faculty-of-information-and-communication-technology/) ตอนขอให้บอกว่าเป็นทีมนักศึกษาที่ใช้ข้อมูลเพื่อการแข่งขันที่ไม่ใช่เชิงพาณิชย์ ขอเฉพาะ subset และเสนอ cite
- **บทเรียนที่ใช้ได้เลยแม้ไม่ได้ data:** ใช้ active learning (uncertainty + diversity) ตอน label ภาพที่ทีมถ่ายเอง จะลดงาน label ได้มาก

**A1 — MFU 17 defects (Kaggle) ⭐ แนะนำอันดับ 1**
- URL: https://www.kaggle.com/datasets/sujitraarw/coffee-green-bean-with-17-defects-original (ตรวจผ่าน Kaggle API แล้ว: 979 jpg, ~80 MB, อัปเดต 2024-07-11, ดาวน์โหลด 1,020 ครั้ง)
- ภาพละ 1 เมล็ด 500×500 px (ตรงกับ input แบบ single-bean crop ของเรา) ชนิดเมล็ดคือ Arabica green
- จำนวนต่อคลาส: Broken 62, Cut 66, Dry Cherry 54, Fade 35, Floater 48, Full Black 41, Full Sour 75, Fungus Damage 75, Husk 53, Immature 78, Parchment 54, Partial Black 65, Partial Sour 50, Severe Insect Damage 57, Shell 57, Slight Insect Damage 55, Withered 54 (ชื่อโฟลเดอร์ในไฟล์สะกดว่า "Damange")
- License ระบุ "Unknown" จึงควร cite DOI [10.1016/j.atech.2024.100680](https://doi.org/10.1016/j.atech.2024.100680) (Smart Agricultural Technology 2024) และอีเมลขออนุญาตไว้ก่อน
- ผู้ติดต่อ: **ผศ.ดร.สุจิตรา อรวัชนานุกูล (Sujitra Arwatchananukul) — sujitra.arw@mfu.ac.th** จาก School of Applied Digital Technology / กลุ่ม IATE ม.แม่ฟ้าหลวง (อีเมลจาก paper IJSIT 2025 [PDF](https://ph01.tci-thaijo.org/index.php/IJSIT/article/download/260481/174216/1007771)) มี web demo ที่ http://iate-coffee-inspection.com/ (ยังไม่ได้ตรวจลิงก์นี้)
- งานต่อยอด (IJSIT 2025) ได้ ConvNeXt เดี่ยว 72.94% และ stacking 87.64% บน 17 คลาส ซึ่งบอกว่า **17 คลาสละเอียดเกินไปสำหรับข้อมูลระดับนี้** จึงควรรวมคลาสก่อนเทรน
- ดาวน์โหลด: `kaggle datasets download -d sujitraarw/coffee-green-bean-with-17-defects-original`
- คะแนน 5: เป็นภาพเมล็ดเดี่ยว ใช้ taxonomy SCA ครบ และมาจากไทย แต่ต้องระวังว่าเป็น Arabica สีอาจต่างจาก Robusta และจำนวนต่อคลาสน้อย

**A3 — Vietnam "DataCoffee_2022" (Kaggle) ⭐ ใกล้ Robusta ที่สุดในบรรดาชุดที่โหลดได้**
- URL: https://www.kaggle.com/datasets/hongdanhthai/coffeebeans (MIT, 1.33 GB, อัปเดต 2023-11-06)
- โครงสร้าง (จาก API file listing): `datasets/DataCoffee_2022/<CLASS>/<ช่วงสัดส่วน>/img|xml` เช่น BLACK 0.00–0.05 และ 0.06–0.08, BROWN, BROKEN, BigBroken, IMMATURE, INSECT, MOLD, PartlyBlack, MIXED (รวม LIGHTFM = foreign matter?) ชื่อไฟล์มีน้ำหนักตัวอย่าง เช่น `BLACK_20200802_..._8.04g_157.jpg` จึงน่าจะเป็น**ภาพถาดตัวอย่างขนาด ~8 g ที่ผสม defect ตามสัดส่วน** มี Pascal VOC xml + YOLO txt (train 1,896 / valid 422 ไฟล์)
- เรื่องนี้เป็น Robusta หรือไม่: Kaggle ไม่มีคำอธิบาย เวียดนามปลูก Robusta เป็นหลักและคลาสตรงกับมาตรฐาน TCVN 4193 แต่ **ยังไม่ยืนยันพันธุ์** ต้องเปิดดูภาพหลังดาวน์โหลด
- จุดแข็ง: มีคลาส MOLD และ BROWN (ตรงกับ pain point เรื่องตากในความชื้นสูง) และเป็นภาพถาดเหมือน pipeline เรา จึงใช้ bbox มา crop ทีละเมล็ดได้
- ดาวน์โหลด: `kaggle datasets download -d hongdanhthai/coffeebeans`
- คะแนน 4 (จะเป็น 5 ถ้ายืนยันได้ว่าเป็น Robusta)

**A4 — Roboflow Renies Workspace "ROBUSTA DATASET"**
- URL: https://universe.roboflow.com/renies-workspace (ใน search index เห็น 10 projects / 8.97k ภาพ) มี project ย่อยดังนี้
  - https://universe.roboflow.com/renies-workspace/robusta-dataset-no-digkit3 (CC BY 4.0)
  - https://universe.roboflow.com/renies-workspace/robusta-dataset-no-augmentation (388 ภาพ)
  - https://universe.roboflow.com/renies-workspace/robusta-dataset-uncropped (460 ภาพ)
  - "Robusta Coffee Bean Defects" เป็น instance segmentation 627 ภาพ, base set 2.36k, merged cropped+uncropped 2.9k
- **ยังไม่ทราบคลาสและแหล่งที่มา** (หน้าเว็บตอบ 403 กับ automated fetch) ให้เปิดดูด้วย browser
- ดาวน์โหลด: Roboflow API หรือ pip `roboflow` แล้วเรียก `rf.workspace("renies-workspace").project("<slug>").version(N).download("yolov8")` หรือ `"folder"` สำหรับ classification ต้องใช้ API key ฟรี
- คะแนน 4 แบบมีเงื่อนไข: ต้องดูคลาสและภาพจริงก่อน เพราะอาจเป็น dataset ที่ augment มาซ้ำกันหลาย version

**งานไทยอื่นที่เกี่ยวข้อง (ไม่พบ data สาธารณะ)**
- SWU (Phukhokwai & Wiwatwattana, 2024): ใช้ CNN กับภาพสารกาแฟ ได้ 0.96 สำหรับ green vs defect และ 0.97 สำหรับ 5 defect ([SWU thesis](https://ir-ithesis.swu.ac.th/handle/123456789/2753), [MSDS](https://msds.science.swu.ac.th/19_64199130062)) ภาพมาจากงาน image processing ก่อนหน้า
- KMUTT: "Quality Sorting of Green Coffee Beans from Wet Processing by Using The Principle of Machine Learning" ([KIRIM](https://kirim.kmutt.ac.th/converis/portal/detail/Publication/820469122?lang=en_GB)) ได้ acc 85% กับตัวอย่างน้อย
- กรมวิชาการเกษตร: รายงาน "การจัดชั้นคุณภาพของเมล็ดกาแฟโดยใช้วิธีทางกายภาพและประสาทสัมผัส" ([PDF](https://doa.go.th/plan/wp-content/uploads/2023/08/843การจัดชั้นคุณภาพของเมล็ดกาแฟโดยใช้วิธีทางกายภาพและประสาทสัมผัส.pdf)) พบว่า **severe insect และ fungus เป็น defect ที่พบบ่อยที่สุด** ใน Robusta/Arabica ไทย จึงควรให้ 2 คลาสนี้มีข้อมูลมาก
- KMITL ชุมพร / Kasetsart / PSU: **ไม่พบ** dataset ภาพสาร Robusta ที่เผยแพร่ เจอแค่เครื่องคัดผลสดด้วยน้ำวน ([phtnet](https://www.phtnet.org/research/download/pdf/rb1584t.pdf)) และเอกสารเครื่องคัดด้วยกล้องในคลัง KMITL ([PDF](https://opacimages.lib.kmitl.ac.th/medias/b00279146/%E0%B8%81%E0%B8%A3%E0%B8%97%E0%B8%A3%E0%B8%B1%E0%B8%9E%E0%B8%A2%E0%B9%8C_%E0%B8%97%E0%B8%A3%E0%B8%B1%E0%B8%9E%E0%B8%A2%E0%B9%8C%E0%B8%81%E0%B8%A3%E0%B8%81%E0%B8%B8%E0%B8%A5-%E0%B8%A7%E0%B8%A8.63.pdf1.pdf2.pdf)) ซึ่งยังไม่ได้อ่านรายละเอียด แนะนำให้ถามอาจารย์ KMITL วิทยาเขตชุมพรโดยตรงระหว่างค่าย

### 2.2 Green bean defect (ส่วนใหญ่เป็น Arabica)

**A2 — `vicanadya/coffee-defect-16-classes`** https://www.kaggle.com/datasets/vicanadya/coffee-defect-16-classes
- CC0, ~152 MB, อัปเดต 2026-06-05 แต่ยังไม่มีคำอธิบาย
- ไฟล์ list ผ่าน API ได้ถึง 40,000 แล้วถูก cap จึง**มีมากกว่านั้น** และยังนับไม่ครบ ตัวอย่างใน test: broken 1,275, full black 1,003, immature 921, parchment 1,888, slight insect 1,733, cherry pod 32, foreign material 21 ส่วน train: broken 9,685, full black 7,587, immature 5,063 …
- ไฟล์เฉลี่ย ~1.7 KB ซึ่งน่าจะเป็น crop ความละเอียดต่ำ (เดาว่า ≤64–96 px, ยังไม่ยืนยัน) ชื่อไฟล์ `DSCF1098_JPG_102.jpg` บอกว่า crop จากภาพถาดของกล้อง Fujifilm และอาจผ่าน augmentation ของ Roboflow
- ⚠️ ระวัง **data leakage:** crop จากภาพถาดเดียวกันอาจไปอยู่ทั้ง train และ test
- คะแนน 4 สำหรับ pretrain: ปริมาณมาก ไลเซนส์สะอาด และ input 96 px ใกล้กับของเรา

**A5 — USK-Coffee** (Febriana, Muchtar, Dawood, Lin — IEEE CyberneticsCom 2022)
- 8,000 ภาพ 256×256 แบ่ง 4 คลาสเท่ากัน (2,000/คลาส: train 1,200 / val 400 / test 400) ต้นฉบับอยู่ที่ comvis.unsyiah.ac.id/usk-coffee (ไม่ได้ตรวจ) และมี mirrors ดังนี้
  - Kaggle: https://www.kaggle.com/datasets/berglingmurphy/coffeebean-usk , https://www.kaggle.com/datasets/mfaisalriftiarrasyid/duardata , แบบตัดพื้นหลังแล้ว https://www.kaggle.com/datasets/mfaisalriftiarrasyid/usk-coffee-rmbg
  - HF: https://huggingface.co/datasets/duvdar/usk-coffee
  - Roboflow: https://universe.roboflow.com/proyectocafeunl/usk-coffe-backup-gcaof , seg: https://universe.roboflow.com/yolo-annotated-dataset/usk-coffe-segmentasi
- คลาส defect เป็นคลาสรวมคลาสเดียว จึงใช้ได้แค่สอน normal vs defect และใช้เป็นตัวอย่าง peaberry
- คะแนน 3: ใช้เป็น "normal" และ "defect (generic)" เสริมได้ดี แต่ไม่แยกชนิด defect

**A6 — Telkom University 17-class** https://btp.telkomuniversity.ac.id/landing/ip/HCNA2002256278
- 3,315 ภาพ 195/คลาส (16 defect + Specialty Grade) ตาม SCAA เป็นงานจดลิขสิทธิ์ ไม่มีลิงก์ดาวน์โหลด ผู้ติดต่อคือ Ema Rachmawati (Telkom Univ. Bandung)

**A7/A8 — Bangladesh (Gope et al.)** มีทั้ง Arabica และ **Robusta** จาก Khagrachari
- AIMS 2025 ([article](https://www.aimspress.com/article/doi/10.3934/agrfood.2025050)): กล้อง Canon M50 สูง 73 cm ไฟ 3 ดวง พื้นกระดาษขาว วางเมล็ดเป็นกริด 40 เมล็ด/แผ่น ภาพ 640×640 ทำ YOLO bbox มี 6 คลาส
- Sci. Rep. 2024 ([DOI 10.1038/s41598-024-78598-7](https://doi.org/10.1038/s41598-024-78598-7)): Nikon D5100 สูง 45 cm และระบุ "data can be obtained from the corresponding author upon reasonable request"
- ติดต่อ **hlgope@sau.ac.bd** (Hira Lal Gope, Sylhet Agricultural Univ.)
- setup นี้คล้าย rig ถาดของเราที่สุด จึงคุ้มที่จะอีเมลขอ

**A9 — Lojano Arabica (Ecuador)** https://www.kaggle.com/datasets/patopucho/lojano-arabica-coffee
- มีทั้งภาพถาด RAW/JPG (พื้นเรียบ แสงควบคุม) และ crop 256×256 แยก good/defective
- เหมาะใช้ทดสอบโค้ด segmentation ของเรา เพราะได้คู่ "ภาพถาด → crop" มาพร้อมกัน
- ไลเซนส์ CC BY-NC 4.0 ใช้ในการแข่งขันได้ แต่ห้ามขายโมเดลเชิงพาณิชย์

**อื่นๆ (ประโยชน์รอง)**
- `vinsentoothpaste/coffee-beans-defect-detection` (MIT, 1,388 ภาพ YOLO, ไม่รู้คลาส ต้องดู data.yaml)
- `danielmejiar/green-coffee-beans` (600 ภาพ hi-res ไม่มี label)
- `j4ckdev/green-coffee-beans-dataset` (11 ภาพ)
- Roboflow: `mfechos-coffee-workspace/coffee-beans-defects-4mnhd` ([link](https://universe.roboflow.com/mfechos-coffee-workspace/coffee-beans-defects-4mnhd)), `intern-2024/fyp_` ([link](https://universe.roboflow.com/intern-2024/fyp_)), `bean-defects/defect_detect_ex` ([link](https://universe.roboflow.com/bean-defects/defect_detect_ex)), `ws-kfoki/green_beans-9dpn9` ([link](https://universe.roboflow.com/ws-kfoki/green_beans-9dpn9)), `greencoffeebean/greencoffeebeandefectdetection_excelsa` ([link](https://universe.roboflow.com/greencoffeebean/greencoffeebeandefectdetection_excelsa)) ซึ่งเป็นพันธุ์ Excelsa/Liberica ใกล้ Robusta มากกว่า Arabica น่าดู
- HF `rasyidf/coffee-beans` (MIT, "Coffee Beans Grading" ภาษาอินโดฯ 4 คลาส 2,000 ภาพ น่าจะเป็น USK อีกชุด)
- ข้อมูล spectral (ไม่ใช่ภาพ, ใช้ไม่ได้กับ pipeline นี้): Mendeley [dtd2fggpyp](https://data.mendeley.com/datasets/dtd2fggpyp) (ATR-FTIR)
- **ไม่พบ** dataset ภาพสารกาแฟบน Zenodo, figshare หรือ IEEE DataPort

### 2.3 Cherry ripeness (pain point: รูดทั้งช่อ ทำให้ผลสุกไม่เท่ากัน)

- **C1** https://www.kaggle.com/datasets/cienciacafeto/coffee-fruit-maturity (CC BY-NC 4.0) มี 859 ภาพ และ 11,044 mask (unripe 8,207, ripe 1,428, semi_dry 874, dry 301, overripe 234) เป็นภาพบนต้น พื้นหลังธรรมชาติ ข้อมูลเอียงไปทาง unripe มาก
- **C2** https://universe.roboflow.com/naromu-eskfw/ripeningcoffee (CC BY 4.0, 859 ภาพ v2 อาจเป็นชุดเดียวกับ C1) และ **C3** https://universe.roboflow.com/mckenzhie/coffee-cherry-mtae4 (4 คลาส ripe/overripe/semi-ripe/unripe)
- **C4** https://www.kaggle.com/datasets/harisyunanda/dataset-coffee-cherry (YOLO 3 คลาส; คำอธิบายบอก 1,000 ภาพ แต่ listing เห็น 432 ซึ่งไม่ตรงกัน)
- **C5** https://www.kaggle.com/datasets/luisdanielc/coffee-cherry-maturity-instance-segmentation (YOLO-seg 675 ภาพ)
- **C6** https://zenodo.org/record/4914786 เป็น multispectral 15 ช่อง ใช้กับกล้อง RGB ไม่ได้
- **C7** https://huggingface.co/datasets/pjramg/colombian_coffee (COCO, Apache-2.0)
- Brazil harvester (UVa) unripe/ripe-red/ripe-yellow/overripe ([uvadoc](https://uvadoc.uva.es/handle/10324/81785?show=full)) ยังไม่ได้ตรวจ license
- **ข้อจำกัดสำคัญ:** ทุกชุดเป็นผลบนต้นหรือบนกิ่ง ส่วนโจทย์ของเราคือ "ผลที่รูดมากองแล้ว" ถ้าทีมจะทำ ripeness ให้ถ่ายผลเชอร์รี Robusta บนถาดเดียวกับ rig เอง ใช้ pipeline segment→crop→classify เดิม ระดับสีแดง/เหลือง/เขียวของเชอร์รีแยกง่าย แค่ 150–300 crop ต่อคลาสก็น่าจะพอ (เป็นการประมาณ)

### 2.4 Roasted (ทางเลือกสุดท้าย ⚠️ ไม่ใช่สารกาแฟดิบ)
- `sot2542/coffee-bean-dataset-v1` เป็นงานไทยที่ร้าน Bona Coffee, JJ Mall มี 4,800 ภาพ (iPhone 12 mini) แบ่ง 4 ระดับคั่ว ใช้ CC BY-SA 4.0 และมีเวอร์ชันย่อ 224×224 คือ `gpiosenka/coffee-bean-dataset-resized-224-x-224`
- คลาส "green" ในชุดนี้เป็นเมล็ดดิบ Arabica ที่ดี เอามาเสริมคลาส normal ได้นิดหน่อย นอกนั้น **ไม่แนะนำ**

---

## 3. Data Strategy ที่แนะนำ

### 3.1 ชุดที่จะ merge (ลำดับความสำคัญ)
1. **A1 MFU 17-class** เป็นแกนหลักของ taxonomy เพราะภาพเดี่ยว 500 px ตรงกับ crop ของเรา
2. **A2 vicanadya 16-class** ใช้ pretrain แบบ low-res (resize เป็น 96 px) โดยต้อง dedupe และ group-split ตามภาพต้นทาง (`DSCFxxxx`)
3. **A3 Vietnam DataCoffee** เอา bbox มา crop แล้วใช้คลาส MOLD/BROWN/INSECT/BLACK (ถ้ายืนยันว่าเป็น Robusta ให้ให้น้ำหนักสูง)
4. **A5 USK-Coffee** ใช้เป็น normal และ peaberry และเป็น defect generic เฉพาะตอนเทรน binary head
5. **A4 Renies ROBUSTA** ใช้เมื่อดูคลาสแล้วเข้ากันได้
6. ส่งอีเมลขอ **AL-ViT (Robusta ไทย)** และ **Bangladesh (มี Robusta)** ทันที เพราะอาจได้ภายใน 1–3 สัปดาห์

### 3.2 Unified class set (9 คลาส + optional)

ให้ classifier บน Pi ใช้ 9 คลาส ส่วนการคิดคะแนนเกรดแบบ SCA ให้คำนวณใน service layer

| Unified class | A1 MFU / A2 vicanadya (SCA) | A3 Vietnam | A5 USK | A7 Bangladesh | SCA cat. |
|---|---|---|---|---|---|
| `normal` | (Specialty) | – | premium, longberry | normal | – |
| `black` | Full Black, Partial Black* | BLACK, PartlyBlack* | – | black | 1 (full) / 2 (partial) |
| `sour_brown` (สีน้ำตาลแดง/หมัก) | Full Sour, Partial Sour* | BROWN | – | sour | 1 / 2 |
| `faded_pale` (ซีด/ลอยน้ำ/เหี่ยว) | Fade, Floater, Withered | – | – | faded | 2 |
| `broken` (แตก/บิ่น/ตัด/เปลือกหอย) | Broken, Cut, Shell | BROKEN, BigBroken | – | broken | 2 |
| `insect` | Slight Insect, Severe Insect* | INSECT | – | – | 2 / 1 (severe) |
| `mold` | Fungus Damage | MOLD | – | – | 1 |
| `immature` | Immature | IMMATURE | – | – | 2 |
| `husk_foreign` (กะลา/เปลือก/ผลแห้ง/สิ่งแปลกปลอม) | Dry Cherry, Husk/Hull, Parchment, Foreign Matter | (LIGHTFM?) | – | – | 1 (dried cherry, foreign) / 2 (hull, parchment) |
| *(optional)* `peaberry` | – | – | peaberry | peaberry | ไม่ใช่ defect |
| *(ทิ้ง)* `defect` generic | – | MIXED (เป็น tray-level) | defect | – | ใช้แค่ binary pretrain |

\* ถ้าข้อมูลพอ ให้แยก partial/full และ slight/severe เป็น sub-label ไว้ใน metadata เพราะน้ำหนักในการคิดเกรดต่างกันมาก

**การคิดเกรดใน service layer (SCA-style):**
- **Category 1:** full black, full sour, dried cherry/pod, fungus damaged, foreign matter, severe insect damage
- **Category 2:** partial black, partial sour, parchment, floater, immature/unripe, withered, shell, broken/chipped/cut, hull/husk, slight insect damage
- ค่า "full defect equivalent" ของ SCA Arabica ที่ใช้กันทั่วไป (จากความรู้เดิม ⚠️ **ควรตรวจกับเอกสาร SCA ก่อนใช้จริง**):
  - full black 1, full sour 1, dried cherry 1, fungus 1, foreign matter 1, severe insect 2–5
  - partial black 3, partial sour 3, parchment 5, floater 5, immature 5, withered 5, shell 5, broken 5, hull 5, slight insect 10
- สำหรับ Robusta ให้อ้าง **Fine Robusta protocol (CQI/UCDA)** และ **มาตรฐานสารกาแฟไทย (มกษ.)** ซึ่งเกณฑ์ต่างจาก SCA และยังไม่ได้ตรวจในรอบนี้ (มีรีวิวเดือน ก.ย. 2026 ระบุว่ามาตรฐานแต่ละฉบับแปลงค่ากันตรงๆ ไม่ได้ [preprints.org](https://www.preprints.org/manuscript/202609.1283)) ควรเก็บ count ดิบต่อคลาสต่อน้ำหนักตัวอย่างไว้ แล้วให้ service แปลงเป็นเกรดตามมาตรฐานที่ผู้ซื้อเลือก

### 3.3 ภาพที่ทีมต้องถ่ายเอง (สำคัญที่สุด)
- **เหตุผล:** ทุก public dataset ต่างจากของเราทั้งพันธุ์ (Arabica กับ Robusta ต่างกันทั้งสี รูปร่าง และร่อง) กล้อง แสง และพื้นหลัง domain shift แบบนี้มักทำให้ accuracy ตกมาก ดังนั้นอย่าใช้ public test set วัดผล
- **เป้าหมาย:** ≥300 crop ต่อคลาส (ขั้นต่ำ) และ 500+ สำหรับคลาสที่สับสนกันบ่อย (sour_brown / faded_pale / mold / insect / normal) รวมราว **3,000–5,000 crop** และ normal ควรมี 1,000+ เพราะในงานจริงคลาสนี้มีมากที่สุด
- **วิธีที่เร็วที่สุด ("pre-sorted trays"):** ให้ผู้ซื้อ/คัดเกรด หรือคนที่ผ่านการอบรม Q/R-grader คัดเมล็ดแยกตามคลาสก่อน แล้วถ่ายถาดละคลาสบน rig จริง จากนั้น OpenCV จะ crop และ label ตามชื่อถาดให้อัตโนมัติ ถาดละ 50–100 เมล็ด ถ่าย 5–10 ถาดต่อคลาส ใช้เวลาไม่กี่ชั่วโมงก็ได้ข้อมูลหลายพัน crop
- **ให้แน่ใจว่าครอบคลุม:** พลิกเมล็ดทั้งสองด้าน (ด้านร่องกับด้านหลัง), ถ่ายหลาย lot หลายสวน หลายระดับความชื้น, ถ่ายทั้งเมล็ดสดใหม่และเมล็ดที่เก็บไว้นาน
- **Test set:** แยกตาม lot/ถาด ไม่ใช่สุ่ม crop เก็บ 1–2 lot ที่ไม่เคยเห็นไว้ทดสอบ
- **Active learning:** หลังเทรนรอบแรก ให้ทำนายภาพ mixed tray แล้วส่งเมล็ดที่ confidence ต่ำหรืออยู่ไกลจาก cluster เดิมให้คน label (ตามบทเรียนจาก AL-ViT)

### 3.4 Augmentation และการลด domain shift
- **คุม rig ก่อน augment:** ใช้ fixed exposure/WB (ปิด auto) ไฟ LED diffuse ที่ CRI สูง พื้นหลังสีเดียว (ฟ้า/น้ำเงินจะ segment ง่าย และไม่ชนสีเขียว/น้ำตาลของเมล็ด) และวาง **gray card/ColorChecker** ในทุกภาพเพื่อ normalize สีอัตโนมัติ
- **Normalize crop ให้เหมือนกันทุก dataset:** mask พื้นหลังเป็นสีเดียวกัน, pad ให้เป็นสี่เหลี่ยมจัตุรัส, resize ด้านยาว และใส่ scale (ขนาดเมล็ด mm/px) เป็น feature เสริมใน service ถ้าทำได้ เพราะ broken/peaberry ดูจากขนาดได้
- **Augment ที่ปลอดภัย:** rotate 0–360°, flip, scale ±15%, perspective เล็กน้อย, Gaussian/motion blur เล็กน้อย, JPEG quality 60–95, noise, brightness/contrast ±20%, gamma, เงาจำลอง
- **Augment ที่ต้องระวัง:** hue shift ให้เล็กมาก (≤±5°) และ saturation ±15% เพราะ **สีคือ signal ของ black/sour/faded/mold** ถ้า jitter สีแรงไปจะทำให้คลาสปนกัน ให้ใช้ white-balance shift (คูณ gain R/B 0.9–1.1) แทน hue jitter
- **Background replacement:** เอา crop จาก public dataset มาวางบนพื้นหลังและแสงแบบ rig ของเรา (copy-paste) เพื่อสร้างภาพถาดสังเคราะห์สำหรับทดสอบ segmentation
- **ลำดับการเทรน:**
  1. ImageNet-pretrained MobileNetV3/YOLO-cls
  2. เทรนบน public data ที่ map แล้ว
  3. fine-tune บนข้อมูลของเรา (LR ต่ำ, unfreeze ทีละชั้น)
  4. ทำ calibration (temperature scaling) แล้วกำหนด threshold "unknown" ให้คนตรวจซ้ำ
- **Class imbalance:** ใช้ weighted sampler หรือ focal loss และรายงานผลเป็น per-class recall ไม่ใช่แค่ accuracy

### 3.5 แหล่งซื้อสาร Robusta ชุมพร (รวมเมล็ดเสีย/ตกเกรด)
⚠️ รอบนี้**ไม่พบ**ร้านออนไลน์ที่ยืนยันได้ว่าขายสาร Robusta ชุมพรพร้อมราคาปัจจุบัน ข้อมูลข้างล่างจึงเป็นแนวทาง ยังไม่ได้ตรวจทีละร้าน
- **Shopee / Lazada:** ค้นคำว่า "สารกาแฟ โรบัสต้า ชุมพร", "สารกาแฟดิบ ท่าแซะ", "Fine Robusta ชุมพร" แล้วเลือกร้านที่ระบุแหล่ง อำเภอ ปีผลิต และวิธีแปรรูป (dry/natural, honey, washed) ให้ซื้อหลายร้านเพื่อให้ได้ความหลากหลาย
- **ขอ "เมล็ดตกเกรด/หางเครื่องคัด/เมล็ดเสีย":** ร้านคัดสารและโรงสีในท่าแซะ สวี หลังสวน และปะทิวมักมีเมล็ดที่ถูกคัดออก ซึ่งเป็น defect จริงจาก Robusta ชุมพร (ทองคำของ dataset) ควรขอแยกตามชนิดถ้าทำได้
- **หน่วยงาน:**
  - ศูนย์วิจัยพืชสวนชุมพร กรมวิชาการเกษตร เจ้าของพันธุ์ ชุมพร 2, 84-4 และ กวก.ชุมพร 1 ([เอกสารพันธุ์](https://www.doa.go.th/hort/wp-content/uploads/2025/01/กาแฟโรบัสตาพันธุ์-กวก.ชุมพร-1.pdf), [คู่มือ 2567](https://www.doa.go.th/hort/wp-content/uploads/2025/01/คู่มือเทคโนโลยีการผลิตกาแฟโรบัสตา-2567.pdf))
  - สำนักงานเกษตรจังหวัดชุมพร
  - วิสาหกิจชุมชน/สหกรณ์กาแฟ เช่น กลุ่มกาแฟบ้านถ้ำสิงห์ อ.เมืองชุมพร (ยังไม่ยืนยันว่าขายสาร)
  - เครือข่ายผู้ผลิต Robusta ชุมพร ที่ได้ทุน บพท. ร่วมกับ มทร.กรุงเทพ ([Thai Post](https://www.thaipost.net/news-update/929978/))
- **ระหว่างค่ายที่ KMITL ชุมพร:** ขอตัวอย่างจากผู้จัดหรือสวนในพื้นที่ แล้วถ่ายเพิ่มบน rig จริงในสภาพแสงและความชื้นของสนาม
- อ้างอิงราคา: ข่าวปี 2566 ระบุว่าเกษตรกรขายโรงงานเฉลี่ยราว 70 บาท/กก. ([Thai Post](https://www.thaipost.net/news-update/929978/)) ตัวเลขนี้เก่าแล้ว อย่าใช้เป็นราคาปัจจุบัน

### 3.6 Action items (เรียงตามความเร่ง)
1. ดาวน์โหลด A1, A3 และ A2 ผ่าน Kaggle CLI (ต้องมี `~/.kaggle/kaggle.json`) แล้วเปิดดูภาพ A3 เพื่อยืนยันว่าเป็น Robusta
2. เปิด Roboflow Renies Workspace ด้วย browser เพื่อดูคลาส แล้ว export เป็น `folder` หรือ `yolov8`
3. ส่งอีเมลขอข้อมูล 3 ฉบับ: AL-ViT (Mahidol/KMUTT), sujitra.arw@mfu.ac.th (ขออนุญาตใช้ A1 และถามว่ามี Robusta ไหม), hlgope@sau.ac.bd (ขอส่วน Robusta)
4. สร้าง rig ถ่ายภาพให้เสร็จก่อน แล้วซื้อสาร Robusta ชุมพร 2–3 แหล่ง รวม "หางเครื่องคัด" ด้วย จากนั้นเริ่ม pre-sorted tray protocol
5. เขียน `class_map.yaml` ตามตาราง 3.2 และ script crop/dedupe/group-split

---

### Sources (หลัก)
- Kaggle API metadata/file listings (ตรวจ 10 ต.ค. 2026): ลิงก์ Kaggle ทั้งหมดในตาราง
- AL-ViT: https://kirim.kmutt.ac.th/converis/portal/detail/Publication/1532355937?lang=en_GB · https://repository.li.mahidol.ac.th/handle/123456789/114424
- MFU IJSIT 2025: https://ph01.tci-thaijo.org/index.php/IJSIT/article/download/260481/174216/1007771
- Bangladesh: https://www.aimspress.com/article/doi/10.3934/agrfood.2025050 · https://www.nature.com/articles/s41598-024-78598-7
- Telkom: https://btp.telkomuniversity.ac.id/landing/ip/HCNA2002256278
- Zenodo: https://zenodo.org/record/4914786
- Hugging Face API: https://huggingface.co/datasets/duvdar/usk-coffee · https://huggingface.co/datasets/pjramg/colombian_coffee · https://huggingface.co/datasets/rasyidf/coffee-beans
- Roboflow (V-search เท่านั้น): https://universe.roboflow.com/renies-workspace และลิงก์อื่นในตาราง
- กรมวิชาการเกษตร: https://doa.go.th/plan/wp-content/uploads/2023/08/843การจัดชั้นคุณภาพของเมล็ดกาแฟโดยใช้วิธีทางกายภาพและประสาทสัมผัส.pdf
