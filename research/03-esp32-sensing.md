# 03 — ESP32 Sensing Node: คู่มือเตรียมตัว TESA Top Gun Rally #20 (Chumphon Robusta AIoT)

> เวอร์ชัน: 2026-10-10 · ผู้จัดทำ: ทีม research (สร้างร่วมกับ AI, ตรวจ API กับเอกสารทางการแล้วตามที่อ้างอิง)
> สถานะโค้ด: **โค้ดทั้งหมดในเอกสารนี้ยังไม่ได้ทดสอบบนบอร์ดจริง (UNTESTED)** ต้อง compile และทดสอบก่อนวันแข่ง

---

## 0. Executive Summary (อ่านอันนี้ก่อน)

1. **เซนเซอร์ที่ผู้จัดน่าจะให้มา** สำหรับโจทย์ "ตากกาแฟ/คุณภาพสารกาแฟ" มีอยู่ 4 กลุ่ม: (ก) อุณหภูมิ/ความชื้นอากาศ (DHT22, SHT3x/SHT4x, AHT20, BME280), (ข) ความชื้นเมล็ด/วัสดุ (capacitive soil moisture v1.2 ที่ใช้แทนได้, probe แบบ resistive), (ค) น้ำหนัก (load cell + HX711) และ (ง) ตัวเสริม เช่น DS18B20, BH1750/LDR, rain sensor, MQ-135/SGP30, TCS34725 และ HC-SR04 **ให้ฝึกทุกตัวในตาราง Quick Reference จนทำได้ภายใน 15 นาทีต่อตัว**
2. **กฎเหล็ก ESP32 (ESP32 รุ่นแรก/WROOM-32):** analog ใช้เฉพาะ **ADC1 (GPIO32–39)** เพราะ ADC2 ใช้ร่วมกับ WiFi · GPIO34–39 เป็น input-only และไม่มี pull-up · ห้ามใช้ GPIO6–11 · หลีกเลี่ยงการต่อโหลดที่ strapping pins (0, 2, 5, 12, 15) · ขา **ไม่รับ 5V** · ควรใช้ `analogReadMilliVolts()` ไม่ใช่ `analogRead()` ดิบ
3. **Arduino-ESP32 core 3.x** (stable ล่าสุดคือ 3.3.12 บน ESP-IDF 5.5.5 ส่วน 4.0.0-RC1 ยังเป็น pre-release **ห้ามใช้ในงานแข่ง**): `ledcSetup`/`ledcAttachPin` **ถูกลบออกแล้ว** ให้ใช้ `ledcAttach(pin, freq, res)` แล้วตามด้วย `ledcWrite(pin, duty)` (อาร์กิวเมนต์เป็น pin ไม่ใช่ channel) ส่วน API ของ timer และ WDT ก็เปลี่ยนเช่นกัน ถ้าใช้ PlatformIO ต้องใช้ platform ของ **pioarduino** เพราะ platform ทางการยังค้างอยู่ที่ core 2.0.17
4. **MQTT:** PubSubClient ใช้ง่ายที่สุดและทุกคนรู้จัก แต่ **เจ้าของประกาศว่าไม่ maintain แล้ว** และข้อจำกัดคือ publish ได้แค่ QoS0 กับ buffer เริ่มต้นแค่ 256 B (ต้องเรียก `setBufferSize()`) ทางเลือกที่ maintain อยู่คือ **arduino-mqtt (256dpi)** ซึ่งรองรับ QoS 0/1/2 และ **espMqttClient (bertmelis)** หรือจะใช้ esp-mqtt ของ ESP-IDF โดยตรงก็ได้ เราใช้ PubSubClient ใน template เพราะสั้นและเสถียรพอสำหรับ telemetry
5. **ความชื้นเมล็ด:** วิธีอ้างอิงคือ **ISO 6673** (อบที่ 105 °C นาน 16 ชม. วัด loss in mass) ICO กำหนดให้สารกาแฟส่งออกมีความชื้น **8–12.5%** (วัดด้วยวิธี ISO 6673) ในงานแข่งไม่มีเวลาอบ 16 ชม. จึงต้อง **เตรียม "ตัวอย่างอ้างอิงที่รู้ความชื้น" จากบ้านไป** ทั้ง Robusta 3–5 ระดับ แล้วทำ calibration แบบหลายจุด (multi-point) ร่วมกับการชดเชยอุณหภูมิ วิธีที่ทนที่สุดคือ **วิธีน้ำหนักหาย (weight loss) ด้วย HX711** ใช้คู่กับ capacitive sensing
6. **ตัวเลือกพิเศษที่น่าใช้:** วัด RH ใน headspace ของขวดปิดสนิทที่ใส่เมล็ด เมื่อเข้าสมดุลจะได้ค่าที่ใกล้ **water activity (aw)** ซึ่งสัมพันธ์กับความเสี่ยงเชื้อรา (ค่า aw < ~0.62 ที่ MC 10–12%) และขา **touch ของ ESP32** (`touchRead`) ใช้เป็นเครื่องวัด capacitance แบบ DIY ได้ทันที
7. **Firmware template** (หัวข้อ 7) เป็นแบบ non-blocking มี WDT, การ reconnect WiFi/MQTT, LWT `online/offline` แบบ retained, รับ config ผ่าน command topic, ตั้งเวลาด้วย NTP, PWM พัดลม และ status LED ครบ ให้ "เสียบเซนเซอร์ใหม่" โดยแก้แค่ฟังก์ชัน `readSensors()`
8. **ฝึก drill** "เซนเซอร์ที่ไม่รู้จัก → MQTT ภายใน 60 นาที" (หัวข้อ 9) ทุกสัปดาห์ก่อนวันแข่ง

---

## 1. Sensor Quick-Reference Table

| เซนเซอร์ | วัดอะไร | Interface | Vcc | Arduino library (ชื่อใน Library Manager → header) | ความแม่น (โดยประมาณจาก datasheet) | Gotcha สำคัญ |
|---|---|---|---|---|---|---|
| DHT11 | T/RH อากาศ | 1-wire เฉพาะ (ไม่ใช่ Dallas) | 3.3–5V | "DHT sensor library" (Adafruit) → `DHT.h` (+ "Adafruit Unified Sensor") หรือ "DHT sensor library for ESPx" → `DHTesp.h` | ±2 °C, ±5 %RH, ช่วง 20–80% | อ่านได้ทุก ≥1 s, ไม่เหมาะกับ RH สูง ๆ |
| DHT22/AM2302 | T/RH | เหมือน DHT11 | 3.3–5V | เหมือน DHT11 | ±0.5 °C, ±2–5 %RH | อ่านได้ทุก ≥2 s, ต้องมี pull-up 4.7–10k (โมดูลส่วนมากมีแล้ว), อ่านพลาดได้ → ต้องเช็ก `isnan()` |
| SHT31/SHT30 | T/RH | I2C 0x44/0x45 | 2.4–5.5V | "Adafruit SHT31 Library" → `Adafruit_SHT31.h` | ±0.3 °C, ±2 %RH | มี heater ไว้ไล่ condensation |
| SHT40/41/45 | T/RH | I2C 0x44 | 1.08–3.6V (บอร์ดโมดูลมักรับ 3–5V) | "Adafruit SHT4x Library" → `Adafruit_SHT4x.h` หรือ "Sensirion I2C SHT4x" | ±0.2 °C, ±1.8 %RH (SHT40) | heater หลายระดับ ช่วยได้มากในสภาพ RH สูง |
| AHT20 / AHT10 | T/RH | I2C 0x38 | 2.0–5.5V | "Adafruit AHTX0" → `Adafruit_AHTX0.h` | ±0.3 °C, ±2 %RH | มักมาเป็นโมดูลคู่กับ BMP280 (AHT20+BMP280) |
| BME280 | T/RH/P | I2C 0x76/0x77, SPI | 1.7–3.6V (โมดูลมี LDO) | "Adafruit BME280 Library" → `Adafruit_BME280.h` | ±1 °C, ±3 %RH | **BMP280 ไม่มี RH** (chip ID 0x58 คือ BMP, 0x60 คือ BME) self-heating ทำให้ T สูงเกิน → ใช้ forced mode |
| BME680/688 | T/RH/P/Gas (VOC) | I2C 0x76/0x77 | 1.7–3.6V | "Adafruit BME680 Library" → `Adafruit_BME680.h`; ถ้าต้องการ IAQ ใช้ "BSEC2" ของ Bosch | gas เป็นค่าความต้านทาน (Ω) ไม่ใช่ ppm | ต้อง burn-in, ใช้ดูแนวโน้มกลิ่นหมัก/รา |
| DS18B20 | อุณหภูมิ (กองเมล็ด/ลมร้อน) | 1-Wire (Dallas) | 3.0–5.5V | "OneWire" + "DallasTemperature" → `OneWire.h`, `DallasTemperature.h` | ±0.5 °C (−10..85 °C) | **ต้องมี pull-up 4.7k** DQ→3.3V; ค่า 85.0 = ยังไม่ convert, −127 = หลุด; ที่ 12-bit ใช้เวลา 750 ms → ใช้ `setWaitForConversion(false)` |
| Load cell + HX711 | น้ำหนัก | 2-wire (DOUT/SCK) bit-bang ไม่ใช่ I2C | 2.6–5.5V | "HX711" (Bogdan Necula/bogde หรือ Rob Tillaart) → `HX711.h`; ทางเลือก "HX711_ADC" (Olav Kallhovd) | 24-bit; ความแม่นจริงขึ้นกับ load cell/creep | สี: E+ แดง, E− ดำ, A− ขาว, A+ เขียว (ไม่ตรงทุกเจ้า) โมดูลบางรุ่นต้องจั๊มป์ RATE ให้ได้ 80 Hz ต้อง tare และ calibrate ด้วยตุ้มน้ำหนักมาตรฐาน **ระวัง drift ตามอุณหภูมิ** |
| Capacitive soil moisture v1.2/v2.0 | ความชื้นวัสดุ (เอามาใช้กับกองเมล็ดได้) | Analog | 3.3–5.5V | ไม่ต้องใช้ lib (`analogReadMilliVolts`) | สัมพัทธ์ ต้อง calibrate เอง | บอร์ดเลียนแบบมักใส่ NE555 ซึ่งไม่ทำงานที่ 3.3V, บางรุ่นไม่มี regulator หรือขาด bleed resistor 1 MΩ → **ทดสอบที่ 5V แล้วเช็กว่า AOUT < 3.1V** ค่าลดลงเมื่อความชื้นเพิ่ม |
| Resistive soil/2-prong (YL-69/FC-28) | ความชื้นแบบ resistive | Analog + Digital (LM393) | 3.3–5V | ไม่ต้องใช้ lib | หยาบมาก | ขั้วกัดกร่อน (electrolysis) → **ให้ไฟเฉพาะตอนอ่าน** (จ่าย Vcc จาก GPIO) เมล็ดแห้ง (<15%) ความต้านทานสูงมาก สัญญาณจะอยู่ใกล้ 0 |
| LDR + R | แสง (สัมพัทธ์) | Analog divider | 3.3V | ไม่ต้องใช้ lib | สัมพัทธ์ | ใช้ R 10k; non-linear |
| BH1750 | ความเข้มแสง (lux) | I2C 0x23/0x5C | 2.4–3.6V (โมดูลรับ 5V) | "BH1750" (Christopher Laws) → `BH1750.h` | 1–65535 lx; กลางแดดเกิน 65k → ใช้ MTreg | ใช้บอกว่า "แดดพอสำหรับตากไหม" |
| Rain sensor (FC-37/YL-83) | ฝน/หยดน้ำ | Analog + Digital (LM393) | 3.3–5V | ไม่ต้องใช้ lib | on/off | แผ่นกัดกร่อน → ให้ไฟเฉพาะตอนอ่าน; ต่อ DO เข้ากับ interrupt เพื่อแจ้ง "ฝนตก เก็บกาแฟ!" |
| MQ-135 (และ MQ-2/3/7) | ก๊าซรวม (NH3, VOC, CO2 แบบหยาบ) | Analog (AO 0–5V) + DO | **5V heater ~150 mA** | "MQUnifiedsensor" (Miguel Califa) → `MQUnifiedsensor.h` หรือคำนวณ Rs/R0 เอง | ค่า ppm ไม่น่าเชื่อถือ ใช้ดู trend | **AO สูงได้ถึง 5V → ต้องใช้ voltage divider** (เช่น 10k/20k) ต้อง preheat ≥ 24–48 ชม. ในครั้งแรก และอย่างน้อยหลายนาทีทุกครั้งที่เปิด |
| SGP30 | TVOC/eCO2 | I2C 0x58 | 1.8V chip (โมดูล 3.3–5V) | "Adafruit SGP30 Sensor" → `Adafruit_SGP30.h` | ใช้ดู trend | ต้องเรียก `IAQmeasure()` ทุก 1 s, ต้อง warm-up 15 s, เก็บ baseline และป้อน absolute humidity เพื่อชดเชย |
| SGP40/41 | VOC index | I2C 0x59 | 1.7–3.6V | "Sensirion I2C SGP40"/"Sensirion Gas Index Algorithm" | index 0–500 | ทางเลือกที่ดีกว่า SGP30 |
| SCD40/41 | CO2 จริง (NDIR-like photoacoustic) | I2C 0x62 | 2.4–5.5V | "Sensirion I2C SCD4x" หรือ "SparkFun SCD4x Arduino Library" | ±(40ppm+5%) | ใช้วัด CO2 จากการหมักหรือการหายใจของเมล็ด |
| TCS34725 | สี RGBC | I2C 0x29 | 3.3V (โมดูลมี LDO) | "Adafruit TCS34725" → `Adafruit_TCS34725.h` | สัมพัทธ์ | ต้องคุมแสงรอบข้าง (ครอบด้วยกล่องดำ + เปิด LED บนโมดูล) แล้ว calibrate white/black ใช้แยกสีเมล็ดเขียวกับสีเปลือก/เมล็ดเสีย |
| TCS3200/TCS230 | สี (ความถี่) | Digital freq (S0–S3, OUT) | 2.7–5.5V | ไม่ต้องใช้ lib (`pulseIn`) | สัมพัทธ์ | ถ้าจ่าย 5V OUT จะเป็น 5V → ต้องลดระดับแรงดัน |
| HC-SR04 | ระยะ (ความสูงกองเมล็ด/ระดับในถัง) | Trig/Echo | **5V** | `pulseIn` เองหรือ "NewPing" | ~3 mm | **Echo ออก 5V → ใช้ divider 1k/2k** หรือหาซื้อ HC-SR04P/RCWL-1601 (3.3V) |
| VL53L0X/VL53L1X | ระยะ (ToF) | I2C 0x29 | 2.6–3.5V (โมดูล 5V) | "VL53L0X" (Pololu) / "VL53L1X" (Pololu) | ±3–5% | ชนกับ TCS34725 เพราะ address 0x29 ซ้ำกัน → ต้องย้าย address หรือแยก bus |
| MLX90614 | อุณหภูมิผิว (IR) | I2C 0x5A | 3.3V (BAA) / 5V (AAA) | "Adafruit MLX90614 Library" | ±0.5 °C | ใช้วัดอุณหภูมิผิวกองเมล็ดตอนตากแดดได้โดยไม่ต้องสัมผัส ขึ้นกับ emissivity |
| IR obstacle / TCRT5000 | มี/ไม่มีวัตถุ | Digital (LM393) | 3.3–5V | — | on/off | ปรับ trimpot; ถูกแสงแดดรบกวน |
| PIR HC-SR501 | การเคลื่อนไหว | Digital (3.3V out) | 5V | — | — | ต้อง warm-up ~60 s |
| ADS1115 (อาจได้มาเป็น ADC เสริม) | ADC 16-bit | I2C 0x48–0x4B | 2–5.5V | "Adafruit ADS1X15" → `Adafruit_ADS1X15.h` | ดีกว่า ADC ภายใน ESP32 มาก | ถ้าจ่าย 5V อย่าให้ input เกิน VDD และ SDA/SCL จะถูก pull-up ไป 5V |

> ค่าความแม่นยำในตารางเป็นค่าทั่วไปจาก datasheet ของผู้ผลิต โมดูลเลียนแบบจากจีนอาจแย่กว่านี้ **ทุกตัวต้องเทียบกับตัวอ้างอิงก่อนใช้**

### 1.1 ขั้นตอนรับมือเซนเซอร์ที่ไม่รู้จัก (Unknown-sensor triage, ≤10 นาที)
1. อ่านตัวหนังสือบนชิปหรือบอร์ด แล้วถ่ายรูป (ทั้งเบอร์ชิปและ silkscreen เช่น VCC/GND/SDA/SCL/AO/DO)
2. นับขา: ถ้ามี SDA/SCL แปลว่าเป็น I2C ให้รัน **I2C scanner** ก่อนอย่างอื่น (ดู address ที่เจอเทียบกับตารางด้านบน) ถ้ามี AO/DO แปลว่าเป็น analog + comparator ถ้ามี DQ/DATA ขาเดียวเป็น 1-Wire/DHT และถ้ามี Trig/Echo หรือ OUT ความถี่ต้องใช้ `pulseIn`
3. ใช้มัลติมิเตอร์วัดก่อนต่อ: จ่ายไฟให้โมดูลแล้ววัดแรงดันสูงสุดที่ขา output **ถ้าเกิน 3.3V ต้องใช้ divider หรือ level shifter**
4. วัดกระแส (ถ้ามี heater เช่น MQ-x ต้องใช้ไฟ 5V จาก USB/VIN ไม่ใช่ 3V3)
5. หา library จาก Library Manager แล้วรันตัวอย่าง (`File > Examples`) ให้ขึ้นค่าทาง Serial ก่อน แล้วค่อยย้ายเข้า template

### 1.2 หมายเหตุรายเซนเซอร์ที่เกี่ยวกับโจทย์กาแฟ
- **T/RH อากาศ:** ปัญหาหลักของการตากในชุมพรคือ RH สูง เซนเซอร์ราคาถูกจะ "ติด" ที่ 99% เมื่อมีหยดน้ำเกาะ (condensation) แนะนำ SHT4x/SHT3x ที่มี heater ให้เปิด heater เป็นช่วงสั้น ๆ แล้วรอให้เย็นก่อนอ่าน ห้ามวางเซนเซอร์โดนแดดตรง ควรใช้ radiation shield (ทำจากจานพลาสติกซ้อนกันก็ได้)
- **คำนวณค่าที่มีประโยชน์จาก T/RH:** dew point, absolute humidity (g/m³) และ VPD เพื่อตัดสินว่า "เปิดพัดลมดูดอากาศภายนอกเข้ามาแล้วช่วยตากหรือไม่" (หัวข้อ 6)
- **Calibration T/RH:** ใช้ **saturated salt test** โดยใส่เกลือแกง (NaCl) ชื้น ๆ ไว้ในขวดปิดสนิท RH จะเข้าใกล้ **~75%** ที่ 25 °C ทิ้งไว้ 6–12 ชม. (ทำที่บ้าน) แล้วบันทึก offset หรือจะใช้ MgCl₂ ซึ่งให้ RH ~33% เป็นจุดที่สองก็ได้ ที่งานแข่งให้ทำแค่เทียบกับเซนเซอร์อีกตัวหรือเครื่องวัดของผู้จัด (1-point offset)
- **HX711 calibration:** `scale.tare()` ตอนว่างก่อน แล้ววางตุ้มน้ำหนักที่รู้ค่า (เช่น ขวดน้ำ 500 g ที่ชั่งด้วยตาชั่งดิจิตอลแล้ว) จากนั้นคิด `factor = reading / known_g` และเรียก `scale.set_scale(factor)` เก็บ factor ลง NVS (Preferences)

---

## 2. ESP32 Pitfalls (ESP32-WROOM-32 / DevKit V1)

### 2.1 Pin map ที่ต้องจำ
| กลุ่ม | GPIO | หมายเหตุ |
|---|---|---|
| **ADC1 (ใช้ได้ตอน WiFi เปิด)** | 32, 33, 34, 35, 36(VP), 39(VN) (37/38 ไม่ได้ออกมาที่ขาบน DevKit) | **analog ทั้งหมดต้องอยู่กลุ่มนี้** |
| ADC2 (อ่านไม่ได้เมื่อ WiFi ทำงาน) | 0, 2, 4, 12, 13, 14, 15, 25, 26, 27 | ใช้เป็น digital ได้ |
| Input-only | 34, 35, 36, 39 | ไม่มี internal pull-up/down → ต้องใส่ R ภายนอก |
| SPI flash (ห้ามใช้) | 6–11 | |
| Strapping pins | 0 (LOW=download), 2 (ต้อง LOW/ลอย), 5 (HIGH), 12 (MTDI ต้อง LOW ไม่งั้นจะเลือก flash 1.8V แล้ว boot ไม่ขึ้น), 15 (HIGH) | ห้ามต่อโมดูลที่ดึงขาเหล่านี้ตอนบูต |
| HIGH/PWM ตอนบูต | 1, 3, 5, 14, 15 | ห้ามต่อ relay/heater เพราะจะติดชั่วขณะตอนบูต |
| UART0 (USB serial) | 1 (TX), 3 (RX) | ห้ามใช้ |
| ขาที่แนะนำ | I2C: 21 (SDA), 22 (SCL); 1-Wire/DHT: 4, 16, 17; PWM out: 18, 19, 23, 25, 26, 27; ADC: 32–36, 39; LED บนบอร์ด: GPIO2 (หลายบอร์ด) | |

แหล่ง: Random Nerd Tutorials ESP32 pinout; ESP-IDF ADC oneshot ("ADC2 is also used by Wi-Fi")

### 2.2 ADC
- ใช้ **`analogReadMilliVolts(pin)`** ซึ่งคืนค่าเป็น mV ที่ calibrate ด้วยค่าใน eFuse แล้ว ส่วน `analogRead()` คืนค่า raw แบบ non-calibrated
- Attenuation (ESP32 รุ่นแรก): `ADC_0db` 100–950 mV, `ADC_2_5db` 100–1250 mV, `ADC_6db` 150–1750 mV, **`ADC_11db` 150–3100 mV (ค่า default)** ตั้งต่อขาได้ด้วย `analogSetPinAttenuation(pin, ADC_11db)`
- **Non-linearity:** ค่าต่ำกว่า ~150 mV จะอ่านเป็น 0 และเกิน ~3.1 V จะ saturate ดังนั้นต้องออกแบบ divider ให้สัญญาณอยู่ราว 0.2–2.8 V
- **Noise:** อ่าน 16–64 ครั้งแล้วใช้ค่าเฉลี่ยหรือ median และใส่ C 100 nF ระหว่างขากับ GND ถ้าอ่านตอน WiFi กำลังส่ง ค่าจะ spike ได้ ส่วน `analogReadResolution(12)` เป็นค่า default
- ถ้าต้องการความละเอียดจริงจัง (เช่น capacitive moisture) ใช้ **ADS1115** ผ่าน I2C
- ใน ESP-IDF ตอนนี้ไม่มี `esp_adc_cal` แบบเดิมแล้ว ถูกแทนด้วย `adc_cali_*` (scheme line fitting/curve fitting) แต่ใน Arduino ให้ใช้ `analogReadMilliVolts` ซึ่งทำส่วนนี้ให้อยู่แล้ว

### 2.3 Level shifting 3.3V ↔ 5V
- **ESP32 ไม่ทน 5V** ถ้าสัญญาณ output จากเซนเซอร์เป็น 5V (HC-SR04 Echo, MQ AO, TCS3200 ที่ 5V, โมดูล I2C ที่ pull-up ไป 5V) ให้แก้ด้วยวิธีใดวิธีหนึ่งต่อไปนี้:
  - Divider: 5V → 3.3V ใช้ R1=1k (บน), R2=2k (ล่าง) ได้ ~3.33V สำหรับสัญญาณดิจิทัล ส่วน analog ใช้ 10k/20k
  - Level shifter แบบ BSS138 (2-way สำหรับ I2C) หรือ TXS0108E
  - I2C: ถ้าโมดูลมี pull-up ไป Vcc 5V ให้จ่ายโมดูลด้วย 3.3V แทน (ถ้า datasheet อนุญาต)
- Output 3.3V จาก ESP32 ไปสั่งโมดูล 5V (relay บางรุ่น) มักใช้ได้ (V_IH ของ TTL ~2V) แต่ relay module แบบ active-LOW ที่ใช้ JD-VCC ต้องตรวจให้ดี

### 2.4 Power & Brownout
- WiFi TX มีกระแส peak ~300–500 mA ถ้าใช้สาย USB ยาวหรือคุณภาพต่ำ หรือจ่ายเซนเซอร์ heater (MQ-x 150 mA) พร้อมกัน จะเจอ **"Brownout detector was triggered"** แล้วบอร์ด reset วนไปเรื่อย ๆ
- แก้ด้วย: ใช้สาย USB ที่สั้นและหนา หรือ power bank ที่ดี, ใส่ **C 470–1000 µF** คร่อม 5V/GND ใกล้บอร์ด, จ่ายไฟ servo/พัดลม/MQ จาก**แหล่งแยก**แล้ว **ต่อ GND ร่วมกัน**
- **ห้ามปิด brownout detector** เป็นทางแก้หลัก (มันแค่ซ่อนปัญหา)
- GPIO จ่ายกระแสได้จำกัด ให้ถือว่า ~12–20 mA ต่อขาเพื่อความปลอดภัย โหลดอย่างพัดลม, heater, buzzer active ต้องขับผ่าน **MOSFET (logic-level เช่น AO3400, IRLZ44N) หรือ transistor + flyback diode**

### 2.5 อื่น ๆ
- ESP32 รุ่นอื่น (S3, C3, C6) มี pin map ต่างกัน **ต้องดู datasheet ของรุ่นที่ใช้จริง** ตัวอย่างใน doc นี้อ้างอิง ESP32 classic
- `delay()` ยาว ๆ ใน `loop()` จะทำให้ MQTT keepalive หลุดและ WDT ทำงาน ให้ใช้ `millis()` แทนเสมอ
- `Serial.begin(115200)` และถ้าไม่ต้องการต้องปิด log ด้วย `Core Debug Level`

---

## 3. Arduino-ESP32 Core 3.x — API ปัจจุบัน

### 3.1 เวอร์ชัน
- **Stable ล่าสุด: 3.3.12 (18 ก.ย. 2026, บน ESP-IDF v5.5.5)** ส่วน 4.0.0-RC1 (IDF 6.1) ยังเป็น pre-release **อย่าใช้ในงานแข่ง** แนะนำให้ล็อกเวอร์ชันเดียวกันทั้งทีม (Boards Manager → esp32 by Espressif → เลือกเวอร์ชัน)

### 3.2 LEDC (PWM) — ของเก่าที่ถูกลบ และของใหม่
| Core 2.x (ถูกลบแล้ว) | Core 3.x (ปัจจุบัน) |
|---|---|
| `ledcSetup(ch, freq, res); ledcAttachPin(pin, ch);` | `bool ledcAttach(uint8_t pin, uint32_t freq, uint8_t resolution);` (เลือก channel อัตโนมัติ) |
| — | `bool ledcAttachChannel(uint8_t pin, uint32_t freq, uint8_t resolution, int8_t channel);` |
| `ledcWrite(ch, duty)` | `bool ledcWrite(uint8_t pin, uint32_t duty);` **← ใช้ pin** |
| `ledcWriteTone(ch, f)` | `uint32_t ledcWriteTone(uint8_t pin, uint32_t freq);` |
| `ledcDetachPin(pin)` | `bool ledcDetach(uint8_t pin);` |
| — | `uint32_t ledcChangeFrequency(uint8_t pin, uint32_t freq, uint8_t resolution);` |
| — | `bool ledcFade(uint8_t pin, uint32_t start_duty, uint32_t target_duty, int max_fade_time_ms);` |

- ESP32 classic รองรับ resolution 1–20 bit ความถี่และความละเอียดขัดกัน (`freq ≈ clk / (div × 2^res)`) ค่าที่ใช้บ่อยคือ พัดลม 4-pin ใช้ **25 kHz/8-bit**, MOSFET+พัดลม 2-pin ใช้ 1–5 kHz/8-bit, servo ใช้ **50 Hz/16-bit** (1 ms = 3277, 1.5 ms = 4915, 2 ms = 6554), LED ใช้ 5 kHz/8-bit
- **ช่องที่มีความถี่และ resolution เดียวกันจะใช้ timer ร่วมกัน** ถ้าเรียก `ledcChangeFrequency` ช่องอื่นจะเปลี่ยนตามด้วย
- `analogWrite(pin, val)` ก็ใช้ได้ใน 3.x (ภายในเรียก LEDC)

### 3.3 Timer / Watchdog / อื่น ๆ
- Timer: `timerBegin(frequency)` รับพารามิเตอร์เดียวแล้ว, `timerAttachInterrupt(timer, isr)` เหลือ 2 พารามิเตอร์, `timerAlarm(timer, alarm_value, autoreload, reload_count)` ใช้แทน `timerAlarmWrite`+`timerAlarmEnable`
- Task WDT: **`esp_task_wdt_init(timeout_s, panic)` แบบ 2 อาร์กิวเมนต์ใช้ไม่ได้แล้ว** ต้องใช้ struct `esp_task_wdt_config_t {timeout_ms, idle_core_mask, trigger_panic}` และเนื่องจาก IDF มักเริ่ม TWDT ให้เองตอนบูต ให้เรียก `esp_task_wdt_reconfigure(&cfg)` ก่อน ถ้าได้ `ESP_ERR_INVALID_STATE` (ยังไม่ init) ค่อยเรียก `esp_task_wdt_init(&cfg)` แล้วตามด้วย `esp_task_wdt_add(NULL)` (ดู template)
- `hallRead()` ถูกลบ, `WiFiClient::flush()` ไม่ล้าง RX buffer แล้ว (ใช้ `clear()`), BLE ใช้ `String`
- ADC: ลบ `analogSetClockDiv`, `adcAttachPin`, `analogSetVRefPin`

### 3.4 Arduino IDE vs PlatformIO vs ESP-IDF
| | Arduino IDE 2.x | PlatformIO (VS Code) | ESP-IDF |
|---|---|---|---|
| ข้อดี | ตั้งค่าเร็ว ทุกคนในทีมใช้เป็น | lock เวอร์ชัน lib ใน `platformio.ini`, build เร็ว, multi-env | ควบคุมได้เต็มที่, esp-mqtt, OTA ระดับ production |
| ข้อเสีย | จัดการเวอร์ชัน lib ยาก | **platform ทางการ (espressif32) ค้างอยู่ที่ Arduino core 2.0.17** → ต้องใช้ pioarduino | ใช้เวลานาน ไม่เหมาะกับโจทย์ 1 ชม. |
| ใช้เมื่อ | drill และวันแข่ง (เครื่องสำรอง) | เครื่องหลักของทีม | ไม่แนะนำสำหรับงานนี้ |

`platformio.ini` สำหรับ core 3.x:
```ini
[env:esp32dev]
; pioarduino community fork (platform ทางการไม่มี core 3.x) — ควร pin tag ให้ตรงกับเวอร์ชันที่ทดสอบแล้ว
platform = https://github.com/pioarduino/platform-espressif32/releases/download/stable/platform-espressif32.zip
board = esp32dev
framework = arduino
monitor_speed = 115200
lib_deps =
  knolleary/PubSubClient@^2.8
  bblanchon/ArduinoJson@^7
  paulstoffregen/OneWire
  milesburton/DallasTemperature
  adafruit/Adafruit SHT4x Library
  bogde/HX711
  tzapu/WiFiManager
```
> **ก่อนแข่ง:** ให้ดาวน์โหลด lib และ core ทั้งหมดไว้ offline (WiFi ในงานอาจช้า) โดย zip โฟลเดอร์ `~/Arduino/libraries` และ `~/.platformio` แล้วสำรองใส่ USB

**ESP-IDF esp-mqtt:** esp-mqtt เป็น component ที่มากับ arduino-esp32 อยู่แล้ว จึง `#include "mqtt_client.h"` แล้วใช้ `esp_mqtt_client_init()` / `esp_mqtt_client_start()` แบบ event-driven ได้ รองรับ QoS 0/1/2, TLS, LWT และมี reconnect อัตโนมัติ (ทำงานใน task ของตัวเอง) ข้อแลกเปลี่ยนคือ API เป็นแบบ C, callback ทำงานอยู่ใน task อื่น จึงต้องระวังเรื่อง thread safety และ debug ยากกว่า

---

## 4. MQTT บน ESP32

### 4.1 เลือก library
| Library | QoS publish | QoS subscribe | Buffer | Blocking? | สถานะ | ใช้เมื่อ |
|---|---|---|---|---|---|---|
| **PubSubClient** (knolleary) `PubSubClient.h` | **0 เท่านั้น** | 0/1 | default **256 B** (รวม header) → `setBufferSize(1024)` | `connect()` block ได้นานถึง socket timeout (default 15 s) | **ไม่ maintain แล้ว** (README) | telemetry ทั่วไป, ทุกคนรู้จัก, ตัวอย่างเยอะ |
| **arduino-mqtt** (256dpi, ชื่อ lib "MQTT" โดย Joel Gaehwiler) `MQTT.h` | 0/1/2 | 0/1/2 | default 128 B → `MQTTClient client(1024)` | กึ่ง block | active | ต้องการ QoS1 publish |
| **espMqttClient** (bertmelis) | 0/1/2 | 0/1/2 | ไม่ค่อยจำกัด | non-blocking/async | active, เป็นผู้สืบทอดของ AsyncMqttClient | ต้องการ async และ TLS |
| AsyncMqttClient (marvinroger) | 0/1/2 | | | async | ไม่ active → ใช้ espMqttClient แทน | — |
| esp-mqtt (ESP-IDF) | 0/1/2 | 0/1/2 | ตั้งค่าได้ | task แยก | official Espressif | ต้องการความทนสูงสุด |

**PubSubClient API ที่ต้องใช้:**
```cpp
mqtt.setServer(host, 1883);
mqtt.setCallback(onMessage);          // void onMessage(char* topic, byte* payload, unsigned int len)
mqtt.setBufferSize(1024);             // คืนค่า bool — เช็กด้วย
mqtt.setKeepAlive(15);                // วินาที
mqtt.setSocketTimeout(3);             // ลดเวลา block ตอน connect
mqtt.connect(clientId, user, pass, willTopic, willQos, willRetain, willMessage, cleanSession);
mqtt.publish(topic, payload, retained);  // QoS0 เสมอ
mqtt.subscribe(topic, 1);             // qos 0 หรือ 1
mqtt.loop();                          // ต้องเรียกทุกรอบ loop
mqtt.state();                         // -4..5 ใช้ debug (เช่น -2 = connect failed, 5 = unauthorized)
```
> ถ้า publish แล้วเงียบ (ได้ `false`) สาเหตุอันดับหนึ่งคือ **payload + topic เกิน buffer** ให้เรียก `setBufferSize()`

### 4.2 Topic design (เสนอ ต้องตกลงกับทีม Pi/backend ก่อน)
```
tesa/<team>/<node>/status        retained, "online"/"offline" (LWT)
tesa/<team>/<node>/telemetry     JSON ทุก N วินาที (QoS0)
tesa/<team>/<node>/event         alert เช่น rain, overtemp, mold_risk
tesa/<team>/<node>/cmd           ← รับคำสั่ง JSON  {"id":"42","set":{"interval":5000,"fan":60}}
tesa/<team>/<node>/cmd/ack       → ตอบ {"id":"42","ok":true}
tesa/<team>/<node>/config        retained, config ปัจจุบัน (ส่งหลัง connect)
```
- ใช้ตัวพิมพ์เล็กล้วน ไม่มีช่องว่าง และไม่ขึ้นต้นด้วย `/` ถ้าผู้จัดกำหนด topic/format มาให้ **ให้ทำตามของผู้จัด 100%**
- Telemetry payload ใส่ `ts` (epoch จาก NTP), `seq` (เลขลำดับ), `uptime`, `rssi` และค่าเซนเซอร์พร้อมหน่วยในชื่อ key เช่น `air_t_c`, `air_rh_pct`, `bean_mc_pct`, `mass_g`
- **Retained:** ใช้กับ status/config เท่านั้น **ห้ามใช้กับ telemetry**
- **LWT:** ตั้ง will = `offline` (retained, QoS1) แล้วเมื่อ connect สำเร็จให้ publish `online` (retained) ทันที

### 4.3 Reconnect แบบ non-blocking (หลักการ)
- ใน `loop()`: ถ้า WiFi หลุด ให้ลอง reconnect ทุก 5 s (ไม่ใช้ while) ถ้า WiFi ต่อได้แล้วแต่ MQTT หลุด ให้ลอง `connect` ทุก 3–5 s แบบ backoff (3→6→12→30 s) และ **ห้าม `while(!mqtt.connected())`**
- เปิด `WiFi.setAutoReconnect(true)` และ `WiFi.persistent(false)`
- clientId ต้องไม่ซ้ำกับใคร (ใช้ MAC ต่อท้าย) ถ้าซ้ำกัน broker จะเตะตัวเก่าออกวนไปมา
- ระหว่าง offline ให้เก็บข้อมูลลง ring buffer เล็ก ๆ (เช่น 50 ข้อความ) แล้วค่อยส่งเมื่อกลับมาออนไลน์ (ถ้ามีเวลาทำ)

### 4.4 ArduinoJson v7 (สิ่งที่เปลี่ยนจาก v6)
```cpp
JsonDocument doc;                         // แทน StaticJsonDocument/DynamicJsonDocument (ขยายขนาดเอง)
doc["air_t_c"] = 28.4;
JsonObject s = doc["sensors"].to<JsonObject>();     // แทน createNestedObject
JsonArray a = doc["arr"].to<JsonArray>();           // แทน createNestedArray
if (doc["set"]["interval"].is<uint32_t>()) {...}    // แทน containsKey
char buf[512]; size_t n = serializeJson(doc, buf);  // serializeJson(String) จะเขียนทับ ไม่ append
DeserializationError e = deserializeJson(doc, payload, len);
if (doc.overflowed()) {...}                         // แทนการเช็ก capacity()
```

### 4.5 NTP time (Thailand UTC+7)
```cpp
configTzTime("<+07>-7", "pool.ntp.org", "time.google.com");  // POSIX TZ: UTC+7
struct tm t; if (getLocalTime(&t, 100)) { time_t now = time(nullptr); }
```
- ถ้ายังไม่ sync (`time(nullptr) < 1700000000`) ให้ส่ง `ts:0` พร้อม `uptime` แทน **อย่าส่งเวลา 1970** ถ้าเครือข่ายในงานบล็อก NTP ให้ใช้ broker หรือ Pi เป็นตัวให้เวลา (Pi ส่ง `tesa/<team>/time` retained)

### 4.6 WiFiManager & OTA
- **WiFiManager (tzapu)** `WiFiManager.h`: `wm.setConfigPortalTimeout(120); wm.autoConnect("TESA-ESP32-XX");` จะเปิด captive portal ให้กรอก SSID ทางมือถือ ช่วยได้มากเมื่อ SSID ในงานเปลี่ยน สามารถเพิ่ม `WiFiManagerParameter` สำหรับ broker host/port ได้ด้วย
- **ArduinoOTA** (มากับ core): `ArduinoOTA.setHostname("tesa-node1"); ArduinoOTA.setPassword("..."); ArduinoOTA.begin();` แล้วเรียก `ArduinoOTA.handle()` ใน loop ต้องใช้ partition scheme ที่มี OTA (Default 4MB with spiffs ใช้ได้) **ในวันแข่งให้ใช้ USB เป็นหลัก** ส่วน OTA เป็นทางเลือกเมื่อบอร์ดติดตั้งอยู่ในจุดที่เข้าถึงยาก

---

## 5. การประมาณความชื้นเมล็ด (Moisture Content, MC)

### 5.1 นิยามและเป้าหมาย
- ใช้ **wet basis**: `MC_wb (%) = (m_water / m_total) × 100` ตามมาตรฐานการค้า
- ICO (Resolution 420, Coffee Quality-Improvement Programme): สารกาแฟส่งออก **Arabica/Robusta ต้องมีความชื้น 8–12.5%** โดยวัดด้วย **ISO 6673** ส่วนเป้าหมายในโจทย์คือ 11–13% ให้ระวังว่าค่า **>12.5% เกินเกณฑ์ ICO**
- Cenicafé: เมล็ดที่ MC 10–12% มีค่า water activity < 0.62 และการตากที่ถูกขัดจังหวะ (ฝนตก/ไม่สม่ำเสมอ) ทำให้ปริมาณเชื้อราและยีสต์สูงขึ้นมาก ราที่สร้าง OTA เจริญได้ดีที่ 28–32 °C และ aw สูง (เริ่มงอกที่ aw ~0.80)

### 5.2 Reference method: ISO 6673 (Green coffee — Determination of loss in mass at 105 °C)
- หลักการ: อบ test portion ที่ **105 °C นาน 16 ชม.** ภายใต้ความดันบรรยากาศ แล้ววัด mass loss ซึ่งตามธรรมเนียมใช้เป็นค่าความชื้นได้ ค่าที่ได้จะ**ต่ำกว่าวิธีอ้างอิงพื้นฐาน ISO 1446 ประมาณ 1.0%**
- สถานะเอกสาร: ฉบับ 2003 ข้อมูลไม่ตรงกัน บางแหล่งระบุว่า withdrawn บางแหล่งว่ายืนยันแล้วในปี 2021 และมี ISO/DIS 6673 กำลังปรับปรุง **ต้องตรวจที่ iso.org ก่อนอ้างในสไลด์**
- วิธีทำที่บ้านเพื่อเตรียมตัวอย่างอ้างอิง (ประยุกต์ ไม่ใช่ตามมาตรฐานครบทุกข้อ):
  1. ชั่งถาดอะลูมิเนียมเปล่า (m_dish) ด้วยตาชั่ง 0.01 g
  2. ใส่เมล็ดทั้งเมล็ด ~10 g แล้วชั่ง (m1)
  3. อบที่ 105 °C ด้วยเตาอบที่วัดอุณหภูมิจริงด้วย DS18B20/เทอร์โมคัปเปิล นาน 16 ชม.
  4. ปล่อยเย็นในภาชนะปิดที่มีสารดูดความชื้น (ซิลิกาเจล) แล้วชั่ง (m2)
  5. `MC = (m1 − m2) / (m1 − m_dish) × 100` ทำซ้ำ 2–3 ถาดแล้วเฉลี่ย

### 5.3 วิธี A — Weight-loss tracking ด้วย HX711 (ทนที่สุด แนะนำ)
ถ้ารู้ MC เริ่มต้น (MC₀) และมวลเริ่มต้น (m₀) จะคำนวณ dry matter ได้คงที่: `m_dry = m₀ × (1 − MC₀)`
```
MC(t)    = 1 − m_dry / m(t)
m_target = m_dry / (1 − MC_target)
```
ตัวอย่าง: เมล็ด 1000 g ที่ MC₀ = 50% จะได้ m_dry = 500 g ถ้าเป้าหมายคือ 12% จะได้ m_target = 500/0.88 = **568 g** ESP32 จึงสามารถส่ง `progress_pct` และ `eta` (จาก slope ของน้ำหนัก) ไปยัง dashboard ได้
- ข้อควรระวัง: load cell drift ตามอุณหภูมิ (กลางแดดเปลี่ยนเยอะ) แก้โดย tare ตอนเช้า, ใช้ถาดเปล่าที่ 2 เป็น reference, กรองด้วย median แล้ว EMA, ป้องกันลมพัดถาด และน้ำฝนที่ตกลงในถาดจะทำให้น้ำหนัก**เพิ่ม** (ใช้ rain sensor ประกอบ)
- ถ้าไม่รู้ MC₀ ให้ใช้ sample ถาดเล็กที่วัด MC ด้วยเครื่องวัดหรือ capacitive แล้ว scale ขึ้น

### 5.4 วิธี B — Capacitive sensing
**หลักการ:** น้ำมีค่า dielectric constant ~80 ส่วนเมล็ดแห้งมี ~2–4 ดังนั้นเมื่อ MC สูงขึ้น capacitance ระหว่างอิเล็กโทรดที่ฝังในกองเมล็ดก็จะสูงขึ้น เครื่องวัดเชิงพาณิชย์ (แบบ capacitance/RF) ใช้หลักเดียวกันนี้บวกการวัดอุณหภูมิ, การชั่งน้ำหนักหรือคุมปริมาตร (bulk density) และ **calibration curve แยกตามชนิดพืช** ส่วนเครื่องแบบ resistive (เข็ม) ใช้ได้ไม่ดีกับเมล็ดแห้งเพราะความต้านทานสูงมาก

**ตัวเลือก hardware (ไล่จากง่ายไปยาก):**
1. **Capacitive soil moisture v1.2** ฝังในถ้วยเมล็ดที่มีปริมาตรคงที่ แล้วอ่าน `analogReadMilliVolts` (ค่า mV จะลดลงเมื่อชื้นขึ้น)
2. **ขา touch ของ ESP32** (T0..T9 เช่น GPIO4, 13, 14, 15, 27, 32, 33) ใช้แผ่นทองแดง 2 แผ่นขนานกันประกบถ้วยพลาสติก โดยต่อแผ่นหนึ่งเข้าขา touch และอีกแผ่นเข้า GND แล้วอ่าน `touchRead(pin)` (บน ESP32 classic ค่าจะลดลงเมื่อ capacitance เพิ่มขึ้น) เป็น DIY capacitance meter ที่ไม่ต้องใช้ชิปเพิ่ม **ระวัง GPIO 0, 2, 12, 15 ที่เป็น strapping** ให้เลือก GPIO32/33 (T9/T8)
3. **RC timing:** ชาร์จ C (ตัวอิเล็กโทรด) ผ่าน R 1 MΩ แล้วจับเวลาจนถึงระดับ HIGH (ใช้ `micros()` หรือ PCNT)
4. **FDC1004 / 555 + PCNT** ละเอียดที่สุดแต่ต้องเตรียมไปก่อน

**ขั้นตอนวัดให้ซ้ำได้ (สำคัญกว่าตัวเซนเซอร์):**
- ใช้ถ้วยปริมาตรคงที่ เทเมล็ดจากความสูงคงที่ (เช่น กรวย 10 cm) แล้วปาดหน้าให้เรียบ **ห้ามกด**
- อ่าน 64 ครั้ง ตัด outlier แล้วเฉลี่ย วัดอุณหภูมิเมล็ดด้วย DS18B20 ในถ้วยเดียวกัน
- ชั่งน้ำหนักถ้วยด้วย (bulk density) เพราะ density เปลี่ยนตาม MC ข้อมูลนี้ใช้เป็น feature ที่ 2 ได้

### 5.5 Calibration: two-point / multi-point + temperature compensation
**เตรียมตัวอย่างอ้างอิง (ทำที่บ้าน 1–2 สัปดาห์ก่อนแข่ง):**
1. ซื้อสาร Robusta ชุมพร ~2 kg แล้ววัด MC ด้วยวิธี 5.2 (หรือยืมเครื่องวัดความชื้นเมล็ด/halogen moisture analyzer จากมหาวิทยาลัย)
2. ทำให้ได้หลายระดับ:
   - **เพิ่มน้ำ:** `น้ำที่ต้องเติม (g) = m × (MC₂ − MC₁) / (1 − MC₂)` ใส่ถุงซิป เขย่า แล้วเก็บในตู้เย็น 24–48 ชม. ให้ความชื้นกระจายเท่ากัน (เขย่าเป็นระยะ)
   - **ลดน้ำ:** อบที่ 40–50 °C แล้วชั่งจนได้ m_target
   - เป้าหมาย 5 ระดับ: ~9%, 11%, 12.5%, 15%, 20% (ครอบคลุมช่วงที่ "ยังไม่แห้ง" ด้วย)
3. ยืนยันค่าแต่ละขวดด้วย oven-dry ซ้ำ 1 ถาด ปิดผนึกขวดแล้วติดฉลาก MC และวันที่

**Fit model:**
- Two-point (เร็ว): `MC = MC_a + (raw − raw_a) × (MC_b − MC_a) / (raw_b − raw_a)` ใช้ได้เฉพาะในช่วงระหว่าง a กับ b
- Multi-point: ใช้ least squares `MC = a + b·raw + c·raw²` หรือ piecewise linear (lookup table) ซึ่งทนกว่าบน MCU
- Temperature compensation: วัดตัวอย่างเดิมที่ 2 อุณหภูมิ (เช่น 25 °C และ 40 °C ด้วยการอุ่นในกล่อง) แล้วหาค่า `k = Δraw/ΔT` จากนั้นใช้ `raw_25 = raw − k × (T − 25)` ก่อนเข้า model
- ใส่ค่า a, b, c, k ลง NVS และให้แก้ได้ผ่าน `cmd` topic (`{"set":{"cal_a":..,"cal_b":..}}`)
- รายงาน error: ใช้ leave-one-out กับตัวอย่าง แล้วบอก RMSE เป็น % MC บนสไลด์ (กรรมการชอบ)

**Quick calibration ที่งานแข่ง (≤20 นาที):**
1. ถ้าผู้จัดมีเครื่องวัดอ้างอิงหรือ sample ที่บอกค่า MC ให้ใช้เป็น**จุดยึด (offset)** 1–2 จุด แล้วปรับเฉพาะ `a` (offset) ของ model ที่ fit มาจากบ้าน
2. ถ้าได้เซนเซอร์คนละรุ่นกับที่ fit มา ให้ใช้ขวดอ้างอิง 3 ระดับที่เตรียมมา (11%, 12.5%, 15%) ทำ multi-point ใหม่
3. ทำ 2-point: ถ้วยเปล่า (air) และถ้วยใส่น้ำหรือเมล็ดชื้นมาก เพื่อ normalize ค่าเป็น 0–1 ก่อน (`norm = (raw_air − raw)/(raw_air − raw_wet)`) วิธีนี้ทำให้ model จากบ้านย้ายไปใช้กับเซนเซอร์ตัวใหม่ได้ดีขึ้น

### 5.6 วิธี C — Headspace RH (water activity proxy)
- ใส่เมล็ด ~2/3 ขวดโหล ปิดสนิทพร้อม SHT4x/SHT3x ข้างใน รอ 30–60 นาทีที่อุณหภูมิคงที่ ค่า RH/100 จะเข้าใกล้ **aw** ของเมล็ด
- ใช้ตัดสินความเสี่ยงรา: aw ≲ 0.62–0.65 ถือว่าปลอดภัยสำหรับการเก็บ, aw ≥ 0.80 เสี่ยงที่เชื้อราจะงอก ข้อมูลนี้ตอบ pain point "mold risk" ได้ตรงและเป็นจุดขายในการ pitch
- ข้อจำกัด: ช้า, ไวต่ออุณหภูมิ และเซนเซอร์ราคาถูกมีความคลาดเคลื่อน ±2–3% RH

---

## 6. Closed-loop Control & Alerts (PWM)

### 6.1 Actuators
| Actuator | วิธีขับ | ค่า PWM แนะนำ | หมายเหตุความปลอดภัย |
|---|---|---|---|
| พัดลม DC 12V 2-pin | Logic-level N-MOSFET (low-side) + flyback diode (1N5819/1N4007) + R gate 100 Ω + pulldown 10k | 1–5 kHz (หรือ 20–25 kHz ให้เงียบ), 8-bit | พัดลมเล็กมักไม่หมุนเมื่อ duty ต่ำกว่า ~30% ให้ kick 100% 300 ms ก่อน |
| พัดลม PC 4-pin | ต่อสาย PWM ตรงจาก GPIO (open-drain ใน fan, pull-up ภายใน) | **25 kHz** | ใช้สาย TACH อ่าน RPM ได้ (pull-up ไป 3.3V) |
| Heater (ฮีตเตอร์/หลอดอินฟราเรด) | **SSR** (ถ้าเป็น AC) หรือ MOSFET (ถ้าเป็น DC) | **time-proportioning** หน้าต่าง 2–10 s ทำใน software ไม่ใช้ LEDC | ต้องมี thermal fuse ทางฮาร์ดแวร์ และ cutoff ที่ max temp ใน software |
| Servo (ช่องระบาย/หลังคาเลื่อน) | ใช้ 5V จากแหล่งแยก + GND ร่วม | 50 Hz/16-bit, duty 3277–6554 | servo กินกระแส peak สูง → brownout ได้ |
| Buzzer passive | `ledcWriteTone(pin, 2000)` | — | active buzzer ใช้ digitalWrite ได้เลย |
| LED / RGB | `ledcWrite` | 5 kHz/8-bit | ใช้เป็นไฟสถานะ |

### 6.2 กลยุทธ์ควบคุมการตาก
- **Ventilation logic (ใช้ได้ทันที):** คำนวณ absolute humidity (AH) ภายในห้องหรือโดมตาก กับภายนอก โดยใช้ `AH = 216.7 × (RH/100 × 6.112 × e^(17.62T/(243.12+T))) / (273.15+T)` g/m³ แล้ว **เปิดพัดลมดูดอากาศเข้าเฉพาะเมื่อ AH_out < AH_in − δ** (δ ~1 g/m³ เป็น hysteresis) ถ้าภายนอกชื้นกว่า (หลังฝนตกหรือตอนกลางคืน) ให้ปิดและหมุนเวียนอากาศภายใน
- **Fan speed PI control:** setpoint คือ RH ภายในโดม ≤ 60–65% (หรือ VPD ≥ x kPa) ส่วน output คือ duty 30–100% ให้ทำแบบ anti-windup โดย clamp ค่า integral
- **Heater:** ถ้าใช้ heater ช่วย ให้คุมอุณหภูมิอากาศไม่ให้สูงเกินช่วงที่ปลอดภัยต่อคุณภาพ (โดยทั่วไปการตากเชิงกลมักใช้อุณหภูมิอากาศไม่เกินราว 40–50 °C แต่**ทีมต้องตรวจค่าจากเอกสารทางวิชาการ Robusta ก่อนใช้**) ใช้ hysteresis 1–2 °C และ min on/off time ≥ 30 s
- **Stop condition:** ถ้า `MC ≤ 12%` (จาก weight-loss) หรือ aw proxy ≤ 0.62 ให้ส่ง event `drying_done`
- **Mold risk index:** นับชั่วโมงสะสมที่ RH > 80% และ T อยู่ในช่วง 25–32 °C ขณะ MC > 13% ถ้าเกิน threshold (เช่น 6 ชม.) ให้ส่ง event `mold_risk` ไปพร้อมกับ LED แดงและ buzzer
- **Rain alert:** ใช้ DO ของ rain sensor ต่อ interrupt แล้วส่ง event ทันที (QoS1 ถ้า lib รองรับ) พร้อม buzzer เพื่อแจ้งให้เก็บกาแฟ

### 6.3 Safety checklist
- [ ] เมื่อเซนเซอร์อ่านค่าล้มเหลว (NaN/−127/85.0) ให้ **ปิด heater** (fail-safe) และส่ง event
- [ ] Heater มี hard limit ในโค้ด + thermal fuse/thermostat ทางฮาร์ดแวร์
- [ ] เมื่อ MQTT หลุด control loop ในเครื่องต้องทำงานต่อได้ (local autonomy)
- [ ] เมื่อบูต ทุก output ต้องเริ่มที่ OFF และไม่ใช้ขาที่เป็น HIGH ตอนบูตกับ heater/relay
- [ ] ไฟ AC ใช้ SSR/relay module ที่มี opto และกล่องปิดมิดชิด ห้ามมีสายเปลือย
- [ ] คำสั่ง `cmd` ที่เปลี่ยน setpoint ต้องมีการ clamp ช่วงค่า (เช่น fan 0–100, heater_max ≤ 55)

---

## 7. Firmware Template (Arduino core 3.x) — **UNTESTED**

ความสามารถ: WiFi + reconnect แบบ non-blocking, MQTT (PubSubClient) พร้อม LWT, telemetry JSON, command topic สำหรับ config (เก็บลง NVS), NTP, Task WDT, status LED, PWM พัดลมด้วย ventilation logic, plug-in sensor โดยเปิดปิดได้ด้วย `#define`

ใช้กับ: Arduino-ESP32 3.3.x, ArduinoJson 7.x, PubSubClient 2.8 (ถ้าเปิด option จะใช้ OneWire/DallasTemperature, Adafruit SHT4x, HX711 ด้วย)

```cpp
// ===== TESA Top Gun #20 — ESP32 Sensing Node Template =====
// STATUS: UNTESTED — compile & bench-test before use.
// Target: arduino-esp32 core 3.3.x, ArduinoJson 7.x, PubSubClient 2.8
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <Preferences.h>
#include <esp_task_wdt.h>
#include <time.h>
#include <math.h>

// ---------- enable/disable optional sensors ----------
#define USE_DS18B20   1
#define USE_SHT4X     0
#define USE_HX711     0
#define USE_ANALOG    1   // generic analog (capacitive moisture, LDR, MQ via divider)

#if USE_DS18B20
  #include <OneWire.h>
  #include <DallasTemperature.h>
#endif
#if USE_SHT4X
  #include <Wire.h>
  #include <Adafruit_SHT4x.h>
#endif
#if USE_HX711
  #include <HX711.h>
#endif

// ---------- user config (defaults; overridable via NVS/cmd) ----------
static const char* WIFI_SSID = "CHANGE_ME";
static const char* WIFI_PASS = "CHANGE_ME";
static const char* TEAM      = "team00";
static const char* NODE      = "esp1";
static const char* NTP_TZ    = "<+07>-7";

// ---------- pins (ESP32 classic DevKit) ----------
constexpr int PIN_LED      = 2;    // onboard LED (strapping pin, OK as output after boot)
constexpr int PIN_FAN_PWM  = 25;   // -> MOSFET gate
constexpr int PIN_BUZZER   = 26;
constexpr int PIN_ONEWIRE  = 4;    // DS18B20 + 4.7k pull-up to 3V3
constexpr int PIN_ANALOG   = 34;   // ADC1 only! input-only pin
constexpr int PIN_HX_DOUT  = 16;
constexpr int PIN_HX_SCK   = 17;

constexpr uint32_t FAN_PWM_FREQ = 25000;  // 25 kHz
constexpr uint8_t  FAN_PWM_RES  = 8;      // 0..255
constexpr uint32_t WDT_TIMEOUT_MS = 15000;

// ---------- runtime config ----------
struct Config {
  String   broker   = "192.168.1.10";
  uint16_t port     = 1883;
  String   user     = "";
  String   pass     = "";
  uint32_t interval = 5000;   // telemetry period (ms)
  int      fanMode  = 0;      // 0=auto, 1=manual
  int      fanPct   = 0;      // manual duty %
  float    rhMax    = 65.0f;  // auto: target max RH inside
  float    calA = 0, calB = 1, calK = 0; // MC = calA + calB*norm ; norm temperature-compensated
  float    hxFactor = 1.0f;
} cfg;

Preferences prefs;
WiFiClient  net;
PubSubClient mqtt(net);

String tBase, tStatus, tTele, tEvent, tCmd, tAck, tCfg, clientId;

#if USE_DS18B20
OneWire oneWire(PIN_ONEWIRE);
DallasTemperature ds(&oneWire);
#endif
#if USE_SHT4X
Adafruit_SHT4x sht4;
#endif
#if USE_HX711
HX711 scale;
#endif

// ---------- state ----------
enum class NetState { WIFI_DOWN, MQTT_DOWN, ONLINE };
NetState netState = NetState::WIFI_DOWN;
uint32_t lastWifiTry = 0, lastMqttTry = 0, mqttBackoff = 2000;
uint32_t lastTele = 0, lastLed = 0, seq = 0;
bool ledOn = false;
float lastAirRH = NAN, lastAirT = NAN;

// ---------- helpers ----------
void loadConfig() {
  prefs.begin("cfg", true);
  cfg.broker   = prefs.getString("broker", cfg.broker);
  cfg.port     = prefs.getUShort("port", cfg.port);
  cfg.user     = prefs.getString("user", cfg.user);
  cfg.pass     = prefs.getString("pass", cfg.pass);
  cfg.interval = prefs.getUInt("interval", cfg.interval);
  cfg.fanMode  = prefs.getInt("fanMode", cfg.fanMode);
  cfg.fanPct   = prefs.getInt("fanPct", cfg.fanPct);
  cfg.rhMax    = prefs.getFloat("rhMax", cfg.rhMax);
  cfg.calA     = prefs.getFloat("calA", cfg.calA);
  cfg.calB     = prefs.getFloat("calB", cfg.calB);
  cfg.calK     = prefs.getFloat("calK", cfg.calK);
  cfg.hxFactor = prefs.getFloat("hx", cfg.hxFactor);
  prefs.end();
}

void saveConfig() {
  prefs.begin("cfg", false);
  prefs.putString("broker", cfg.broker);
  prefs.putUShort("port", cfg.port);
  prefs.putString("user", cfg.user);
  prefs.putString("pass", cfg.pass);
  prefs.putUInt("interval", cfg.interval);
  prefs.putInt("fanMode", cfg.fanMode);
  prefs.putInt("fanPct", cfg.fanPct);
  prefs.putFloat("rhMax", cfg.rhMax);
  prefs.putFloat("calA", cfg.calA);
  prefs.putFloat("calB", cfg.calB);
  prefs.putFloat("calK", cfg.calK);
  prefs.putFloat("hx", cfg.hxFactor);
  prefs.end();
}

void setupWdt() {
  esp_task_wdt_config_t wcfg = {
    .timeout_ms = WDT_TIMEOUT_MS,
    .idle_core_mask = 0,          // don't watch idle tasks (avoid false trips)
    .trigger_panic = true          // reset on timeout
  };
  // TWDT is usually already started by IDF config in arduino-esp32 3.x
  if (esp_task_wdt_reconfigure(&wcfg) == ESP_ERR_INVALID_STATE) {
    esp_task_wdt_init(&wcfg);
  }
  esp_task_wdt_add(NULL);          // watch loopTask (current task)
}

uint32_t readAnalogMvAvg(int pin, int n = 32) {
  uint32_t sum = 0;
  for (int i = 0; i < n; i++) sum += analogReadMilliVolts(pin);
  return sum / n;
}

float absHumidity(float tC, float rh) {         // g/m^3
  float es = 6.112f * expf(17.62f * tC / (243.12f + tC));
  return 216.7f * (rh / 100.0f * es) / (273.15f + tC);
}

void setFanPct(int pct) {
  pct = constrain(pct, 0, 100);
  ledcWrite(PIN_FAN_PWM, (uint32_t)(pct * 255 / 100));
}

void publishEvent(const char* type, const char* msg) {
  JsonDocument d;
  d["type"] = type; d["msg"] = msg; d["ts"] = (uint32_t)time(nullptr);
  char buf[256]; size_t n = serializeJson(d, buf, sizeof(buf));
  mqtt.publish(tEvent.c_str(), (const uint8_t*)buf, n, false);
}

void publishConfig() {
  JsonDocument d;
  d["broker"] = cfg.broker; d["port"] = cfg.port; d["interval"] = cfg.interval;
  d["fanMode"] = cfg.fanMode; d["fanPct"] = cfg.fanPct; d["rhMax"] = cfg.rhMax;
  d["calA"] = cfg.calA; d["calB"] = cfg.calB; d["calK"] = cfg.calK; d["hx"] = cfg.hxFactor;
  char buf[384]; size_t n = serializeJson(d, buf, sizeof(buf));
  mqtt.publish(tCfg.c_str(), (const uint8_t*)buf, n, true);   // retained
}

// ---------- MQTT command handler ----------
// Example: {"id":"1","set":{"interval":2000,"fanMode":1,"fanPct":70}}
//          {"id":"2","cmd":"tare"} | {"id":"3","cmd":"reboot"} | {"id":"4","cmd":"beep"}
void onMessage(char* topic, byte* payload, unsigned int len) {
  JsonDocument in;
  DeserializationError err = deserializeJson(in, payload, len);
  JsonDocument ack;
  ack["id"] = in["id"] | "";
  if (err) { ack["ok"] = false; ack["err"] = err.c_str(); }
  else {
    bool changed = false, rebootReq = false;
    JsonObject set = in["set"];
    if (!set.isNull()) {
      if (set["interval"].is<uint32_t>()) { cfg.interval = constrain(set["interval"].as<uint32_t>(), 500u, 600000u); changed = true; }
      if (set["fanMode"].is<int>())       { cfg.fanMode  = constrain(set["fanMode"].as<int>(), 0, 1); changed = true; }
      if (set["fanPct"].is<int>())        { cfg.fanPct   = constrain(set["fanPct"].as<int>(), 0, 100); changed = true; }
      if (set["rhMax"].is<float>())       { cfg.rhMax    = constrain(set["rhMax"].as<float>(), 30.0f, 95.0f); changed = true; }
      if (set["calA"].is<float>())        { cfg.calA = set["calA"]; changed = true; }
      if (set["calB"].is<float>())        { cfg.calB = set["calB"]; changed = true; }
      if (set["calK"].is<float>())        { cfg.calK = set["calK"]; changed = true; }
      if (set["hx"].is<float>())          { cfg.hxFactor = set["hx"]; changed = true; }
      if (set["broker"].is<const char*>()) { cfg.broker = set["broker"].as<const char*>(); changed = true; rebootReq = true; }
      if (set["port"].is<uint16_t>())     { cfg.port = set["port"]; changed = true; rebootReq = true; }
    }
    const char* c = in["cmd"] | "";
    if (!strcmp(c, "reboot")) rebootReq = true;
#if USE_HX711
    if (!strcmp(c, "tare")) scale.tare(10);
#endif
    if (!strcmp(c, "beep")) { ledcWriteTone(PIN_BUZZER, 2000); delay(150); ledcWriteTone(PIN_BUZZER, 0); }
    if (changed) { saveConfig(); publishConfig(); }
    ack["ok"] = true;
    if (rebootReq) {
      char b[96]; size_t n = serializeJson(ack, b, sizeof(b));
      mqtt.publish(tAck.c_str(), (const uint8_t*)b, n, false);
      mqtt.loop(); delay(200); ESP.restart();
    }
  }
  char buf[128]; size_t n = serializeJson(ack, buf, sizeof(buf));
  mqtt.publish(tAck.c_str(), (const uint8_t*)buf, n, false);
}

// ---------- networking (non-blocking) ----------
void netTask() {
  uint32_t now = millis();
  if (WiFi.status() != WL_CONNECTED) {
    netState = NetState::WIFI_DOWN;
    if (now - lastWifiTry > 5000) {
      lastWifiTry = now;
      Serial.println("[wifi] reconnect");
      WiFi.disconnect();
      WiFi.begin(WIFI_SSID, WIFI_PASS);
    }
    return;
  }
  if (!mqtt.connected()) {
    netState = NetState::MQTT_DOWN;
    if (now - lastMqttTry > mqttBackoff) {
      lastMqttTry = now;
      Serial.printf("[mqtt] connect %s:%u ...\n", cfg.broker.c_str(), cfg.port);
      bool ok = mqtt.connect(clientId.c_str(),
                             cfg.user.length() ? cfg.user.c_str() : nullptr,
                             cfg.pass.length() ? cfg.pass.c_str() : nullptr,
                             tStatus.c_str(), 1, true, "offline", true);
      if (ok) {
        mqttBackoff = 2000;
        mqtt.publish(tStatus.c_str(), "online", true);
        mqtt.subscribe(tCmd.c_str(), 1);
        publishConfig();
        Serial.println("[mqtt] online");
      } else {
        Serial.printf("[mqtt] fail state=%d\n", mqtt.state());
        mqttBackoff = min<uint32_t>(mqttBackoff * 2, 30000);
      }
    }
    return;
  }
  netState = NetState::ONLINE;
  mqtt.loop();
}

void ledTask() {   // ONLINE: slow blink, MQTT_DOWN: fast blink, WIFI_DOWN: solid on
  uint32_t period = netState == NetState::ONLINE ? 1000 : (netState == NetState::MQTT_DOWN ? 150 : 0);
  if (period == 0) { digitalWrite(PIN_LED, HIGH); return; }
  if (millis() - lastLed > period) { lastLed = millis(); ledOn = !ledOn; digitalWrite(PIN_LED, ledOn); }
}

// ---------- sensors -> JSON (EDIT THIS for the unknown sensor) ----------
void readSensors(JsonObject s) {
#if USE_DS18B20
  ds.requestTemperatures();                 // non-blocking mode set in setup
  float tb = ds.getTempCByIndex(0);         // reads previous conversion
  if (tb == DEVICE_DISCONNECTED_C || tb == 85.0f) s["bean_t_c"] = nullptr; else s["bean_t_c"] = tb;
#endif
#if USE_SHT4X
  sensors_event_t hum, temp;
  if (sht4.getEvent(&hum, &temp)) {
    lastAirT = temp.temperature; lastAirRH = hum.relative_humidity;
    s["air_t_c"] = lastAirT; s["air_rh_pct"] = lastAirRH;
    s["air_ah_gm3"] = absHumidity(lastAirT, lastAirRH);
  }
#endif
#if USE_ANALOG
  uint32_t mv = readAnalogMvAvg(PIN_ANALOG, 64);
  s["an_mv"] = mv;
  // capacitive moisture example: normalize & calibrate (fill calA/calB/calK via cmd)
  float t = s["bean_t_c"].is<float>() ? s["bean_t_c"].as<float>() : 25.0f;
  float mvComp = mv - cfg.calK * (t - 25.0f);
  s["bean_mc_pct"] = cfg.calA + cfg.calB * mvComp;
#endif
#if USE_HX711
  if (scale.is_ready()) s["mass_g"] = scale.get_units(5);
#endif
}

void controlTask() {
  int pct;
  if (cfg.fanMode == 1) pct = cfg.fanPct;
  else if (isnan(lastAirRH)) pct = 0;                 // fail-safe: no data -> off (fan is low risk; heater must be OFF)
  else pct = lastAirRH > cfg.rhMax + 2 ? 100 : (lastAirRH < cfg.rhMax - 2 ? 0 : 50);  // simple hysteresis
  setFanPct(pct);
}

void telemetryTask() {
  if (millis() - lastTele < cfg.interval) return;
  lastTele = millis();
  JsonDocument d;
  d["seq"] = seq++;
  d["ts"] = (uint32_t)time(nullptr) > 1700000000 ? (uint32_t)time(nullptr) : 0;
  d["up_s"] = millis() / 1000;
  d["rssi"] = WiFi.RSSI();
  readSensors(d["s"].to<JsonObject>());
  controlTask();
  char buf[768];
  size_t n = serializeJson(d, buf, sizeof(buf));
  Serial.println(buf);
  if (netState == NetState::ONLINE) {
    if (!mqtt.publish(tTele.c_str(), (const uint8_t*)buf, n, false))
      Serial.println("[mqtt] publish failed (buffer size?)");
  }
}

// ---------- setup / loop ----------
void setup() {
  Serial.begin(115200);
  pinMode(PIN_LED, OUTPUT);
  ledcAttach(PIN_FAN_PWM, FAN_PWM_FREQ, FAN_PWM_RES);   // core 3.x API
  ledcAttach(PIN_BUZZER, 2000, 8);
  setFanPct(0);
  ledcWriteTone(PIN_BUZZER, 0);
  analogSetPinAttenuation(PIN_ANALOG, ADC_11db);

  loadConfig();

  String mac = WiFi.macAddress(); mac.replace(":", "");
  clientId = String("tesa-") + NODE + "-" + mac.substring(6);
  tBase   = String("tesa/") + TEAM + "/" + NODE;
  tStatus = tBase + "/status";  tTele = tBase + "/telemetry";
  tEvent  = tBase + "/event";   tCmd  = tBase + "/cmd";
  tAck    = tBase + "/cmd/ack"; tCfg  = tBase + "/config";

#if USE_DS18B20
  ds.begin(); ds.setResolution(12); ds.setWaitForConversion(false); ds.requestTemperatures();
#endif
#if USE_SHT4X
  Wire.begin(21, 22);
  if (!sht4.begin()) Serial.println("[sht4] not found");
  else { sht4.setPrecision(SHT4X_HIGH_PRECISION); sht4.setHeater(SHT4X_NO_HEATER); }
#endif
#if USE_HX711
  scale.begin(PIN_HX_DOUT, PIN_HX_SCK); scale.set_scale(cfg.hxFactor); scale.tare(10);
#endif

  WiFi.mode(WIFI_STA);
  WiFi.persistent(false);
  WiFi.setAutoReconnect(true);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  lastWifiTry = millis();
  configTzTime(NTP_TZ, "pool.ntp.org", "time.google.com");

  mqtt.setServer(cfg.broker.c_str(), cfg.port);   // NOTE: cfg.broker must outlive mqtt (it does: global)
  mqtt.setCallback(onMessage);
  mqtt.setBufferSize(1024);
  mqtt.setKeepAlive(15);
  mqtt.setSocketTimeout(3);

  setupWdt();
  Serial.println("[boot] ready");
}

void loop() {
  esp_task_wdt_reset();
  netTask();
  telemetryTask();
  ledTask();
}
```

**หมายเหตุ template:**
- `mqtt.connect()` ยังคง block ได้นาน 3 s (socket timeout) + TCP connect ซึ่งยังน้อยกว่า WDT 15 s
- DS18B20 อ่านแบบ async: ค่าที่ได้เป็นของรอบก่อนหน้า (ถ้า interval ≥ 1 s ก็พอ)
- เมื่อมีเซนเซอร์ใหม่: (1) เพิ่ม `#include` และ object (2) เพิ่ม init ใน `setup()` (3) เพิ่ม key ใน `readSensors()` แค่นี้พอ
- ถ้าใช้ WiFiManager ให้แทน `WiFi.begin(...)` ใน setup ด้วย `wm.autoConnect()` และเปลี่ยนการ reconnect ใน `netTask` เป็น `WiFi.reconnect()`

---

## 8. Debug Toolkit (ของที่ต้องเอาไป)

**Hardware**
- [ ] ESP32 DevKit **3–4 บอร์ด** (รุ่นเดียวกับที่ฝึก) ซึ่งแฟลช template + I2C scanner ไว้แล้ว และ 1 บอร์ดสำรองที่ยังไม่บัดกรี header
- [ ] สาย USB **ที่รับส่ง data ได้** (ทดสอบแล้ว ติดเทป "DATA") อย่างน้อย 4 เส้น ทั้ง micro-USB และ USB-C ตามบอร์ด
- [ ] ไดรเวอร์ CP210x/CH340 สำหรับ Windows/macOS เก็บไว้ใน USB แบบ offline
- [ ] มัลติมิเตอร์ (ที่วัด continuity และกระแส mA ได้)
- [ ] Logic analyzer 8ch 24 MHz (Saleae clone) + PulseView/sigrok สำหรับ debug I2C/1-Wire/HX711
- [ ] Breadboard 2 แผ่น, สายจั๊มเปอร์ M-M/M-F/F-F อย่างละ 40 เส้น, สาย Dupont แบบยาว
- [ ] ตัวต้านทาน: **4.7k (1-Wire/I2C), 10k (pull-up/divider), 1k/2k (5V→3.3V), 100 Ω (gate), 1 MΩ (RC/bleed)** ชุด kit ทั้งชุด
- [ ] ตัวเก็บประจุ 100 nF, 10 µF, 470–1000 µF
- [ ] Level shifter BSS138 4ch 2–3 ตัว
- [ ] Logic-level MOSFET (AO3400/IRLZ44N) และไดโอด 1N5819/1N4007, transistor 2N2222
- [ ] ADS1115 สำรอง (เผื่อ ADC ภายในไม่พอ)
- [ ] เซนเซอร์สำรองของเราเอง: SHT31/SHT4x, DS18B20 แบบกันน้ำ, HX711 + load cell 1–5 kg, capacitive soil v1.2 (ที่ตรวจแล้วว่าใช้ TLC555)
- [ ] Power bank 2 ก้อน + adapter 5V 2A + DC 12V สำหรับพัดลม
- [ ] หัวแร้ง ตะกั่ว ฟลักซ์ ที่ดูดตะกั่ว ท่อหด เทปพันสายไฟ สายรัด คีม คัตเตอร์
- [ ] ตาชั่งดิจิตอล 0.01 g + ตุ้มน้ำหนักมาตรฐาน (หรือขวดน้ำที่รู้มวล)
- [ ] **ขวดตัวอย่างเมล็ดอ้างอิงที่รู้ค่า MC** 3–5 ระดับ (ปิดผนึก) + ถ้วยวัดปริมาตรคงที่ + กรวย
- [ ] ขวดโหลปิดสนิทสำหรับวัด headspace RH, ซิลิกาเจล
- [ ] Router/AP พกพา (ตั้ง SSID เดียวกับที่ใช้ซ้อม) เผื่อ WiFi ในงานมีปัญหา
- [ ] แว่นขยาย/ไฟฉาย (อ่านเบอร์ชิป)

**Software (offline)**
- [ ] Arduino IDE 2.x + core esp32 เวอร์ชันที่ lock ไว้ และ zip ของโฟลเดอร์ libraries
- [ ] MQTT Explorer หรือ MQTTX, `mosquitto_sub/pub`
- [ ] Mosquitto broker บนโน้ตบุ๊ก (สำรองในกรณีที่ broker ของงานล่ม)
- [ ] I2C scanner sketch, ADC test sketch, PWM sweep sketch, DS18B20 address finder
- [ ] PDF datasheet ของเซนเซอร์ทุกตัวในตารางหัวข้อ 1 เก็บไว้ในโฟลเดอร์ offline

---

## 9. Drill Exercises — "Unknown sensor → MQTT ภายใน 60 นาที"

ให้ฝึกเป็นคู่ (คนหนึ่ง wiring/วัด อีกคนเขียนโค้ด) จับเวลาและบันทึกผลทุกครั้ง

| # | Drill | เป้าเวลา | Pass criteria |
|---|---|---|---|
| D1 | แฟลช template ใหม่บนบอร์ดเปล่า → `online` retained + telemetry dummy บน MQTT Explorer | **≤ 10 นาที** | เห็น LWT `offline` ภายใน ~1.5×keepalive เมื่อถอดไฟ |
| D2 | I2C sensor ไม่บอกชื่อ (ปิดฉลาก) → scanner → ระบุชิปจาก address → lib → MQTT | **≤ 20 นาที** | ค่า T/RH สมเหตุสมผลเมื่อเทียบกับเซนเซอร์อ้างอิง (±1 °C) |
| D3 | Analog sensor 5V (MQ-135 หรือ soil) → วัด Vmax ด้วยมิเตอร์ → ออกแบบ divider → ADC1 → mV | **≤ 15 นาที** | ไม่มีแรงดันเกิน 3.3V เข้าขา, ใช้ `analogReadMilliVolts` |
| D4 | DS18B20 3 ตัวบนสายเดียว → อ่าน address → publish แยก key | **≤ 15 นาที** | ไม่มีค่า 85/−127 |
| D5 | HX711 + load cell → tare + calibrate → `mass_g` → ส่ง factor ผ่าน `cmd` | **≤ 25 นาที** | error < 1% ที่ 500 g |
| D6 | Capacitive moisture + ขวดอ้างอิง 3 ระดับ → fit 2/3-point → ส่ง `bean_mc_pct` | **≤ 30 นาที** | ค่าที่ได้คลาดจากค่าจริงของขวดไม่เกิน ±1% MC |
| D7 | Fan PWM closed-loop: ตั้ง `rhMax` ผ่าน MQTT แล้วเป่าลมหายใจใส่เซนเซอร์ → พัดลมต้องทำงาน | **≤ 20 นาที** | ack ถูกต้องและพัดลมตอบสนองภายใน 1 interval |
| D8 | "Chaos test": ถอด router 30 s แล้วปิด broker 30 s ระหว่างทำงาน | **≤ 5 นาทีในการกู้** | กลับมา online เองโดยไม่ reset มือ และไม่มี WDT reset loop |
| D9 | **Full mock** (จำลองวันแข่ง): ผู้ฝึกสุ่มเซนเซอร์ 2 ตัวที่ไม่บอกชื่อ + topic/JSON schema ที่กำหนดเอง → ส่งข้อมูลถูก schema ให้ทีม Pi/backend | **≤ 60 นาที** | ทีม backend รับได้ทันทีโดยไม่ต้องแก้โค้ดฝั่งเขา |
| D10 | Brownout drill: จ่าย MQ-135 + servo + WiFi จาก USB สายยาว → ทำให้เกิด reset → แก้ด้วย C/แหล่งจ่ายแยก | ≤ 15 นาที | ทำงานต่อเนื่อง 10 นาทีโดยไม่ reset |

**เป้าหมายก่อนวันแข่ง (เหลือ ~5 สัปดาห์):**
- สัปดาห์ 1: D1–D4 ทุกคนในทีมต้องทำ D1 ได้
- สัปดาห์ 2: D5–D7 + เตรียมขวดตัวอย่างอ้างอิง MC (ใช้เวลาเตรียม 2–3 วัน)
- สัปดาห์ 3: D8, D10 + ตกลง topic/JSON schema กับทีม Pi และ backend
- สัปดาห์ 4–5: D9 อย่างน้อย 3 รอบ (สุ่มเซนเซอร์ใหม่ทุกครั้ง) และ lock เวอร์ชัน core/lib แล้วจัดของในหัวข้อ 8

### Checklist วันแข่ง (ก่อนเริ่มโจทย์)
- [ ] (วันงาน) ถาม SSID/รหัส, broker host/port/user, รูปแบบ topic ที่ผู้จัดกำหนด, NTP ใช้ได้ไหม
- [ ] ถ่ายรูปเซนเซอร์ที่ได้ แล้วระบุชิปในตาราง Quick Reference
- [ ] วัด Vout ของเซนเซอร์ก่อนต่อเข้า ESP32
- [ ] ตรวจว่าทุก analog อยู่ใน ADC1 และไม่ได้ใช้ strapping pin กับ output
- [ ] ทำ calibration offset กับตัวอ้างอิงของผู้จัดถ้ามี และบันทึกค่าลง NVS
- [ ] รัน chaos test (D8) อย่างย่อ 1 ครั้งก่อนส่งงาน

---

## 10. แหล่งอ้างอิง (Sources)

**ESP32 / Arduino core**
- Arduino-ESP32 migration guide 2.x → 3.0: https://docs.espressif.com/projects/arduino-esp32/en/latest/migration_guides/2.x_to_3.0.html
- Arduino-ESP32 LEDC API: https://docs.espressif.com/projects/arduino-esp32/en/latest/api/ledc.html
- Arduino-ESP32 ADC API: https://docs.espressif.com/projects/arduino-esp32/en/latest/api/adc.html
- Arduino-ESP32 releases (3.3.12 / IDF 5.5.5): https://github.com/espressif/arduino-esp32/releases
- ESP-IDF ADC oneshot (ADC2 shared with Wi-Fi): https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/adc/adc_oneshot.html
- ESP-IDF Watchdogs (TWDT, `esp_task_wdt_reconfigure`): https://docs.espressif.com/projects/esp-idf/en/v5.1/esp32c3/api-reference/system/wdts.html
- ESP32 3.0.x watchdog discussion: https://forum.arduino.cc/t/watchdog-doesnt-work-with-esp32-3-0-1/1270966 , https://esp32.com/viewtopic.php?p=133247
- ESP32 pinout reference: https://randomnerdtutorials.com/esp32-pinout-reference-gpios/
- PlatformIO + Arduino-ESP32 3.x (pioarduino): https://community.platformio.org/t/how-to-make-sure-i-have-the-latest-arduino-esp32-core/44760 , https://github.com/sivar2311/platform-espressif32-versions

**MQTT / JSON**
- PubSubClient (unmaintained notice, limits): https://github.com/knolleary/pubsubclient
- arduino-mqtt (256dpi): https://github.com/256dpi/arduino-mqtt
- espMqttClient (bertmelis): https://github.com/bertmelis/espMqttClient
- ArduinoJson v6 → v7 upgrade: https://arduinojson.org/v7/how-to/upgrade-from-v6/

**Sensors**
- Capacitive soil moisture v1.2 flaws: https://www.makerguides.com/capacitive-soil-moisture-sensor-with-arduino/ , https://www.atomic14.com/esp32/sensors/capacitive-soil/
- Capacitive sensor calibration (thermo-gravimetric): https://reference-global.com/article/10.2478/johh-2022-0014
- ESP32 + capacitive sensor for coffee beans (Polije thesis): https://sipora.polije.ac.id/35295/
- Bean moisture meter concept (FDC1004): https://forum.digikey.com/t/project-preview-sikwal-beansense-a-compact-coffee-bean-moisture-meter/71477

**Coffee moisture / quality**
- ISO 6673:2003 Green coffee — loss in mass at 105 °C: https://www.iso.org/standard/38375.html ; ISO 6673:1983: https://www.iso.org/standard/13101.html ; scope summary: https://www.technickenormy.cz/en/iso-6673-green-coffee-determination-of-loss-in-mass-at-105-degrees-c/
- ICO Resolution 420 (8–12.5% moisture, ISO 6673): https://ico.org/wp-content/documents/iccres420e.pdf
- Water activity vs moisture in coffee: https://aqualab.com/learn/water-activity-better-moisture-metric-coffee-and-tea
- Cenicafé (aw, OTA, mechanical drying interruptions): https://publicaciones.cenicafe.org/index.php/cenicafe/article/view/1172 , https://www.cenicafe.org/es/publications/Articulo_Inocuidad.pdf

> **สิ่งที่ยังไม่ได้ยืนยันจากแหล่งปฐมภูมิ (ต้องตรวจเพิ่ม):** ช่วงอุณหภูมิอากาศที่ปลอดภัยสำหรับการตาก Robusta แบบเชิงกล, ค่าความแม่นยำของโมดูลเลียนแบบ, ชื่อ library บางตัวที่อ้างจากความรู้เดิม (BH1750 / MQUnifiedsensor / Sensirion) ซึ่งต้องค้นใน Library Manager อีกครั้ง, และสถานะปัจจุบันของ ISO 6673
