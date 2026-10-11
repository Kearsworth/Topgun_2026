# 02 — Vision Node บน Raspberry Pi 5 (CPU-only) สำหรับเมล็ดกาแฟสาร Robusta

> TESA Top Gun Rally #20 — "Chumphon Robusta AIoT Platform – Toward the Next-Gen Market"
> เอกสารวิจัยเชิงวิศวกรรม (ร่างที่ 1, 10 ต.ค. 2026) — ตัวเลขที่ไม่ได้ยืนยันจากแหล่งปฐมภูมิจะติดป้าย **[ยังไม่ยืนยัน]** หรือ **[ประมาณการ]**
> โค้ดทั้งหมดในเอกสารนี้ **ยังไม่ได้ทดสอบ (UNTESTED)** — ใช้เป็นโครงเริ่มต้นแล้วปรับแก้เอง

---

## 0. Executive Summary (อ่านส่วนนี้ก่อน)

1. **ปัญหานี้ไม่ใช่ปัญหา AI เป็นหลัก แต่เป็นปัญหาแสงและการแยกเมล็ด**: ถ้าแสงคงที่และแยกเมล็ดได้สะอาด classifier ตัวเล็กมากก็พอ แต่ถ้าแสงแกว่งหรือเมล็ดติดกัน โมเดลไหนก็ช่วยไม่ได้ ควรใช้เวลา 60% ไปกับ light box, การล็อกกล้อง และ segmentation
2. **กล้องที่แนะนำคือ Camera Module 3 (standard, 12MP, IMX708)** วางสูงจากถาดประมาณ 22–25 ซม. แล้ว**ล็อกโฟกัสด้วย `LensPosition`** ที่ระยะนี้จะได้ประมาณ 15–16 px/mm และเมล็ดกว้าง 6–7 มม. จะกินพื้นที่ประมาณ 100 px ซึ่งพอสำหรับวัดขนาดระดับ 1/64 นิ้ว (0.4 มม. ≈ 6 px) **[ประมาณการจาก FoV ทางการ]** ส่วน HQ Camera + เลนส์ 6 มม. เป็นตัวเลือกสำรองที่ดี ไม่แนะนำ Global Shutter (1.6MP ละเอียดไม่พอ) และ USB webcam (ล็อก exposure/WB ยาก)
3. **ต้องล็อกทุกอย่าง** ได้แก่ `AeEnable=False`, `AwbEnable=False`, `ExposureTime`, `AnalogueGain`, `ColourGains`, `AfMode=Manual` และ `LensPosition` (หน่วยเป็น dioptre = 1/ระยะเป็นเมตร) ค่าทั้งหมดได้จากการ calibrate ครั้งเดียวด้วย gray card แล้วเก็บไว้ในไฟล์ config
4. **Light box**: ใช้ LED CRI ≥ 90 (ถ้าได้ 95+ ยิ่งดี) 5000–5600 K ส่องแบบอ้อมหรือผ่าน diffuser ผนังด้านในเป็นสีขาวด้าน **พื้นหลังแนะนำสีน้ำเงินด้าน** (แยกด้วยช่อง b* ของ Lab ได้ง่าย) หรือดีกว่านั้นคือ **backlight (แผ่น LED tracing pad ใต้ถาดอะคริลิกขุ่น)** ถ่าย 2 ช็อต ช็อตแรกเปิด backlight เพื่อทำ mask ช็อตที่สองเปิดไฟบนเพื่อเก็บสี **ห้ามใช้พื้นหลังสีดำ** เพราะเมล็ดดำ (black bean) จะกลืนไปกับพื้น
5. **Segmentation**: ใช้ Otsu แล้วตามด้วย morphology, distance transform, `peak_local_max` และ watershed ให้ทำบนภาพที่ย่อ 0.5× เพื่อความเร็ว แล้วค่อยขยาย label กลับไปวัดและ crop บนภาพเต็ม ก้อนที่ใหญ่กว่า 1.6× ของพื้นที่มัธยฐานให้ flag เป็น clump แล้วประมาณจำนวนจากพื้นที่ วิธีที่ช่วยได้มากที่สุดคือ**กระจายเมล็ดไม่ให้ติดกัน** (เขย่าถาด หรือใช้ถาดแบบหลุม)
6. **การวัด**: วาง ArUco marker ขนาดรู้ค่า (เช่น 30 มม.) อย่างน้อย 2 อันบนระนาบถาด แล้ว calibrate distortion ครั้งเดียวด้วย checkerboard แปลงความกว้างเมล็ดเป็น screen size ด้วย `screen = floor(width_mm / 0.396875)` (screen 18 = 18/64" = 7.14 มม.) แต่**ต้อง calibrate ความสัมพันธ์นี้กับตะแกรงจริง** เพราะความกว้างที่เห็นจากด้านบนไม่เท่ากับมิติที่ลอดรูกลมพอดี
7. **Classifier ค่าเริ่มต้น**: ใช้ **Ultralytics YOLO26n-cls (หรือ YOLO11n-cls) ที่ imgsz=128** export เป็น **NCNN** บน Pi 5 (ncnn benchmark ทางการ, 4 threads, 224px) MobileNetV3 ใช้ 7.35 ms, ShuffleNetV2 ใช้ 3.39 ms, EfficientNet-B0 ใช้ 12.33 ms และ ResNet18 ใช้ 19.96 ms ถ้าถาดมี 300 เมล็ด คาดว่าใช้เวลาจำแนกรวม 1–3 วินาที **[ประมาณการ]** **INT8 บน Pi 5 แทบไม่เร็วขึ้น** (resnet18 เร็วขึ้นจาก 19.96 เป็น 16.74 ms; squeezenet 7.38 เป็น 7.21 ms) จึงใช้ FP32/FP16 ไปเลย ไม่ต้องเสี่ยงความแม่นตก
8. **Training**: ถ่ายรูป**ถาดที่มีเมล็ดคลาสเดียว** (เช่น เทแต่เมล็ดดำลงถาด) แล้วได้ label อัตโนมัติ ซึ่งเร็วกว่าการ annotate มาก แบ่ง train/val/test **ตามถาด/รอบถ่าย** ไม่ใช่ตาม crop **ปิด RandAugment และ hue jitter** เพราะสีคือ feature หลักของ defect ตั้ง `scale` ต่ำเพื่อไม่ให้ random crop ทำให้ขนาดเพี้ยน ควรมีอย่างน้อยประมาณ 300 crop ต่อคลาส (เป้า 1,000+) **[heuristic]**
9. **งานวิจัยที่ตีพิมพ์**: accuracy 94–99% บนข้อมูล Arabica/Bangladesh ที่สะอาด แต่คลาสที่ขึ้นกับสี (sour/faded) มักต่ำสุด (Pinto 2017 ได้ 72.4–98.7% ต่อคลาส) งานบน Raspberry Pi 3 ทำได้ 98.19% ที่ 13.77 ภาพ/วินาที แต่เป็นงาน binary (peaberry หรือ normal) ที่ 64×64 px
10. **Thermal/Power**: ต้องใช้ Active Cooler และ PSU 27W (5V/5A) ถ้าใช้ 3A พอร์ต USB จะถูกจำกัดไว้ที่ 600 mA CPU จะเริ่ม throttle ที่ 80°C และลดหนักที่ 85°C ให้ใส่ `vcgencmd get_throttled` ลงใน payload ทุกครั้ง **ห้าม overclock ในวันแข่ง**

### Recommended Default Stack

| Layer | Default | Fallback |
|---|---|---|
| OS | Raspberry Pi OS 64-bit (ทั้งทีมใช้เวอร์ชันเดียวกัน, ตอนนี้ default คือ Trixie; Bookworm = legacy) | Bookworm legacy ถ้า tutorial/แพ็กเกจพัง |
| Camera | Camera Module 3 (standard, IR-cut) สูงประมาณ 22–25 ซม. | HQ Camera + 6 mm CS lens |
| Capture | Picamera2 (apt) ใน venv `--system-site-packages`, ล็อก AE/AWB/AF | `rpicam-still` CLI |
| Light | LED strip CRI≥90 5000–5600K แบบ indirect, กล่องขาวด้าน, backlight pad | Ring diffuser + polarizer |
| Background | Backlight (2-shot) หรือกระดาษ/EVA สีน้ำเงินด้าน | เทาอ่อนด้าน |
| Scale | ArUco DICT_4X4_50, 30 มม. × 2–4 อัน + gray patch ในทุกเฟรม | เหรียญ (ไม่แนะนำ) |
| Segmentation | OpenCV + scikit-image watershed (ทำที่ 0.5×) | YOLO-seg / StarDist (ถ้าจำเป็น) |
| Classifier | YOLO26n-cls / YOLO11n-cls @128 → NCNN | MobileNetV3-small (timm) → ONNX Runtime |
| Messaging | paho-mqtt 2.x (`CallbackAPIVersion.VERSION2`), QoS 1, LWT | — |
| Hardware | Pi 5 (4GB+ ), Active Cooler, PSU 27W, ไฟ LED ใช้แหล่งจ่ายแยก | — |

---

## 1. กล้องสำหรับ Raspberry Pi 5

### 1.1 สเปกทางการ

ข้อมูลจาก Raspberry Pi Camera documentation (https://www.raspberrypi.com/documentation/accessories/camera.html)

| รุ่น | Sensor | ความละเอียด | Pixel | Focal | HFoV × VFoV | โฟกัส | Min focus |
|---|---|---|---|---|---|---|---|
| Camera Module 3 | IMX708 | 4608×2592 (11.9MP) | 1.4 µm | 4.74 mm | 66° × 41° | Motorised (PDAF) | ~10 ซม. |
| Camera Module 3 Wide | IMX708 | 4608×2592 | 1.4 µm | 2.75 mm | 102° × 67° | Motorised | ~5 ซม. |
| HQ Camera | IMX477 | 4056×3040 (12.3MP) | 1.55 µm | ขึ้นกับเลนส์ | ขึ้นกับเลนส์ | ปรับมือ | ขึ้นกับเลนส์ |
| Global Shutter | IMX296 | 1456×1088 (1.58MP) | 3.45 µm | ขึ้นกับเลนส์ | ขึ้นกับเลนส์ | ปรับมือ | ขึ้นกับเลนส์ |
| AI Camera (IMX500) | IMX500 | 4056×3040 | 1.55 µm | 4.74 mm | 66° × 52° | ปรับมือ | ~20 ซม. |

> หมายเหตุ: AI Camera (IMX500) มี NPU อยู่ในตัว ซึ่ง**น่าจะเข้าข่าย "AI accelerator" ที่กติกาห้าม** ไม่ควรใช้ (ถ้าจะใช้ต้องยืนยันกับกรรมการในวันงานก่อน)
> Pi 5 ใช้สาย **22-pin mini (Standard–Mini cable)** เสียบที่ CAM/DISP0 หรือ CAM/DISP1 ได้ทั้งคู่ ควรสั่งสายยาว 300 มม. เผื่อไว้ เพราะสายสั้นที่ติดมากับกล้องมักไม่พอสำหรับ light box

### 1.2 เรขาคณิตสำหรับถาด 20×15 ซม. **[ประมาณการ คำนวณจาก FoV ทางการ]**

ความกว้างของภาพที่ระยะ d คือ `2·d·tan(HFoV/2)`

| ตัวเลือก | ระยะกล้องถึงถาด | พื้นที่ครอบคลุม (H×V) | px/mm | ความกว้างเมล็ด 6.5 มม. (px) | 1 screen (0.397 มม.) (px) |
|---|---|---|---|---|---|
| CM3 standard | 22 ซม. | ~28.6 × 16.4 ซม. | ~16.1 | ~105 | ~6.4 |
| CM3 standard | 25 ซม. | ~32.5 × 18.7 ซม. | ~14.2 | ~92 | ~5.6 |
| HQ + เลนส์ 6 mm (sensor ~6.29×4.71 mm) | 25 ซม. | ~26 × 19.6 ซม. | ~15.6 | ~101 | ~6.2 |
| Global Shutter + 6 mm | 25 ซม. | ~? (sensor ~5.0×3.8 mm) ~21×16 ซม. | ~7 | ~45 | ~2.8 |
| USB webcam 1080p | — | ~26 ซม. กว้าง | ~7.4 | ~48 | ~2.9 |

**ข้อสรุป**
- ด้าน V ของ CM3 (41°) เป็นตัวจำกัด ถ้าต้องการให้ถาด 15 ซม. อยู่ในภาพทั้งหมด ต้องวางกล้องสูงอย่างน้อยประมาณ 20 ซม. ใช้ **22–25 ซม.** จะมีที่ว่างสำหรับ ArUco และ gray patch ที่ขอบ
- **CM3 standard** ดีที่สุดในแง่ราคา ความง่าย และโฟกัสที่ล็อกด้วยซอฟต์แวร์ได้ ส่วน CM3 Wide มี distortion สูงกว่า (102°) ไม่จำเป็นต้องใช้
- **HQ + 6 mm** ให้คุณภาพดีพอกัน แต่เลนส์ 6 mm ราคาถูกมี barrel distortion มาก ต้อง undistort และต้องตั้งโฟกัสกับรูรับแสงด้วยมือแล้วล็อกด้วยสกรู
- **Global shutter**: ถาดอยู่นิ่ง จึงไม่ได้ประโยชน์จาก global shutter และความละเอียดไม่พอสำหรับ texture/defect เล็ก ๆ อย่างรูแมลงเจาะ
- **USB webcam**: ส่วนใหญ่ล็อก AWB/exposure ผ่าน v4l2 ได้ไม่เสถียร บางรุ่นเป็น fixed focus ที่ระยะไกล ให้ใช้เป็น backup ฉุกเฉินเท่านั้น
- Depth of field ไม่ใช่ปัญหา เพราะเมล็ดหนาประมาณ 3–5 มม. และระนาบถาดแบน

### 1.3 Picamera2: ติดตั้งและล็อกค่าเพื่อให้สีซ้ำได้

ข้อเท็จจริงจาก Picamera2 manual (https://pip.raspberrypi.com/documents/RP-008156-DS-1-picamera2-manual.pdf)
- `LensPosition` มีหน่วยเป็น **dioptre (1/ระยะเป็นเมตร)** ค่า 0 = infinity ดังนั้นที่ 22 ซม. ≈ **4.5** และที่ 25 ซม. = **4.0** ให้ตั้ง `AfMode: controls.AfModeEnum.Manual` คู่กันไปด้วย ส่วน `picam2.camera_controls['LensPosition']` จะคืนค่า (min, max, default)
- `AeEnable=False` ปิด AEC/AGC; `AwbEnable=False` ปิด AWB; `ColourGains=(red_gain, blue_gain)` มีช่วง 0.0–32.0 และ**การตั้งค่านี้จะปิด AWB ให้เอง**
- ตัวอย่าง `controls.py` ในคู่มือใช้แนวทาง "อ่าน ExposureTime/AnalogueGain/ColourGains ตอนที่ค่า auto นิ่งแล้ว จากนั้น fix ค่าไว้"
- **venv ต้องสร้างด้วย `python -m venv --system-site-packages my-env`** เพราะ libcamera Python bindings ไม่มีบน PyPI
- HDR ของ CM3 ต้องเปิด/ปิดก่อนเปิด Picamera2 (ค่า default ปิดอยู่ ให้คงไว้แบบนั้น)

**ขั้นตอน calibrate กล้อง (ทำครั้งเดียวต่อ setup แล้วบันทึกลง `camera.json`)**
1. วาง gray card หรือแผ่นขาวด้านกลางถาด เปิดไฟ light box ทิ้งไว้ 10 นาทีให้อุณหภูมิ LED นิ่ง
2. ตั้ง AF เป็น Auto แล้วสั่ง `autofocus_cycle()` จากนั้นอ่าน `LensPosition` จาก metadata และจดค่าไว้ (หรือ sweep ค่า 3.5–5.5 แล้วเลือกค่าที่ variance of Laplacian บน ArUco สูงสุด)
3. ปล่อย AE/AWB ทำงานอัตโนมัติประมาณ 2 วินาที แล้วอ่าน `ExposureTime`, `AnalogueGain`, `ColourGains`
4. ปรับ ExposureTime ให้**เป็นจำนวนเท่าของ 10,000 µs** (ไฟบ้านไทย 50 Hz ทำให้ LED แบบ AC/PWM กระพริบ 100 Hz และ rolling shutter จะเกิดแถบมืด) **AnalogueGain ให้ใกล้ 1.0** เพื่อลด noise และปรับให้พิกเซลของ gray card อยู่ประมาณ 110–130/255 ไม่ให้ clip
5. ปรับ `ColourGains` จนค่า R≈G≈B บน gray card (หรือใช้ค่าจาก AWB เป็นจุดเริ่มต้น)
6. บันทึกค่าทั้งหมด ทุกครั้งที่ capture ให้ตรวจ metadata ว่าค่าตรงกับที่ตั้งไว้ (QA)

ทดสอบเร็วด้วย CLI:
```bash
rpicam-still --autofocus-mode manual --lens-position 4.5 \
  --shutter 20000 --gain 1.0 --awbgains 1.8,1.6 --denoise cdn_off \
  -o test.jpg --immediate
```

**ข้อควรระวัง**
- ใน Picamera2 format `"RGB888"` จะได้ array ที่**เรียงแบบ BGR** ซึ่งตรงกับ OpenCV ใช้ได้ทันที (ตามคำอธิบาย format ในคู่มือ) **[ควรตรวจด้วยการถ่ายวัตถุสีแดง]**
- Saturation/Contrast/Sharpness ให้คงค่า default (1.0) และอย่าเปลี่ยนระหว่างเก็บ dataset กับวันแข่ง
- RAW/DNG ให้สีที่ควบคุมได้ดีที่สุด แต่ต้อง demosaic และ color-correct เอง ซึ่งซับซ้อนเกินไปสำหรับเวลาที่มี ให้ใช้ RGB จาก ISP ที่ล็อกค่าแล้ว แล้วทำ gray-patch normalization ซ้ำทุกเฟรม

### 1.4 ติดตั้งแพ็กเกจบน Pi (Bookworm/Trixie 64-bit) และปัญหาที่พบบ่อย

```bash
sudo apt update && sudo apt full-upgrade -y
sudo apt install -y python3-picamera2 python3-opencv python3-venv   # Lite image: add --no-install-recommends
python3 -m venv --system-site-packages ~/venv-vision
source ~/venv-vision/bin/activate
pip install -U pip
pip install "paho-mqtt>=2.0" scikit-image ultralytics      # ultralytics pulls torch (large, ~several hundred MB)
# Optional lightweight path (no torch at runtime):
pip install onnxruntime ncnn
```

**ปัญหาที่พบบ่อย (จากชุมชน)**
- **`ValueError: numpy.dtype size changed, may indicate binary incompatibility`**: เกิดเมื่อ pip ติดตั้ง numpy 2.x ลงใน venv ทับ numpy ของระบบ ซึ่ง `simplejpeg`/`picamera2` จาก apt ถูก compile ไว้กับ numpy 1.x วิธีแก้ที่มีคนรายงานว่าใช้ได้คือ `pip install -U simplejpeg` หลังติดตั้ง ultralytics หรือ pin `numpy<2` ใน venv (https://github.com/raspberrypi/picamera2/issues/218, https://community.ultralytics.com/t/installation-of-yolo-creates-problems-with-dronekit-python-flight-scripts-on-raspberry-pi/1283)
- **อย่า `pip install opencv-python` ซ้อนกับ `python3-opencv`** ถ้าจำเป็นต้องใช้ pip ให้ใช้ `opencv-contrib-python-headless` (ต้องใช้ contrib ถ้าจะใช้ `cv2.mcc` ตรวจ ColorChecker)
- **`ModuleNotFoundError: libcamera._libcamera`**: มักเกิดจากสร้าง venv โดยไม่ใส่ `--system-site-packages` หรือใช้ Python คนละเวอร์ชันกับระบบ (เช่น conda/pyenv)
- Raspberry Pi OS ตอนนี้มี Trixie เป็น default แล้ว ส่วน tutorial หลายตัวยังอิง Bookworm (https://forum.core-electronics.com.au/t/how-to-set-up-yolo-computer-vision-on-a-raspberry-pi-conda-ultralytics/23803) **ทั้งทีมต้องใช้ image เดียวกัน**, `pip freeze > requirements-pi.txt` และ**โคลน SD card สำรองไว้ 1 ใบก่อนวันแข่ง**
- Ultralytics export เป็น LiteRT (`.tflite`) ได้เฉพาะบน Linux x86_64 หรือ macOS ส่วน NCNN export บน laptop แล้ว copy โฟลเดอร์ไปที่ Pi ได้เลย (https://docs.ultralytics.com/guides/raspberry-pi)

---

## 2. Light Box

### 2.1 หลักการ
- **แสงกระจาย (diffuse) จากหลายทิศ** ช่วยลดเงาและ specular highlight จากผิวเมล็ด/ซิลเวอร์สกิน
- **CRI ≥ 90 (เป้า 95+), 5000–5600 K** CRI ต่ำทำให้สเปกตรัมขาดช่วงแดง/เหลือง จนแยก sour (น้ำตาลแดง) กับ faded (ซีด) ได้ยาก งาน buckwheat ที่ใช้ studio box ใช้ไฟ 5500–5600 K, LED board ด้านหลัง และพื้นสีน้ำเงินสำหรับ chroma-key พร้อม color tag ในทุกภาพ (https://www.frontiersin.org/articles/10.3389/fpls.2020.581546/full) ตัวเลข CRI ข้างต้นเป็นแนวปฏิบัติทั่วไปของงานถ่ายภาพสี **[ไม่มีแหล่งที่ระบุเฉพาะงานเมล็ดพืช]**
- **ไฟต้องนิ่ง**: ใช้ LED driver แบบ constant-current DC (ไฟเส้น 12/24V จาก adapter ที่ดี) ไม่ใช้หลอด AC ราคาถูกที่มี PWM/flicker
- **แหล่งจ่ายไฟของ LED ต้องแยกจาก Pi** ไม่ดึงไฟจาก 5V rail ของ Pi

### 2.2 แบบ DIY ราคาถูก (แนะนำ)
```
           [Pi5 + CM3]  ← รูกล้องกลางฝา, สูง ~22–25 ซม. จากถาด
    ┌───────────────────────────────┐
    │  LED strip CRI95 ติดรอบขอบบน    │ ← หันขึ้นเพดาน/ผนัง (indirect) หรืออยู่หลังแผ่น opal acrylic
    │  ผนังด้านใน: foam board ขาวด้าน   │
    │                               │
    │   [ArUco] [gray] [ArUco]      │
    │   ┌─────── tray 20×15 ───────┐ │ ← ถาดอะคริลิกขุ่น (frosted/opal)
    │   └──────────────────────────┘ │
    │   [LED tracing pad A4/A3] (backlight)
    └───────────────────────────────┘   กล่องประมาณ 40×40×35 ซม. ปิดทึบ (กันแสงภายนอก)
```
- **วัสดุ** (ราคาโดยประมาณในไทย **[ประมาณการ]**): foam board ขาว 3–4 แผ่น, LED strip CRI 90+ 5000K 1–2 ม. พร้อม adapter 12V, LED tracing pad A4 (ประมาณ 300–600 บาท), แผ่นอะคริลิกขุ่น 3 มม., ArUco พิมพ์บนกระดาษด้านแล้วเคลือบด้าน (ห้ามเคลือบเงา), gray card 18%
- **Two-shot strategy (แนะนำมาก)**:
  - ช็อต A: **เปิด backlight อย่างเดียว** จะได้ silhouette ของเมล็ดดำสนิทบนพื้นขาว ซึ่ง Otsu แยกได้ง่ายมาก ขอบคม ไม่มีเงา และใช้วัดขนาดได้ดีที่สุด (หลักการเดียวกับงาน Arabidopsis seed-size ที่ใช้ transmitted light แล้ว threshold, และเครื่องคัดเมล็ดเชิงพาณิชย์ที่ใช้ blue back light: https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12128448)
  - ช็อต B: **ปิด backlight แล้วเปิดไฟบน** เพื่อเก็บสีผิวเมล็ดสำหรับคำนวณ Lab และ crop ให้ classifier
  - ควบคุมไฟด้วย GPIO ผ่าน MOSFET module หรือ relay 2 ช่อง ถ้าถาดและกล้องไม่ขยับ mask จากช็อต A จะใช้กับช็อต B ได้ทันที
  - ข้อควรระวัง: ตั้ง exposure แยกให้แต่ละช็อต ถ้าทำแบบนี้ไม่ทัน ให้ใช้แบบ single-shot บนพื้นสีน้ำเงิน
- **พื้นหลัง (กรณี single-shot)**:
  - **น้ำเงินด้าน**: เมล็ดกาแฟสารทุกคลาสมี b* ≥ 0 (โทนเหลือง/เขียวอมเหลือง/น้ำตาล) ส่วนพื้นน้ำเงินมี b* ติดลบมาก จึงแยกด้วย Otsu บนช่อง b* ได้ดี **[เหตุผลเชิงสี ควรตรวจกับเมล็ดจริง]**
  - **ห้ามใช้สีดำ** เพราะ black bean จะกลืนไปกับพื้น และ**ระวังสีขาว** เพราะ faded bean และขอบที่สะท้อนแสงจะกลืนกับพื้น (งาน Gope et al. 2025 ใช้กระดาษขาว แต่ใช้ detector ที่ train มา ไม่ได้ใช้ threshold)
- **Specular highlight**: ถ้ายังมีจุดสะท้อนขาว ให้ใช้ **cross-polarization** คือติด polarizer film หน้า LED และหมุน polarizer หน้าเลนส์ 90° (จะเสียแสงประมาณ 1.5–2 stop **[ประมาณการ]**) หรือเพิ่มระยะ diffuser
- **เงา**: แสง indirect รอบทิศจะให้เงาน้อยมาก และ backlight จะลบเงาบนพื้นได้ทั้งหมด

### 2.3 Color calibration
- **ทุกเฟรม**: วาง **gray patch** (gray card 18% ตัดชิ้นเล็ก) ที่ตำแหน่งคงที่บนถาด แล้วคำนวณ per-channel gain = target / mean(gray patch) และคูณทั้งภาพ วิธีนี้ชดเชย drift ของ LED ตามอุณหภูมิและอายุการใช้งานได้ ให้ log ค่า mean ของ gray ไว้เป็น health metric และตั้ง alert ถ้า ΔE > 3 **[threshold ตั้งเอง]**
- **ครั้งเดียวต่อ setup (ถ้ามีเวลา)**: ถ่าย **ColorChecker 24 patch** แล้วใช้ OpenCV `mcc` (ต้องใช้ opencv_contrib) เพื่อตรวจ chart จากนั้นใช้ `ccm.ColorCorrectionModel(src, COLORCHECKER_Vinyl)` → `run()` → `infer()` input ต้องเป็น **RGB ช่วง [0,1]** ไม่ใช่ BGR (https://docs.opencv.org/4.x/d1/dc1/tutorial_ccm_color_correction_model.html) ColorChecker ปลอมราคาถูกมีค่าอ้างอิงไม่ตรงมาตรฐาน ให้ใช้เพื่อความ "สม่ำเสมอ" ไม่ใช่ความ "ถูกต้องสัมบูรณ์"
- **หลักการสำคัญ**: ต้องใช้ pipeline สีชุดเดียวกันทั้งตอนเก็บ dataset, train และวันแข่ง ถ้าเปลี่ยน LED, ระยะ หรือค่ากล้อง ต้องเก็บ golden tray ใหม่และตรวจว่าโมเดลยังแม่นอยู่

---

## 3. Segmentation เมล็ดที่ติดกัน

### 3.1 Recipe มาตรฐาน (OpenCV + scikit-image)
อ้างอิง: OpenCV watershed tutorial (https://docs.opencv.org/4.x/d3/db4/tutorial_py_watershed.html), distance-transform tutorial (https://docs.opencv.org/3.4.1/d2/dbd/tutorial_distance_transform.html)

1. **ย่อภาพ 0.5×** (12MP เหลือ 3MP; ความละเอียดยังเหลือประมาณ 8 px/mm ซึ่งพอสำหรับ mask)
2. Threshold:
   - backlight: ใช้ gray แล้ว `THRESH_BINARY_INV + OTSU`
   - พื้นน้ำเงิน: ใช้ช่อง b* ของ Lab แล้ว `GaussianBlur(5)` → `THRESH_BINARY + OTSU`
3. `morphologyEx(OPEN, ellipse 5×5)` เพื่อลบ noise แล้วตามด้วย `CLOSE` และ **fill holes** (ร่องกลางเมล็ด center-cut อาจทำให้เกิดรูใน mask)
4. ลบ component ที่เล็กกว่า 0.25 × พื้นที่เมล็ดที่คาดไว้ (ฝุ่น, เศษ)
5. `dist = cv2.distanceTransform(mask, DIST_L2, 5)` แล้ว `GaussianBlur` เล็กน้อยเพื่อลด peak ซ้อนบนเมล็ดยาว
6. `peak_local_max(dist, min_distance≈0.35×ความกว้างเมล็ด(px), threshold_abs≈0.3×ครึ่งความกว้าง, labels=cc, exclude_border=False)` จะได้ 1 marker ต่อเมล็ด
7. `skimage.segmentation.watershed(-dist, markers, mask=mask)` หรือ `cv2.watershed` (ต้องใช้ภาพ 3 ช่องและ marker แบบ int32 ที่มี unknown = 0)
8. ขยาย label กลับเป็นขนาดเต็มด้วย `INTER_NEAREST` แล้ววัดและ crop บนภาพเต็ม

### 3.2 พารามิเตอร์และปัญหาที่พบบ่อย
- **Over-segmentation** (เมล็ดยาวถูกแบ่งเป็น 2 ส่วน): ให้เพิ่ม `min_distance`, blur ค่า dist มากขึ้น หรือใช้ h-maxima (`skimage.morphology.h_maxima`) ส่วนเมล็ด Robusta ค่อนข้างกลมจึงเกิดปัญหานี้น้อยกว่า Arabica **[ยังไม่ยืนยัน]**
- **Under-segmentation** (3–4 เมล็ดเป็นก้อนเดียว): ถ้าก้อนมีพื้นที่ > 1.6× median → flag `clump` แล้วประมาณจำนวนด้วย `round(area/median_area)` นับเข้า bean_count แต่**ไม่นำไปคำนวณ size distribution**
- **Broken bean** (เมล็ดแตก) มีพื้นที่เล็ก อย่าตั้ง min_area สูงจนตัดทิ้ง ใช้ประมาณ 0.25× ของเมล็ดปกติ
- **ArUco/gray patch** ต้องถูก mask ออก (ระบุ ROI ของถาดไว้ใน config)
- **วิธีแก้ปัญหาทางกายภาพได้ผลกว่าวิธีทางอัลกอริทึม**: ให้เขย่าหรือใช้ "ปาด" กระจายเมล็ดเป็นชั้นเดียว ถาด 20×15 ซม. ใส่เมล็ดได้ประมาณ 200–350 เมล็ดแบบไม่ซ้อนกัน **[ประมาณการ]** หรือทำถาดแบบหลุม (laser-cut/3D print หลุม ~12 มม.) ซึ่งทำให้ segmentation แทบไม่มีโอกาสผิดเลย แต่ใช้เวลาวางเมล็ดนานกว่า

### 3.3 ทางเลือก: โมเดล segmentation ขนาดเล็ก (เฉพาะกรณีจำเป็น)
- **YOLO26n-seg / YOLO11n-seg**: detection แบบ YOLO26n ที่ 640px บน Pi 5 ใช้ NCNN ประมาณ 67 ms/ภาพ (ตาราง Ultralytics Pi 5; ไม่ชัดว่าเป็น n หรือ s) seg จะช้ากว่านั้น ถ้าใช้กับภาพ 12MP ต้องตัด tile 640 ประมาณ 20–30 tile จะใช้เวลาประมาณ 2–4 วินาทีต่อถาด **[ประมาณการ]** ซึ่งรับได้เพราะงานนี้ไม่ใช่ real-time แต่ต้อง annotate polygon เอง (หรือใช้ mask จาก OpenCV เป็น pseudo-label)
- **StarDist** (star-convex polygons) เหมาะกับวัตถุรูปไข่ที่ติดกันอย่างเมล็ดกาแฟ ทำงานบน CPU ได้ แต่ต้องใช้ TensorFlow ซึ่งติดตั้งบน Pi ได้ยากกว่า **[ไม่ได้ทดสอบ]**
- **คำแนะนำ**: เริ่มจาก OpenCV ก่อน ถ้าวัดแล้ว count error > 2% บน golden tray ค่อยพิจารณา YOLO-seg

---

## 4. การวัดขนาดและ Screen Size

### 4.1 px → mm
- **ArUco** (OpenCV ≥ 4.7 API): `dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)`, `det = cv2.aruco.ArucoDetector(dict, cv2.aruco.DetectorParameters())`, `corners, ids, _ = det.detectMarkers(gray)` (https://docs.opencv.org/4.12.0/d5/dae/tutorial_aruco_detection.html) แล้วคำนวณ `px_per_mm = mean(ความยาวขอบ 4 ด้าน)/marker_mm`
- ใช้ **2–4 markers ที่มุมถาด**: เฉลี่ย scale และตรวจความเอียงของกล้อง (ถ้าค่า px/mm ระหว่าง marker ต่างกันเกิน 1% แปลว่ากล้องเอียง ให้ใช้ homography จาก 4 marker ทำ perspective-rectify)
- **ตรวจขนาด marker ที่พิมพ์ด้วย caliper** เพราะเครื่องพิมพ์มัก scale ผิด 1–3%
- **เหรียญ** (เช่น 10 บาท) ใช้ได้แต่ขอบสะท้อนแสงและหาได้ยากกว่า ไม่แนะนำ
- **ความหนาของเมล็ด**: ผิวบนเมล็ดอยู่สูงกว่าระนาบถาดประมาณ 4 มม. ที่ระยะ 220 มม. ทำให้ขนาดเพี้ยนประมาณ 1.8% **[คำนวณ]** แต่ขอบ silhouette ส่วนใหญ่อยู่ใกล้ระนาบถาด จึงรับได้ และ calibration กับตะแกรงจริง (4.3) จะชดเชยส่วนนี้ให้

### 4.2 Lens distortion
- Calibrate ครั้งเดียวด้วย checkerboard หรือ ChArUco ประมาณ 15–25 ภาพทุกมุมของ FoV ผ่าน `cv2.calibrateCamera` แล้วบันทึก `K, dist` ลง `calib.npz`
- ตอนรันไม่จำเป็นต้อง undistort ทั้งภาพ 12MP (ช้า) ให้ใช้ `cv2.undistortPoints` กับ contour points เฉพาะตอนวัด หรือใช้ `initUndistortRectifyMap` ครั้งเดียวแล้ว `remap` (เร็ว)
- CM3 standard มี distortion ปานกลาง ส่วน HQ + 6 mm มี barrel ชัดเจน **ต้อง**ทำ calibration

### 4.3 Coffee screen size → เกรดการค้า
- **Screen N = รูกลมเส้นผ่านศูนย์กลาง N/64 นิ้ว** (1/64" = 0.396875 มม.) เช่น screen 18 = 7.14 มม. (https://coffeeresearch.org/coffee/beansize.htm, https://driftaway.coffee/coffee-grades/; FAO ปัดเป็น 7 มม.: https://www.fao.org/4/x6939e/X6939e13.htm)
- **เมล็ดที่ค้างบนตะแกรง N ได้เกรด screen N** (ไม่ใช่ตะแกรงที่เมล็ดลอดผ่าน) ส่วน SCA อนุโลมให้คลาดเคลื่อนได้ประมาณ 5%
- **Robusta มักใช้ screen เลขคี่** (13, 15, 17…) ส่วน Arabica มักใช้เลขคู่ (coffeeresearch.org)

| Screen | นิ้ว | มม. | ชื่อเรียกทั่วไป |
|---|---|---|---|
| 20 | 20/64 | 7.94 | Very large / Elephant |
| 18 | 18/64 | 7.14 | Large (AA, Supremo) |
| 17 | 17/64 | 6.75 | |
| 16 | 16/64 | 6.35 | Medium (Excelso, AB) |
| 15 | 15/64 | 5.95 | |
| 14 | 14/64 | 5.56 | Small |
| 13 | 13/64 | 5.16 | |
| 12 | 12/64 | 4.76 | |

- **มาตรฐานไทย**: มกษ. 5700-2552 เมล็ดกาแฟโรบัสตา (ACFS) ให้ดาวน์โหลดฉบับเต็มเพื่อดูเกณฑ์ขนาดและข้อบกพร่องที่ใช้จริง และเช็กว่ามีฉบับปรับปรุงหรือไม่ **[ยังไม่ได้อ่านฉบับเต็ม]** ส่วน มกษ. 5701 (อาราบิกา) แบ่ง defect เป็น 8 ประเภทเริ่มจากเมล็ดดำ (https://opsmoac.go.th/saraburi-manual-files-431491791810)
- **การแปลงจากภาพ**: เมล็ดที่วางราบจะเห็นด้าน length × width จากด้านบน รูกลมจะกั้นเมล็ดด้วยมิติ "width" (มิติกลาง) เป็นหลัก จึงประมาณได้เป็น `screen_est = floor(width_mm / 0.396875)` แต่ minAreaRect ของ silhouette มักให้ค่าสูงกว่ามิติที่ลอดรูจริงเล็กน้อย
- **ขั้นตอนที่ต้องทำ**: ขอยืม/ซื้อ**ตะแกรงจริง** (screen 13/15/17) แล้วร่อนเมล็ด 3–5 กอง ถ่ายรูปแต่ละกอง แล้ว fit offset หรือ linear regression `screen_true ≈ a·width_px/px_per_mm + b` ใช้ค่าที่ fit ได้ใน config นี่คือหลักฐานที่ดีที่สุดสำหรับกรรมการว่า "ขนาด mm" ของเราเชื่อถือได้
- **Output** ที่แนะนำ: histogram ของ width_mm (bin 0.25 มม.), สัดส่วนต่อ screen (≥18, 17, 16, 15, 14, 13, <13), mean/SD ของ length และ width

---

## 5. Color Features สำหรับ Defects (Lab)

- **ไม่พบ threshold Lab ที่ตีพิมพ์และใช้ได้ทั่วไป** สำหรับ black/sour/faded ของกาแฟสาร งานทบทวนระบุว่ายังไม่มี color characteristic ที่เป็นที่ยอมรับร่วมกัน เพราะใช้ทั้ง RGB, HSV และ CIE (https://arxiv.org/pdf/2409.04068 — Tan, Hung, Tsai 2024 "Site-Specific Color Features of Green Coffee Beans") ส่วน HunterLab ก็ระบุว่าอุตสาหกรรมยังไม่มีมาตรฐานสีเดียว (https://www.hunterlab.com/blog/best-practices-for-measuring-the-color-of-green-coffee-beans)
- Color defects ที่วรรณกรรมกล่าวถึงได้แก่ fade, black, fermented, moldy, insect-damaged และ sour มีช่วงสีตั้งแต่น้ำตาลถึงดำ น้ำตาลอ่อนถึงน้ำตาลเข้ม และอำพันถึงเหลือง (arXiv 2409.04068)
- **แนวทางที่แนะนำ**: เก็บ per-bean Lab features เอง แล้วหา threshold หรือ train โมเดลเล็ก (Logistic Regression/RandomForest) ใช้เป็น **feature ประกอบ** และ cross-check กับ CNN
  - Features: median L*, a*, b*; chroma C* = √(a²+b²); hue h = atan2(b,a); สัดส่วนพิกเซลที่ L* < 30 (`dark_frac`, ใช้จับ partial black); สัดส่วนพิกเซลที่ a* สูงผิดปกติ (`red_frac`, ใช้จับ sour); std ของ L* (ความด่าง)
  - **กฎตั้งต้น (สมมติฐาน ต้อง calibrate กับข้อมูลจริง)**: full black เมื่อ median L* < ~30; partial black เมื่อ dark_frac > ~0.25; sour (น้ำตาลแดง/เหลืองเข้ม) เมื่อ a* สูงกว่า median ของถาดเกิน ~5 หน่วยและ L* ต่ำลง; faded (ซีด/ขาวด่าง) เมื่อ L* สูงและ C* ต่ำกว่าเมล็ดปกติชัดเจน **[ยังไม่ยืนยัน ทั้งหมด]**
  - ใช้ **ค่าสัมพัทธ์ต่อถาด** (Lab ของเมล็ด − median ของถาด) เพื่อลดผลจาก lot/ความชื้น และ**ค่าสัมบูรณ์** (หลังทำ gray normalization) เพื่อดู "สีของ lot" ที่ตลาดสนใจ
- แปลง Lab ด้วย OpenCV โดยให้ input เป็น float32 ใน [0,1] จะได้ L* ช่วง 0–100 และ a*, b* ช่วงประมาณ −127..127 (ถ้าใช้ uint8 OpenCV จะ scale L เป็น 0–255 และ offset a,b +128)
- **นิยามตามมาตรฐาน SCA** (ใช้ในการรายงานผล): Category 1 ได้แก่ full black, full sour, dried cherry, fungus damage, foreign matter (1 เมล็ด = 1 full defect), severe insect damage (5:1) ส่วน Category 2 ได้แก่ partial black/partial sour (3:1), parchment, floater, immature, withered, shell, broken/chipped/cut, hull/husk (5:1) และ slight insect damage (10:1) ใช้ตัวอย่าง 350 g, Specialty ต้องมี Cat1 = 0 และ Cat2 ≤ 5 (https://sca.coffee/research/protocols-best-practices; CVA forms 2025: https://library.sweetmarias.com/wp-content/uploads/2025/06/SCA-CVA-Forms-English-May-2025.pdf) โดยนี่เป็นมาตรฐานของ Arabica ถ้าจะใช้กับ Robusta ให้อ้างอิง มกษ. 5700 หรือ CQI Fine Robusta ด้วย

---

## 6. Classifier บน Pi 5 CPU

### 6.1 ตัวเลขจริงบน Pi 5

**ncnn benchmark ทางการ** (Raspberry Pi 5 BCM2712, Cortex-A76 2.4 GHz, `benchncnn`, input มาตรฐานของแต่ละโมเดล ส่วนใหญ่ 224) จาก https://github.com/Tencent/ncnn/blob/master/benchmark/README.md

| Model | 4 threads avg (ms) | 1 thread avg (ms) | INT8 4 threads (ms) |
|---|---|---|---|
| shufflenet_v2 | 3.39 | 7.14 | — |
| mobilenet_v3 | 7.35 | 11.80 | — |
| squeezenet | 7.38 | 11.87 | 7.21 |
| mnasnet | 7.10 | 12.99 | — |
| mobilenet_v2 | 10.52 | 16.38 | — |
| regnety_400m | 10.99 | 16.49 | — |
| efficientnet_b0 | 12.33 | 24.20 | — |
| resnet18 | 19.96 | 29.68 | 16.74 |
| resnet50 | 46.21 | 89.43 | 40.75 |
| vision_transformer | 611.65 | 1250.30 | — |

**ข้อสรุป**: (1) โมเดลกลุ่ม mobile ที่ 224 ใช้เวลาประมาณ 3–12 ms ต่อภาพ (2) **INT8 แทบไม่ช่วย** บน A76 (เพราะ ncnn ใช้ FP16 storage/arith บน ARMv8.2 อยู่แล้ว) **[เหตุผลเชิงเทคนิค ยังไม่ยืนยัน]** (3) ViT ช้าเกินไป ห้ามใช้

**Ultralytics บน Pi 5** (https://docs.ultralytics.com/guides/raspberry-pi): NCNN เร็วที่สุดบน Pi (detection 640px: NCNN 67 ms, MNN 92 ms, OpenVINO 105 ms, LiteRT 123 ms, ONNX 126 ms, PyTorch 299 ms; หน้าเอกสารไม่ระบุชัดว่าเป็น YOLO26n หรือ s) YOLO26n เร็วกว่า YOLO11n ประมาณ 15% บน Pi 5 (ONNX) ส่วนตารางเก่าที่ใช้ Ultralytics 8.3.39 ให้ YOLO11n NCNN ที่ 88 ms และ OpenVINO ที่ 81 ms

**YOLO26-cls** (https://docs.ultralytics.com/tasks/classify/): YOLO26n-cls มี 2.8M params, 0.4 GFLOPs @224, ImageNet top-1 71.4% (เวลา CPU ONNX 5.0 ms วัดบน CPU ของ server ไม่ใช่ Pi) ที่ **imgsz=128** FLOPs จะลดลงประมาณ 3× เทียบกับ 224 คาดว่าบน Pi 5 NCNN จะใช้ประมาณ 3–8 ms ต่อ crop **[ประมาณการ — ต้อง benchmark เอง]**

**TFLite**: มีรายงาน MobileNet (ไม่ระบุเวอร์ชัน) บน Pi 5 ใช้เวลา 7.57 ± 0.05 ms (https://arxiv.org/pdf/2509.02018) ส่วนตัวเลข "MobileNetV3-small 200 FPS" จากบล็อกยังไม่ได้รับการยืนยัน

### 6.2 การเลือกโมเดล

| ตัวเลือก | ข้อดี | ข้อเสีย | แนะนำ |
|---|---|---|---|
| **YOLO26n-cls / YOLO11n-cls → NCNN** | train/val/confusion matrix/export ได้ด้วยคำสั่งเดียว ทีมเรียนรู้ได้เร็ว | ultralytics + torch บน Pi มีขนาดใหญ่ และ augmentation default ไม่เหมาะกับงานสี | **Default** |
| MobileNetV3-small/large (timm/torchvision) → ONNX Runtime | runtime เบา (numpy + onnxruntime) ทำ batch แบบ dynamic ได้ | ต้องเขียน training loop เอง | Fallback/เปรียบเทียบ |
| EfficientNet-lite0 → TFLite | ทำ INT8 ได้ดี | ecosystem ซับซ้อน และ export ยาก | ไม่จำเป็น |
| OpenVINO บน ARM | เร็วพอ ๆ กับ NCNN ในบางตาราง | ติดตั้งยุ่งกว่า | ทางเลือก |

### 6.3 Throughput ต่อถาด **[ประมาณการ]**
- Capture 12MP ใช้เวลาประมาณ 0.5–1 s, segmentation ที่ 0.5× ประมาณ 0.5–1.5 s, วัดและ crop 300 เมล็ดประมาณ 0.5 s, classify 300 × 5 ms ประมาณ 1.5 s รวมแล้วประมาณ **3–5 วินาทีต่อถาด** ซึ่งเพียงพอ
- **Threading**: NCNN ใช้ 4 threads ภายในโมเดลอยู่แล้ว **อย่ารันหลาย process แข่งกัน** ถ้าต้องการ pipeline ให้แยก thread capture ออกจาก thread process
- **Batching**: ultralytics รับ list ของ crop ได้ แต่ NCNN ไม่ได้ประโยชน์จาก batch มากนัก ส่วน ONNX Runtime ที่ใช้ batch 32–64 ช่วยเพิ่ม throughput ได้ **[ต้องวัดเอง]**
- **วัดเองเสมอ**: ใช้ `bench_cls.py` (ภาคผนวก) รัน 200 ครั้งหลัง warm-up 20 ครั้ง และบันทึกอุณหภูมิ CPU ไปพร้อมกัน

---

## 7. Training Recipe สำหรับ Dataset ขนาดเล็ก

### 7.1 คลาสที่แนะนำ (ปรับตามที่ทีมหาตัวอย่างได้)
`normal`, `black` (รวม full และ partial ถ้าตัวอย่างน้อย), `sour`, `faded`, `broken`, `insect`, `other` (husk/parchment/foreign matter) และ `peaberry` (ถ้าต้องการ) ควรเริ่มจาก 4–5 คลาสที่หาตัวอย่างได้จริงจากโรงสีที่ชุมพร

### 7.2 การเก็บข้อมูล (สิ่งที่ช่วยประหยัดเวลาได้มากที่สุด)
- **ถาดแบบคลาสเดียว**: ให้ผู้เชี่ยวชาญหรือ Q-grader คัดเมล็ดแต่ละคลาสแยกถุง แล้วเทลงถาดทีละคลาส รัน `crop_beans.py` แล้วจะได้ crop ที่มี label อัตโนมัติ เช่น ถาดละ 150–300 crop
- **ต้องถ่ายใน light box และใช้ค่ากล้องชุดเดียวกับวันแข่ง**
- **ตั้งชื่อไฟล์ให้มี tray id** (เช่น `black/T0031__b0123.png`) เพื่อแบ่ง split ตามถาด
- **กลับเมล็ด** (ถ่ายทั้งด้านแบนและด้านโค้ง) เพราะ defect หลายชนิดเห็นได้แค่ด้านเดียว
- **จำนวนข้อมูล** **[heuristic]**: ขั้นต่ำประมาณ 300 crop ต่อคลาสสำหรับ transfer learning เป้าคือ 1,000+ crop ต่อคลาส งานวิจัยที่ได้ผลดีใช้ชุดข้อมูลประมาณ 4,000–8,000 ภาพ (Gope et al. 2025: 4,367 ภาพ 6 คลาส; USK-Coffee: 8,000 ภาพ 4 คลาส)
- **Pretraining เสริม**: ใช้ USK-Coffee (Arabica, 4 คลาส: defect/longberry/peaberry/premium; https://universe.roboflow.com/yolo-annotated-dataset/usk-coffe-segmentasi) เพื่อ fine-tune ก่อนได้ แต่**ห้ามนำมาปนใน test set** เพราะแสงและพันธุ์ต่างกัน

### 7.3 Augmentation (สำคัญมาก: ต้องระวังการ jitter สี)
Ultralytics classify มี default ดังนี้ (https://docs.ultralytics.com/usage/cfg/): `auto_augment=randaugment`, `erasing=0.4`, `hsv_h=0.015`, `hsv_s=0.7`, `hsv_v=0.4` (โดย hsv ใช้เฉพาะเมื่อ `auto_augment=None`), `fliplr=0.5`, `flipud=0`, `scale=0.5`
- **ปิด RandAugment** (`auto_augment=None`) เพราะ RandAugment มี color op ที่จะเปลี่ยน sour เป็น normal หรือ faded เป็น normal ได้
- `hsv_h=0.0`, `hsv_s≤0.1`, `hsv_v≤0.15` (ยอมให้ความสว่างแกว่งเล็กน้อยเพื่อเผื่อ drift ของ LED)
- `fliplr=0.5`, `flipud=0.5` (เมล็ดวางทิศไหนก็ได้ และ crop ถูกหมุนให้แกนยาวเป็นแนวนอนแล้ว)
- `scale` ต่ำ (เช่น 0.05–0.1): ใน ultralytics ค่านี้ใช้กับ RandomResizedCrop ช่วง (1−scale, 1) **[จากการอ่าน source ควรตรวจในเวอร์ชันที่ใช้]** ค่า default 0.5 จะซูมจนขนาดเมล็ดเพี้ยนและอาจตัด defect ออกจากภาพ
- `erasing≤0.1` เพราะ random erasing อาจลบรูแมลงเจาะหรือจุดดำเล็ก ๆ จน label ผิด

### 7.4 Class imbalance
- ข้อมูลจริงมีเมล็ด normal มากกว่า defect หลายสิบเท่า ให้เก็บข้อมูลแบบ "คัดมาแล้ว" ให้สมดุลขึ้น และทำ **oversample คลาสเล็กใน train** (copy ไฟล์ซ้ำ หรือ offline flip/rot90) แต่**ห้าม oversample ใน val/test**
- ใน val/test ให้ดู **per-class recall** และ **macro-F1** ไม่ใช่ accuracy อย่างเดียว
- ตั้ง **confidence threshold** ถ้า top1 conf < 0.5–0.6 ให้รายงานเป็น `uncertain` แยกต่างหาก ซึ่งตรงไปตรงมากว่าการเดาคลาส

### 7.5 Validation และ test-time checks
- **Split ตามถาด** เป็น 70/15/15 (group split) ไม่ใช่สุ่มตาม crop เพราะ crop จากถาดเดียวกันมีแสงและ lot เดียวกัน ถ้าปนกันจะทำให้ val ดูดีเกินจริง
- Ultralytics จะบันทึก `confusion_matrix.png` และ `confusion_matrix_normalized.png` ใน `runs/classify/...` ให้ดูคู่ที่สับสนบ่อย (sour↔normal, faded↔normal และ partial black↔insect)
- **Golden trays**: เตรียมถาดอ้างอิง 2–3 ถาดที่นับและตรวจด้วยมือแล้ว (จำนวน, screen และ defect) ให้รันทุกเช้าและก่อนแข่ง เทียบผลกับค่าจริงเป็น regression test ทั้ง segmentation, การวัด และโมเดล
- **Test บน Pi จริง**: export แล้วรัน NCNN บน Pi ด้วย test set เดียวกัน accuracy ต้องตรงกับบน laptop ภายใน ±0.5% ถ้าไม่ตรงแสดงว่า preprocessing ไม่ตรงกัน (BGR/RGB หรือการ resize)

### 7.6 Hyperparameters เริ่มต้น
`imgsz=128` (crop จริงมีขนาดประมาณ 100–160 px จึงไม่ต้อง upscale), `epochs=100`, `patience=20`, `batch=64`, `cos_lr=True`, `dropout=0.2`, `pretrained=True` บน GTX 1650 (4 GB) ที่ 128px batch 64 ควรรันได้ **[ยังไม่ยืนยัน]** ถ้า OOM ให้ลดเป็น 32

---

## 8. งานวิจัยที่ตีพิมพ์และบทเรียน

| งาน | ข้อมูล | วิธี | ผลลัพธ์ | บทเรียน |
|---|---|---|---|---|
| Pinto, Furukawa, Fukai, Tamura (ICAICTA 2017) doi:10.1109/ICAICTA.2017.8090980 | กาแฟสาร Timor-Leste | Deep CNN | Accuracy **72.4–98.7% ต่อคลาส** | ความยากแต่ละคลาสต่างกันมาก |
| Gope & Fukai (AIMS Agric. Food 2022) https://aimspress.com/aimspress-data/aimsagri/2022/1/PDF/agrfood-07-01-010.pdf | Peaberry กับ normal, กล้อง Nikon D5100 | CNN, SVM, KNN | **98.19% @64×64 บน Raspberry Pi 3, ~13.77 ภาพ/วินาที**; CNN ดีกว่า SVM/KNN และ Pi 3 RAM ไม่พอสำหรับ SVM/KNN ที่ภาพใหญ่ | ภาพเล็ก 64px พอสำหรับงานแยก "รูปร่าง" |
| Gope, Fukai, Ruhad, Barman (Sci. Rep. 2024) doi:10.1038/s41598-024-78598-7 | 4,032 train / 506 test, Bangladesh, black/broken/fade/sour | YOLOv3–v8 + custom | custom-YOLOv8n: P 97.7%, R 99.9%, F1 98.3% (ตาม Sprudge https://sprudge.com/artificial-intelligence-may-help-producers-identify-green-coffee-defects-262515.html) | ข้อมูลมาจากแหล่งเดียว generalize ได้จำกัด |
| Gope et al. (AIMS Agric. Food 2025) doi:10.3934/agrfood.2025050 | 4,367 ภาพ, Arabica + Robusta, 6 คลาส (black, sour, fade, broken, normal, peaberry); กล้อง mirrorless สูง 73 ซม., ไฟ 3 ดวง, พื้นกระดาษขาว, 640×640 | EfficientNet, ResNet-50, Faster R-CNN, YOLOv3–v10 | YOLOv10-N: P 0.992, R 0.984, mAP 0.995; ResNet-50: P 0.837 | มี Robusta และคลาสใกล้เคียงกับโจทย์เรา ใช้อ้างอิงเรื่อง taxonomy ได้ |
| Febriana, Muchtar et al. (IEEE CyberneticsCom 2022) — **USK-Coffee** | 8,000 ภาพ 256×256, 4 คลาส | dataset | ใช้เป็น benchmark ในหลายงาน (เช่น EfficientNet-B0 เทียบ ViT-B16: https://jurnal.polibatam.ac.id/index.php/JAIC/article/view/11563) | ใช้ pretraining ได้ |
| Huang et al. (อ้างใน Hsia et al., Appl. Sci. 2022, 12(21):10966) | good 1,000 + bad 1,000 | YOLOv3 + augmentation | 94.63% **[อ้างทอดจาก secondary source]** | |
| IEEE Access (ม.ค. 2024) https://doaj.org/article/1839ab04806f4e068f51918be7a84a93 | multi-defect | DL | overall 96%, ต่อคลาส 84–98.9% **[ยังไม่ได้อ่านฉบับเต็ม]** | มีคลาสที่ยากอยู่เสมอ |
| Tan, Hung, Tsai (arXiv 2409.04068, 2024) | seed coat color | color features + ML | แยกแหล่งปลูกได้ด้วยสี | สีมีข้อมูลมาก แต่ขึ้นกับแหล่งปลูก |
| Avercasso CS1 (Taiwan, เชิงพาณิชย์) | — | AI real-time | proprietary | ยืนยันว่าตลาดต้องการระบบแบบนี้จริง |

**บทเรียนรวม**
1. งานส่วนใหญ่ได้ accuracy สูงเพราะ**ข้อมูลมาจากแหล่งเดียวและแสงเดียว** ระบบเราก็จะได้ผลแบบนั้นเช่นกันถ้าควบคุมแสงได้ ซึ่งยืนยันว่า light box คือหัวใจของระบบ
2. **คลาสที่ขึ้นกับสี (sour/faded)** มักได้คะแนนต่ำสุด จึงควรมี Lab features ประกอบด้วย
3. งาน Pi ที่ตีพิมพ์ยังเป็น Pi 3 และ binary task สิ่งที่ทีมเราจะทำ (Pi 5, multi-class, per-tray JSON และวัด mm) จึง**เป็นจุดเด่นที่นำเสนอได้**
4. **เกือบไม่มีงานไหนรายงานขนาดเป็น mm และ screen grade** ซึ่งเป็นช่องว่างที่ตลาดต้องการ ควรนำเสนอให้ชัดเจน

---

## 9. Thermal และ Power

- **PSU**: Pi 5 รองรับ 5V 5A (25W; อะแดปเตอร์ทางการคือ 27W 5.1V) ถ้าใช้ 5V 3A **พอร์ต USB จะถูกจำกัดไว้ที่ 600 mA** และพอร์ตพัดลมก็ใช้ limit เดียวกัน (https://www.raspberrypi.com/documentation/computers/raspberry-pi.html)
- **Throttling**: ช่วง 80–85°C Arm cores จะถูกลด clock ทีละขั้น และที่ 85°C ทั้ง Arm และ GPU จะถูกลด (เอกสารเดียวกัน)
- **Active Cooler**: พัดลมเริ่มหมุนที่ 60°C, เร่งที่ 67.5°C และหมุนเต็มที่ที่ 75°C (https://www.raspberrypi.com/news/heating-and-cooling-raspberry-pi-5/) ถ้าไม่มี cooler โหลด NN 4 threads ต่อเนื่องจะ throttle ภายในไม่กี่นาที **[ประมาณการ]** และ latency จะเพิ่มขึ้นมาก
- **Light box เป็นกล่องปิดและมี LED อยู่ข้างใน** ทำให้อุณหภูมิภายในสูง ให้**วาง Pi ไว้นอกกล่อง** (ใช้สายกล้องยาว) หรือเจาะช่องระบายอากาศ
- **Monitoring**: `vcgencmd measure_temp` และ `vcgencmd get_throttled` (0x0 = ปกติ; bit0 = under-voltage now, bit1 = arm freq capped, bit2 = throttled now, bit3 = soft temp limit, bit16–19 = "เคยเกิด" ตั้งแต่บูต) ส่งค่าเหล่านี้ใน JSON ทุกถาดเพื่อเป็น health telemetry ของ AIoT
- **Overclock** (`arm_freq=3000`) Ultralytics แนะนำไว้ แต่**ไม่ควรทำในวันแข่ง** เพราะเพิ่มความร้อนและความเสี่ยงที่ระบบจะไม่เสถียร
- **Storage**: ถ้ามีการเขียนภาพต่อเนื่อง ให้ใช้ SSD (NVMe Base) หรืออย่างน้อยเขียนแค่ JSON + JPEG คุณภาพ 90 และลบไฟล์เก่าเป็นระยะ

---

## 10. JSON Schema ที่เสนอ (MQTT)

Topic: `topgun/<team>/vision/tray` (QoS 1, retain=False), status: `topgun/<team>/vision/status` (LWT, retain=True)

```json
{
  "schema": "vision.tray.v1",
  "node_id": "pi5-vision-01",
  "tray_id": "T0042",
  "lot_id": "CHP-2026-11-17-A",
  "ts": "2026-11-17T10:21:33+07:00",
  "calib": {"px_per_mm": 16.08, "aruco_ok": true, "gray_dE": 1.2, "lens_pos": 4.5},
  "count": {"total": 287, "segmented": 279, "clumps": 4, "clump_est": 8},
  "size_mm": {
    "width_mean": 6.21, "width_sd": 0.48, "length_mean": 9.35,
    "hist_width": {"bins": [5.0, 5.25, 5.5], "counts": [3, 7, 15]},
    "screen_dist": {"18+": 0.02, "17": 0.08, "16": 0.21, "15": 0.33, "14": 0.22, "13": 0.10, "<13": 0.04}
  },
  "color_lab": {"L_median": 52.1, "a_median": -1.8, "b_median": 18.4, "L_p10": 41.0},
  "defects": {
    "counts": {"normal": 251, "black": 6, "sour": 4, "faded": 9, "broken": 7, "insect": 2, "uncertain": 0},
    "defect_rate_count": 0.100,
    "model": "yolo26n-cls-128-v3", "conf_threshold": 0.55
  },
  "health": {"cpu_temp_c": 58.4, "throttled": "0x0", "proc_ms": 3820},
  "image_ref": "T0042_20261117T102133.jpg"
}
```
ส่วนรายละเอียดรายเมล็ด (ถ้าต้องการ) ให้ส่งแยกที่ `.../tray/beans` หรือเก็บเป็นไฟล์ จะได้ไม่ทำให้ payload หลักมีขนาดใหญ่

---

## 11. Code Skeletons (UNTESTED)

> ทุกไฟล์ด้านล่าง**ยังไม่ได้ทดสอบ** ต้องปรับค่าใน config ให้ตรงกับ setup จริง ใช้ Python 3.11+, OpenCV 4.8+, scikit-image 0.22+, ultralytics 8.3+/8.4+, paho-mqtt 2.x

### 11.1 `crop_beans.py` — segmentation + measurement + crop

```python
#!/usr/bin/env python3
"""crop_beans.py — UNTESTED skeleton.
Segment green coffee beans on a tray, measure size (mm) and Lab color, and export
canonical per-bean crops (major axis horizontal, fixed mm canvas, masked background).

Usage (dataset building on laptop or Pi):
    python crop_beans.py --images raw/black/*.jpg --label black --out crops/ --csv beans.csv
"""
from __future__ import annotations
import argparse, csv, glob, json, math, os
from dataclasses import dataclass, asdict, field
import cv2
import numpy as np
from skimage.feature import peak_local_max
from skimage.segmentation import watershed

# ----------------------------- config ---------------------------------------
@dataclass
class Cfg:
    mode: str = "blue_bg"          # "blue_bg" | "backlight" (mask from a separate backlit frame)
    seg_scale: float = 0.5         # segment on downscaled image for speed
    aruco_dict: int = cv2.aruco.DICT_4X4_50
    aruco_mm: float = 30.0         # measured with caliper after printing!
    tray_roi: tuple | None = None  # (x, y, w, h) in full-res px; None = whole image minus markers
    gray_roi: tuple | None = None  # (x, y, w, h) of gray patch in full-res px
    gray_target: float = 120.0     # target mean value of gray patch (0-255) per channel
    exp_bean_width_mm: float = 6.0 # expected bean width for parameter scaling
    min_area_frac: float = 0.25    # drop blobs < this * expected bean area
    clump_factor: float = 1.6      # blob area > factor * median -> clump
    canvas_mm: float = 14.0        # crop canvas side (mm); keeps absolute size info
    out_px: int = 128              # classifier input size
    bg_value: tuple = (128, 128, 128)
    screen_a: float = 1.0          # screen calibration: width_corr = a*width + b (fit with real sieves)
    screen_b: float = 0.0
    calib_npz: str | None = None   # camera matrix/distortion from cv2.calibrateCamera

INCH_64_MM = 25.4 / 64.0  # 0.396875 mm per screen unit

# ----------------------------- helpers --------------------------------------
def gray_normalize(img: np.ndarray, cfg: Cfg) -> tuple[np.ndarray, list[float] | None]:
    if cfg.gray_roi is None:
        return img, None
    x, y, w, h = cfg.gray_roi
    patch = img[y:y + h, x:x + w].reshape(-1, 3).astype(np.float32)
    mean = np.median(patch, axis=0) + 1e-6
    gains = cfg.gray_target / mean
    out = np.clip(img.astype(np.float32) * gains, 0, 255).astype(np.uint8)
    return out, mean.tolist()

def detect_scale(img: np.ndarray, cfg: Cfg):
    """Return (px_per_mm, list_of_marker_quads) using ArUco (OpenCV >= 4.7 API)."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    det = cv2.aruco.ArucoDetector(cv2.aruco.getPredefinedDictionary(cfg.aruco_dict),
                                  cv2.aruco.DetectorParameters())
    corners, ids, _ = det.detectMarkers(gray)
    if ids is None or len(ids) == 0:
        return None, []
    sides = []
    for c in corners:
        q = c.reshape(4, 2)
        sides += [np.linalg.norm(q[i] - q[(i + 1) % 4]) for i in range(4)]
    px_per_mm = float(np.mean(sides)) / cfg.aruco_mm
    # sanity: per-marker scale spread > 1% => camera tilt; consider homography rectification
    return px_per_mm, [c.reshape(4, 2) for c in corners]

def fill_holes(mask: np.ndarray) -> np.ndarray:
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    out = np.zeros_like(mask)
    cv2.drawContours(out, cnts, -1, 255, thickness=cv2.FILLED)
    return out

def make_mask(img_small: np.ndarray, cfg: Cfg, backlit_small: np.ndarray | None) -> np.ndarray:
    if cfg.mode == "backlight" and backlit_small is not None:
        g = cv2.cvtColor(backlit_small, cv2.COLOR_BGR2GRAY)
        g = cv2.GaussianBlur(g, (5, 5), 0)
        _, m = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    else:  # blue background: beans have higher b* (yellowish) than blue bg
        lab = cv2.cvtColor(img_small, cv2.COLOR_BGR2LAB)
        b = cv2.GaussianBlur(lab[:, :, 2], (5, 5), 0)
        _, m = cv2.threshold(b, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, k, iterations=1)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, k, iterations=2)
    return fill_holes(m)

def split_touching(mask: np.ndarray, bean_w_px: float) -> np.ndarray:
    """Distance transform + peak_local_max + watershed. Returns int32 label image."""
    dist = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
    dist = cv2.GaussianBlur(dist, (0, 0), sigmaX=max(1.0, bean_w_px * 0.05))
    n_cc, cc = cv2.connectedComponents(mask)
    coords = peak_local_max(dist,
                            min_distance=max(3, int(0.35 * bean_w_px)),
                            threshold_abs=0.3 * (bean_w_px / 2.0),
                            labels=cc, exclude_border=False)
    markers = np.zeros(mask.shape, dtype=np.int32)
    for i, (r, c) in enumerate(coords, start=1):
        markers[r, c] = i
    labels = watershed(-dist, markers, mask=mask > 0)
    return labels.astype(np.int32)

def lab_stats(img_bgr: np.ndarray, m: np.ndarray) -> dict:
    lab = cv2.cvtColor(img_bgr.astype(np.float32) / 255.0, cv2.COLOR_BGR2LAB)  # L 0..100
    px = lab[m > 0]
    if px.size == 0:
        return {}
    L, a, b = px[:, 0], px[:, 1], px[:, 2]
    return {
        "L_med": float(np.median(L)), "a_med": float(np.median(a)), "b_med": float(np.median(b)),
        "L_p10": float(np.percentile(L, 10)), "L_std": float(np.std(L)),
        "C_med": float(np.median(np.hypot(a, b))),
        "dark_frac": float(np.mean(L < 30.0)),   # threshold = hypothesis, calibrate!
    }

@dataclass
class Bean:
    idx: int
    cx: float; cy: float
    area_mm2: float
    length_mm: float; width_mm: float
    angle_deg: float
    solidity: float
    clump: bool
    est_count: int
    screen: int | None
    color: dict = field(default_factory=dict)

def canonical_crop(img_pad: np.ndarray, lab_pad: np.ndarray, label: int, cx: float, cy: float,
                   angle_deg: float, px_per_mm: float, cfg: Cfg, pad: int) -> np.ndarray:
    """Rotate bean so major axis is horizontal, place on fixed-mm canvas, mask background."""
    canvas_px = cfg.canvas_mm * px_per_mm
    R = int(canvas_px * 0.75) + 2
    x, y = int(round(cx)) + pad, int(round(cy)) + pad
    roi = img_pad[y - R:y + R, x - R:x + R].copy()
    lroi = lab_pad[y - R:y + R, x - R:x + R]
    roi[lroi != label] = cfg.bg_value
    s = cfg.out_px / canvas_px
    M = cv2.getRotationMatrix2D((R, R), angle_deg, s)  # +angle = counter-clockwise
    M[0, 2] += cfg.out_px / 2 - R
    M[1, 2] += cfg.out_px / 2 - R
    return cv2.warpAffine(roi, M, (cfg.out_px, cfg.out_px), flags=cv2.INTER_AREA,
                          borderValue=cfg.bg_value)

# ----------------------------- main API -------------------------------------
def process_image(img: np.ndarray, cfg: Cfg, backlit: np.ndarray | None = None,
                  make_crops: bool = True):
    """Return (beans: list[Bean], crops: list[np.ndarray], meta: dict)."""
    meta: dict = {}
    if cfg.calib_npz:  # optional full undistort (consider precomputed remap maps for speed)
        d = np.load(cfg.calib_npz)
        img = cv2.undistort(img, d["K"], d["dist"])
        if backlit is not None:
            backlit = cv2.undistort(backlit, d["K"], d["dist"])
    img, gray_mean = gray_normalize(img, cfg)
    meta["gray_mean"] = gray_mean
    px_per_mm, quads = detect_scale(img, cfg)
    if px_per_mm is None:
        raise RuntimeError("No ArUco marker found — cannot convert px to mm")
    meta["px_per_mm"] = px_per_mm

    s = cfg.seg_scale
    small = cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    bl_small = cv2.resize(backlit, None, fx=s, fy=s, interpolation=cv2.INTER_AREA) if backlit is not None else None
    mask = make_mask(small, cfg, bl_small)
    # exclude markers / outside tray
    for q in quads:
        cv2.fillConvexPoly(mask, (q * s).astype(np.int32), 0)
    if cfg.tray_roi:
        x, y, w, h = [int(v * s) for v in cfg.tray_roi]
        roi_m = np.zeros_like(mask); roi_m[y:y + h, x:x + w] = 255
        mask = cv2.bitwise_and(mask, roi_m)
        if cfg.gray_roi:
            gx, gy, gw, gh = [int(v * s) for v in cfg.gray_roi]
            mask[gy:gy + gh, gx:gx + gw] = 0

    bean_w_px_small = cfg.exp_bean_width_mm * px_per_mm * s
    labels_small = split_touching(mask, bean_w_px_small)
    labels = cv2.resize(labels_small.astype(np.float32), (img.shape[1], img.shape[0]),
                        interpolation=cv2.INTER_NEAREST).astype(np.int32)

    exp_area_px = (cfg.exp_bean_width_mm * 1.5 * cfg.exp_bean_width_mm) * px_per_mm ** 2
    ids = [i for i in np.unique(labels) if i != 0]
    areas = {i: int(np.count_nonzero(labels == i)) for i in ids}   # OK for ~300 beans; optimise w/ regionprops if slow
    ids = [i for i in ids if areas[i] >= cfg.min_area_frac * exp_area_px]
    med_area = float(np.median([areas[i] for i in ids])) if ids else 1.0

    pad = int(cfg.canvas_mm * px_per_mm)
    img_pad = cv2.copyMakeBorder(img, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=cfg.bg_value)
    lab_pad = cv2.copyMakeBorder(labels, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)

    beans, crops = [], []
    for k, i in enumerate(ids):
        m = (labels == i).astype(np.uint8) * 255
        cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        c = max(cnts, key=cv2.contourArea)
        mo = cv2.moments(c)
        if mo["m00"] == 0:
            continue
        cx, cy = mo["m10"] / mo["m00"], mo["m01"] / mo["m00"]
        theta = 0.5 * math.atan2(2 * mo["mu11"], mo["mu20"] - mo["mu02"])  # major-axis angle
        (_, _), (rw, rh), _ = cv2.minAreaRect(c)
        length_px, width_px = max(rw, rh), min(rw, rh)
        hull_area = cv2.contourArea(cv2.convexHull(c)) or 1.0
        clump = areas[i] > cfg.clump_factor * med_area
        width_mm = width_px / px_per_mm
        width_corr = cfg.screen_a * width_mm + cfg.screen_b
        bean = Bean(idx=k, cx=cx, cy=cy, area_mm2=areas[i] / px_per_mm ** 2,
                    length_mm=length_px / px_per_mm, width_mm=width_mm,
                    angle_deg=math.degrees(theta), solidity=cv2.contourArea(c) / hull_area,
                    clump=clump, est_count=max(1, round(areas[i] / med_area)) if clump else 1,
                    screen=None if clump else int(math.floor(width_corr / INCH_64_MM)),
                    color=lab_stats(img, m))
        beans.append(bean)
        if make_crops and not clump:
            crops.append(canonical_crop(img_pad, lab_pad, i, cx, cy, bean.angle_deg, px_per_mm, cfg, pad))
        elif make_crops:
            crops.append(None)
    meta["median_area_px"] = med_area
    return beans, crops, meta

# ----------------------------- CLI ------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", nargs="+", required=True)
    ap.add_argument("--backlit", nargs="*", default=None, help="matching backlit frames (same order)")
    ap.add_argument("--label", default="unlabeled", help="class name for single-class trays")
    ap.add_argument("--out", default="crops")
    ap.add_argument("--csv", default="beans.csv")
    ap.add_argument("--cfg", default=None, help="JSON overrides for Cfg")
    a = ap.parse_args()
    cfg = Cfg(**json.load(open(a.cfg))) if a.cfg else Cfg()
    files = sorted(f for p in a.images for f in glob.glob(p))
    os.makedirs(os.path.join(a.out, a.label), exist_ok=True)
    with open(a.csv, "a", newline="") as fh:
        w = None
        for n, f in enumerate(files):
            img = cv2.imread(f)
            bl = cv2.imread(a.backlit[n]) if a.backlit else None
            tray = os.path.splitext(os.path.basename(f))[0]
            beans, crops, meta = process_image(img, cfg, bl)
            for b, cr in zip(beans, crops):
                if cr is not None:
                    cv2.imwrite(os.path.join(a.out, a.label, f"{tray}__b{b.idx:04d}.png"), cr)
                row = {"tray": tray, "label": a.label, **{k: v for k, v in asdict(b).items() if k != "color"}, **b.color}
                if w is None:
                    w = csv.DictWriter(fh, fieldnames=list(row.keys())); 
                    if fh.tell() == 0: w.writeheader()
                w.writerow(row)
            print(f"{f}: {len(beans)} blobs, px/mm={meta['px_per_mm']:.2f}")

if __name__ == "__main__":
    main()
```

### 11.2 `train.py` — Ultralytics cls train + group split + export NCNN

```python
#!/usr/bin/env python3
"""train.py — UNTESTED skeleton (run on laptop with GPU).
Input layout (from crop_beans.py):  crops/<class>/<trayid>__bNNNN.png
Creates group-by-tray split:        data/{train,val,test}/<class>/...
"""
import argparse, os, random, shutil
from collections import defaultdict
from pathlib import Path

def group_split(src: Path, dst: Path, val=0.15, test=0.15, seed=0, oversample_to=0):
    random.seed(seed)
    if dst.exists():
        shutil.rmtree(dst)
    for cls_dir in sorted(p for p in src.iterdir() if p.is_dir()):
        by_tray = defaultdict(list)
        for f in cls_dir.glob("*.png"):
            by_tray[f.name.split("__")[0]].append(f)
        trays = sorted(by_tray); random.shuffle(trays)
        n = len(trays); n_val = max(1, round(n * val)); n_test = max(1, round(n * test))
        parts = {"test": trays[:n_test], "val": trays[n_test:n_test + n_val], "train": trays[n_test + n_val:]}
        if n < 3:
            print(f"WARNING {cls_dir.name}: only {n} trays — split leaks; collect more trays!")
        for split, tl in parts.items():
            out = dst / split / cls_dir.name; out.mkdir(parents=True, exist_ok=True)
            files = [f for t in tl for f in by_tray[t]]
            for f in files:
                shutil.copy2(f, out / f.name)
            # naive oversampling of minority classes in TRAIN only
            if split == "train" and oversample_to and 0 < len(files) < oversample_to:
                k = 0
                while len(files) + k < oversample_to:
                    f = files[k % len(files)]
                    shutil.copy2(f, out / f"{f.stem}__dup{k}{f.suffix}"); k += 1
        print(cls_dir.name, {k: len(v) for k, v in parts.items()}, "trays")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--crops", default="crops")
    ap.add_argument("--data", default="data")
    ap.add_argument("--model", default="yolo26n-cls.pt")   # or yolo11n-cls.pt
    ap.add_argument("--imgsz", type=int, default=128)
    ap.add_argument("--epochs", type=int, default=100)
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--oversample_to", type=int, default=600)
    a = ap.parse_args()

    group_split(Path(a.crops), Path(a.data), oversample_to=a.oversample_to)

    from ultralytics import YOLO
    model = YOLO(a.model)
    model.train(
        data=a.data, imgsz=a.imgsz, epochs=a.epochs, batch=a.batch, patience=20,
        cos_lr=True, dropout=0.2, pretrained=True, workers=4, seed=0, deterministic=True,
        # --- colour-safe augmentation (defects ARE colour) ---
        auto_augment=None,      # disable RandAugment (if your version rejects None, upgrade or try "")
        hsv_h=0.0, hsv_s=0.05, hsv_v=0.10,
        fliplr=0.5, flipud=0.5,
        scale=0.08,             # RandomResizedCrop range ~(0.92,1.0): keep apparent size
        erasing=0.1,
        project="runs/cls", name="beans",
    )
    best = Path(model.trainer.save_dir) / "weights" / "best.pt"
    m = YOLO(str(best))
    metrics = m.val(data=a.data, split="test", imgsz=a.imgsz)   # saves confusion matrix PNGs
    print("test top1:", metrics.top1, "top5:", metrics.top5)

    # per-class report
    try:
        from sklearn.metrics import classification_report, confusion_matrix
        names = m.names; y_true, y_pred = [], []
        for cls_id, cls_name in names.items():
            for f in (Path(a.data) / "test" / cls_name).glob("*.png"):
                r = m.predict(str(f), imgsz=a.imgsz, verbose=False)[0]
                y_true.append(cls_id); y_pred.append(int(r.probs.top1))
        print(classification_report(y_true, y_pred, target_names=[names[i] for i in sorted(names)], digits=3))
        print(confusion_matrix(y_true, y_pred))
    except ImportError:
        print("pip install scikit-learn for per-class report")

    # export for Pi 5 CPU
    print("NCNN:", m.export(format="ncnn", imgsz=a.imgsz))   # -> best_ncnn_model/ ; copy folder to Pi
    print("ONNX:", m.export(format="onnx", imgsz=a.imgsz, dynamic=True, simplify=True))  # optional ORT path

if __name__ == "__main__":
    main()
```

### 11.3 `run_pi.py` — capture → pipeline → MQTT JSON (paho-mqtt v2)

```python
#!/usr/bin/env python3
"""run_pi.py — UNTESTED skeleton for Raspberry Pi 5 vision node.
Waits for MQTT command {"cmd":"capture","tray_id":"T0042","lot_id":"..."} then
capture -> segment/measure/crop -> classify -> publish JSON.
"""
import json, os, subprocess, time, threading, queue
from datetime import datetime, timezone, timedelta
import numpy as np
import cv2
import paho.mqtt.client as mqtt
from picamera2 import Picamera2
from libcamera import controls
from crop_beans import Cfg, process_image

TEAM = "teamX"; NODE = "pi5-vision-01"
BROKER = os.getenv("MQTT_HOST", "192.168.1.10"); PORT = int(os.getenv("MQTT_PORT", "1883"))
T_CMD = f"topgun/{TEAM}/vision/cmd"; T_OUT = f"topgun/{TEAM}/vision/tray"; T_STATUS = f"topgun/{TEAM}/vision/status"
CAM = json.load(open("camera.json"))     # {"ExposureTime":20000,"AnalogueGain":1.0,"ColourGains":[1.8,1.6],"LensPosition":4.5}
CFG = Cfg(**json.load(open("pipeline.json"))) if os.path.exists("pipeline.json") else Cfg()
MODEL_DIR = "models/best_ncnn_model"; CONF_TH = 0.55; DEFECT_CLASSES = None  # None => all except "normal"
TZ = timezone(timedelta(hours=7))
SAVE_DIR = "captures"; os.makedirs(SAVE_DIR, exist_ok=True)

# ----------------------------- camera ---------------------------------------
def open_camera() -> Picamera2:
    cam = Picamera2()
    cfg = cam.create_still_configuration(main={"size": (4608, 2592), "format": "RGB888"},  # RGB888 => BGR order for OpenCV
                                         buffer_count=2)
    cam.configure(cfg)
    cam.set_controls({
        "AeEnable": False, "AwbEnable": False,
        "ExposureTime": int(CAM["ExposureTime"]), "AnalogueGain": float(CAM["AnalogueGain"]),
        "ColourGains": tuple(CAM["ColourGains"]),
        "AfMode": controls.AfModeEnum.Manual, "LensPosition": float(CAM["LensPosition"]),
    })
    cam.start(); time.sleep(1.0)   # let controls settle (lens move, gains)
    return cam

def capture(cam: Picamera2):
    req = cam.capture_request()
    try:
        img = req.make_array("main").copy(); md = req.get_metadata()
    finally:
        req.release()
    # QA: verify locked values actually applied
    if abs(md.get("ExposureTime", 0) - CAM["ExposureTime"]) > 200:
        print("WARN exposure drift", md.get("ExposureTime"))
    return img, md

# ----------------------------- classifier -----------------------------------
class Classifier:
    def __init__(self, path: str, imgsz: int):
        from ultralytics import YOLO
        self.m = YOLO(path, task="classify"); self.imgsz = imgsz
        self.names = None
        dummy = np.full((imgsz, imgsz, 3), 128, np.uint8)
        for _ in range(5):
            self.m.predict(dummy, imgsz=imgsz, verbose=False)   # warm-up
    def __call__(self, crops):
        out = []
        for i in range(0, len(crops), 32):
            res = self.m.predict(crops[i:i + 32], imgsz=self.imgsz, verbose=False)  # numpy inputs = BGR
            for r in res:
                self.names = r.names
                out.append((r.names[int(r.probs.top1)], float(r.probs.top1conf)))
        return out

# ----------------------------- health ---------------------------------------
def health():
    def sh(cmd):
        try: return subprocess.check_output(cmd, text=True).strip()
        except Exception: return ""
    t = sh(["vcgencmd", "measure_temp"]).replace("temp=", "").replace("'C", "")
    th = sh(["vcgencmd", "get_throttled"]).replace("throttled=", "")
    return {"cpu_temp_c": float(t) if t else None, "throttled": th}

# ----------------------------- aggregate ------------------------------------
def summarize(beans, preds, meta, tray_id, lot_id, md, t0):
    singles = [b for b in beans if not b.clump]
    widths = np.array([b.width_mm for b in singles]) if singles else np.array([])
    counts = {}
    for p in preds:
        cls = "uncertain" if p is None or p[1] < CONF_TH else p[0]
        counts[cls] = counts.get(cls, 0) + 1
    n_cls = sum(counts.values()) - counts.get("uncertain", 0)
    defect = sum(v for k, v in counts.items()
                 if k not in ("normal", "uncertain") and (DEFECT_CLASSES is None or k in DEFECT_CLASSES))
    scr = [b.screen for b in singles if b.screen is not None]
    def frac(pred): return round(sum(1 for s in scr if pred(s)) / len(scr), 4) if scr else None
    hist, edges = np.histogram(widths, bins=np.arange(4.0, 9.01, 0.25)) if widths.size else ([], [])
    return {
        "schema": "vision.tray.v1", "node_id": NODE, "tray_id": tray_id, "lot_id": lot_id,
        "ts": datetime.now(TZ).isoformat(timespec="seconds"),
        "calib": {"px_per_mm": round(meta["px_per_mm"], 3), "gray_mean": meta.get("gray_mean"),
                  "lens_pos": md.get("LensPosition"), "exposure_us": md.get("ExposureTime")},
        "count": {"total": len(singles) + sum(b.est_count for b in beans if b.clump),
                  "segmented": len(singles), "clumps": sum(b.clump for b in beans),
                  "clump_est": sum(b.est_count for b in beans if b.clump)},
        "size_mm": {
            "width_mean": round(float(widths.mean()), 3) if widths.size else None,
            "width_sd": round(float(widths.std()), 3) if widths.size else None,
            "length_mean": round(float(np.mean([b.length_mm for b in singles])), 3) if singles else None,
            "hist_width": {"bins": [round(float(e), 2) for e in edges[:-1]], "counts": [int(c) for c in hist]},
            "screen_dist": {"18+": frac(lambda s: s >= 18), "17": frac(lambda s: s == 17), "16": frac(lambda s: s == 16),
                            "15": frac(lambda s: s == 15), "14": frac(lambda s: s == 14), "13": frac(lambda s: s == 13),
                            "<13": frac(lambda s: s < 13)},
        },
        "color_lab": {k: round(float(np.median([b.color[k] for b in singles if b.color])), 2)
                      for k in ("L_med", "a_med", "b_med", "L_p10")} if singles else {},
        "defects": {"counts": counts, "defect_rate_count": round(defect / n_cls, 4) if n_cls else None,
                    "model": os.path.basename(MODEL_DIR), "conf_threshold": CONF_TH},
        "health": {**health(), "proc_ms": int((time.time() - t0) * 1000)},
    }

# ----------------------------- MQTT (paho v2) -------------------------------
jobs: "queue.Queue[dict]" = queue.Queue()

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print("MQTT connect failed:", reason_code); return
    client.subscribe(T_CMD, qos=1)                     # (re)subscribe on every reconnect
    client.publish(T_STATUS, json.dumps({"node": NODE, "state": "online"}), qos=1, retain=True)

def on_message(client, userdata, msg):
    try:
        cmd = json.loads(msg.payload)
        if cmd.get("cmd") == "capture":
            jobs.put(cmd)
    except Exception as e:
        print("bad cmd", e)

def main():
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id=NODE)
    client.will_set(T_STATUS, json.dumps({"node": NODE, "state": "offline"}), qos=1, retain=True)
    client.on_connect = on_connect; client.on_message = on_message
    client.reconnect_delay_set(min_delay=1, max_delay=30)
    client.connect_async(BROKER, PORT, keepalive=30)
    client.loop_start()

    cam = open_camera()
    clf = Classifier(MODEL_DIR, CFG.out_px)
    print("ready")
    while True:
        cmd = jobs.get()
        t0 = time.time()
        tray_id = cmd.get("tray_id", datetime.now(TZ).strftime("T%H%M%S")); lot_id = cmd.get("lot_id")
        try:
            # (two-shot option) toggle backlight via GPIO here, capture backlit, then top light
            img, md = capture(cam)
            stamp = datetime.now(TZ).strftime("%Y%m%dT%H%M%S")
            cv2.imwrite(os.path.join(SAVE_DIR, f"{tray_id}_{stamp}.jpg"), img, [cv2.IMWRITE_JPEG_QUALITY, 90])
            beans, crops, meta = process_image(img, CFG)
            idx = [i for i, c in enumerate(crops) if c is not None]
            preds = [None] * len(beans)
            for i, p in zip(idx, clf([crops[i] for i in idx])):
                preds[i] = p
            preds = [p for b, p in zip(beans, preds) if not b.clump]   # classify singles only
            payload = summarize(beans, preds, meta, tray_id, lot_id, md, t0)
            payload["image_ref"] = f"{tray_id}_{stamp}.jpg"
        except Exception as e:
            payload = {"schema": "vision.tray.v1", "node_id": NODE, "tray_id": tray_id, "error": str(e),
                       "health": health()}
        info = client.publish(T_OUT, json.dumps(payload, separators=(",", ":")), qos=1)
        info.wait_for_publish(timeout=5)
        with open(os.path.join(SAVE_DIR, f"{tray_id}.json"), "w") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=1)
        print(tray_id, payload.get("count"), payload.get("defects", {}).get("defect_rate_count"),
              payload.get("health"))

if __name__ == "__main__":
    main()
```

### 11.4 `bench_cls.py` — วัด latency บน Pi เอง (UNTESTED)

```python
import time, numpy as np, subprocess
from ultralytics import YOLO
m = YOLO("models/best_ncnn_model", task="classify")
x = (np.random.rand(128, 128, 3) * 255).astype(np.uint8)
for _ in range(20): m.predict(x, imgsz=128, verbose=False)
ts = []
for _ in range(200):
    t = time.perf_counter(); m.predict(x, imgsz=128, verbose=False); ts.append((time.perf_counter() - t) * 1e3)
print(f"median {np.median(ts):.2f} ms, p95 {np.percentile(ts,95):.2f} ms (includes pre/post-processing)")
print(subprocess.getoutput("vcgencmd measure_temp; vcgencmd get_throttled"))
```

### 11.5 `calib_camera.py` (สั้น ๆ, UNTESTED): หา LensPosition/WB แล้วบันทึกลง camera.json

```python
import json, time, cv2, numpy as np
from picamera2 import Picamera2
from libcamera import controls
cam = Picamera2(); cam.configure(cam.create_still_configuration(main={"size": (4608, 2592), "format": "RGB888"}))
cam.start(); cam.set_controls({"AfMode": controls.AfModeEnum.Auto})
ok = cam.autofocus_cycle(); time.sleep(2.0)                 # AE/AWB converge on gray card
md = cam.capture_metadata()
lp, et, ag, cg = md["LensPosition"], md["ExposureTime"], md["AnalogueGain"], md["ColourGains"]
et = max(10000, round(et / 10000) * 10000)                  # multiple of 10 ms (50 Hz mains)
json.dump({"ExposureTime": et, "AnalogueGain": 1.0, "ColourGains": list(cg), "LensPosition": lp},
          open("camera.json", "w"), indent=1)
print("saved", lp, et, ag, cg, "AF ok:", ok, "-> now re-check gray card R≈G≈B and tweak ColourGains/ExposureTime")
```

---

## 12. Checklist

### Hardware / Setup
- [ ] Pi 5 (4GB+) + **Active Cooler** + **PSU 27W ทางการ** + microSD/SSD สำรองที่โคลนไว้แล้ว
- [ ] Camera Module 3 standard + สาย 22-pin mini ยาว 300 มม. (สำรอง 1 ชุด)
- [ ] Light box ผนังขาวด้าน, LED CRI≥90 5000–5600K, driver DC (ไม่ flicker), แหล่งจ่ายไฟแยกจาก Pi
- [ ] Backlight pad + ถาดอะคริลิกขุ่น **หรือ** พื้นน้ำเงินด้าน (ห้ามใช้สีดำ)
- [ ] ArUco 30 มม. × 2–4 อัน (วัดด้วย caliper แล้ว) + gray patch ติดตายตำแหน่ง
- [ ] Pi วางนอกกล่องหรือมีช่องระบายอากาศ และตรวจ `get_throttled` = 0x0 หลังโหลด 10 นาที

### Calibration
- [ ] `camera.json` ล็อกค่าแล้ว (AE/AWB off, Exposure เป็นจำนวนเท่าของ 10 ms, Gain ≈ 1, ColourGains, LensPosition)
- [ ] Camera intrinsics (`calib.npz`) จาก checkerboard 15–25 ภาพ
- [ ] Fit screen calibration (a, b) กับตะแกรงจริง (13/15/17) จากอย่างน้อย 3 กอง
- [ ] (ถ้ามีเวลา) ColorChecker CCM
- [ ] Golden trays 2–3 ถาด พร้อมผลนับด้วยมือ

### Software
- [ ] OS image เดียวกันทั้งทีม + venv `--system-site-packages` + `requirements-pi.txt`
- [ ] ทดสอบ numpy/simplejpeg/picamera2 import หลังติดตั้ง ultralytics
- [ ] `crop_beans.py` บน golden tray มี count error ≤ 2% และไม่มี over-split ที่มองเห็นได้
- [ ] `bench_cls.py` บน Pi: median latency และอุณหภูมิ
- [ ] `run_pi.py` รองรับ LWT, reconnect, เก็บภาพ + JSON ทุกถาด และ error ต้อง publish เป็น JSON ไม่ใช่ crash

### Data / Model
- [ ] เก็บถาดคลาสเดียวทุกคลาส ทั้งสองด้านของเมล็ด และหลายรอบ/หลายวัน
- [ ] ≥ 300 crop/คลาส (เป้า 1,000+) และแบ่ง split ตามถาด
- [ ] ปิด RandAugment และ hue jitter, scale ต่ำ, erasing ต่ำ
- [ ] ดู confusion matrix และ per-class recall โดยเฉพาะ black/sour
- [ ] ตรวจว่า accuracy บน Pi (NCNN) ตรงกับบน laptop
- [ ] ตั้ง confidence threshold และรายงาน `uncertain`

### วันแข่ง
- [ ] เปิดไฟ light box อุ่นเครื่อง 10 นาที แล้วรัน golden tray 1 รอบ
- [ ] ตรวจ gray patch drift และ px/mm ให้ตรงกับค่าที่บันทึกไว้
- [ ] ห้าม overclock และห้ามเปลี่ยนค่ากล้องหน้างาน
- [ ] มี USB stick ที่มีโมเดลสำรองและ config สำรอง

---

## 13. แหล่งอ้างอิง

**Hardware/Camera**
- Raspberry Pi camera documentation: https://www.raspberrypi.com/documentation/accessories/camera.html
- Picamera2 manual (PDF): https://pip.raspberrypi.com/documents/RP-008156-DS-1-picamera2-manual.pdf
- Raspberry Pi 5 power/thermal: https://www.raspberrypi.com/documentation/computers/raspberry-pi.html
- Heating and cooling Raspberry Pi 5: https://www.raspberrypi.com/news/heating-and-cooling-raspberry-pi-5/
- picamera2 numpy issue: https://github.com/raspberrypi/picamera2/issues/218
- Ultralytics community (numpy/simplejpeg): https://community.ultralytics.com/t/installation-of-yolo-creates-problems-with-dronekit-python-flight-scripts-on-raspberry-pi/1283
- Core Electronics (Bookworm vs Trixie): https://forum.core-electronics.com.au/t/how-to-set-up-yolo-computer-vision-on-a-raspberry-pi-conda-ultralytics/23803

**Inference/Models**
- Ultralytics Raspberry Pi guide: https://docs.ultralytics.com/guides/raspberry-pi
- Ultralytics classify (YOLO26-cls): https://docs.ultralytics.com/tasks/classify/
- Ultralytics classify dataset format: https://docs.ultralytics.com/datasets/classify/
- Ultralytics config/augmentation: https://docs.ultralytics.com/usage/cfg/
- ncnn benchmark (Pi 5 section): https://github.com/Tencent/ncnn/blob/master/benchmark/README.md
- TFLite on Pi 5 (MobileNet 7.57 ms): https://arxiv.org/pdf/2509.02018
- paho-mqtt 2.0 migration: https://eclipse.dev/paho/files/paho.mqtt.python/html/migrations.html

**Image processing**
- OpenCV watershed: https://docs.opencv.org/4.x/d3/db4/tutorial_py_watershed.html
- OpenCV distance transform + watershed: https://docs.opencv.org/3.4.1/d2/dbd/tutorial_distance_transform.html
- OpenCV ArUco detection: https://docs.opencv.org/4.12.0/d5/dae/tutorial_aruco_detection.html
- OpenCV CCM: https://docs.opencv.org/4.x/d1/dc1/tutorial_ccm_color_correction_model.html
- Buckwheat seed studio box (blue bg, 5500K, color tag): https://www.frontiersin.org/articles/10.3389/fpls.2020.581546/full
- Seed sorting patent (top white + blue back light): https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12128448

**Coffee standards**
- Screen sizes: https://coffeeresearch.org/coffee/beansize.htm, https://driftaway.coffee/coffee-grades/, FAO: https://www.fao.org/4/x6939e/X6939e13.htm
- SCA protocols: https://sca.coffee/research/protocols-best-practices ; CVA forms (2025): https://library.sweetmarias.com/wp-content/uploads/2025/06/SCA-CVA-Forms-English-May-2025.pdf
- มกษ. (อ้างถึง 5700-2552 / 5701-2561): https://opsmoac.go.th/saraburi-manual-files-431491791810
- HunterLab green coffee color: https://www.hunterlab.com/blog/best-practices-for-measuring-the-color-of-green-coffee-beans

**Coffee vision papers**
- Pinto et al. 2017 (ICAICTA) doi:10.1109/ICAICTA.2017.8090980
- Gope & Fukai 2022 (Pi 3): https://aimspress.com/aimspress-data/aimsagri/2022/1/PDF/agrfood-07-01-010.pdf
- Gope et al. 2024 Sci. Rep. doi:10.1038/s41598-024-78598-7 ; news: https://dailycoffeenews.com/2024/12/16/researchers-find-highly-accurate-ai-algorithm-for-coffee-defect-detection ; https://sprudge.com/artificial-intelligence-may-help-producers-identify-green-coffee-defects-262515.html
- Gope et al. 2025 AIMS: https://www.aimspress.com/aimspress-data/aimsagri/2025/4/PDF/agrfood-10-04-050.pdf
- USK-Coffee (Roboflow mirror): https://universe.roboflow.com/yolo-annotated-dataset/usk-coffe-segmentasi
- EfficientNet-B0 vs ViT on USK-Coffee: https://jurnal.polibatam.ac.id/index.php/JAIC/article/view/11563
- Hsia et al. (Appl. Sci. 2022): https://www.mdpi.com/2076-3417/12/21/10966
- IEEE Access 2024 (DOAJ): https://doaj.org/article/1839ab04806f4e068f51918be7a84a93
- Tan, Hung, Tsai 2024: https://arxiv.org/abs/2409.04068

**ข้อจำกัดของเอกสารนี้**: ไม่ได้อ่านฉบับเต็มของ มกษ. 5700, Pinto 2017, IEEE Access 2024 และ Sci. Rep. 2024 (ใช้ abstract หรือข่าว) ตัวเลข latency ของ YOLO-cls ที่ 128 px บน Pi 5 และเวลาต่อถาดเป็นการประมาณการที่ต้องวัดเอง ส่วน threshold ของ Lab ทั้งหมดเป็นสมมติฐานที่ต้อง calibrate กับเมล็ด Robusta ชุมพรจริง
