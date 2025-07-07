from machine import Pin, SPI
import mfrc522
import utime

# --- กำหนดขา SPI และ RC522 ---
# *** ปรับค่าเหล่านี้ให้ถูกต้องตามการเชื่อมต่อของคุณ ***
# สำหรับ Raspberry Pi Pico (SPI0):
sck_pin = 18    # SCK0
mosi_pin = 19   # MOSI0
miso_pin = 16   # MISO0
sda_pin = 17    # SDA (Chip Select)
rst_pin = 22    # RST (Reset)

# สำหรับ ESP32 (ตัวอย่างขา SPI2/VSPI):
# sck_pin = 18
# mosi_pin = 23
# miso_pin = 19
# sda_pin = 5
# rst_pin = 27


# Initialise SPI Bus
# สำหรับ Pico ใช้ SPI(0), สำหรับ ESP32/ESP8266 อาจเป็น SPI(1) หรือ SPI(2)
spi = SPI(0, baudrate=2500000, polarity=0, phase=0,
          sck=Pin(sck_pin, Pin.OUT),
          mosi=Pin(mosi_pin, Pin.OUT),
          miso=Pin(miso_pin, Pin.IN))

# Initialise RC522
rdr = mfrc522.MFRC522(spi, Pin(sda_pin), Pin(rst_pin))

# --- กำหนดขา GPIO สำหรับ Relay ---
# *** เปลี่ยน GP0 เป็นขาที่คุณต่อ Relay จริงๆ ***
RELAY_PIN = 0 # เช่น GP0 (Pin 1 บน Raspberry Pi Pico)
relay = Pin(RELAY_PIN, Pin.OUT)
relay.value(0) # ตรวจสอบว่า Relay เริ่มต้นที่สถานะปิด (0 = OFF, 1 = ON)
               # บาง Relay Module อาจเป็น Active LOW (0 = ON, 1 = OFF)
               # ให้ปรับตาม Relay ของคุณ

# --- กำหนด UID ของบัตรที่ได้รับอนุญาต ---
# *** สำคัญ: คุณต้องเปลี่ยนค่านี้เป็น UID ของบัตรที่คุณต้องการให้เปิด Relay ได้ ***
# วิธีหา UID: รันโค้ดอ่าน UID ก่อน แล้วนำค่า UID ที่ได้มาใส่ที่นี่
AUTHORIZED_UIDS = [
    "1234abcd", # ตัวอย่าง UID ของบัตรที่ 1
    "efgh5678", # ตัวอย่าง UID ของบัตรที่ 2
    # เพิ่ม UID อื่นๆ ที่ได้รับอนุญาตได้ที่นี่
]

# ระยะเวลาที่ Relay จะเปิด (เป็นวินาที)
RELAY_ON_DURATION = 2 # เปิด Relay 2 วินาที


print("--- RFID Access Control System Started ---")
print("Scan an RFID tag to control the Relay...")

while True:
    try:
        (stat, tag_type) = rdr.request(rdr.REQIDL)

        if stat == rdr.OK:
            (stat, raw_uid) = rdr.anticoll()

            if stat == rdr.OK:
                uid_str = ("%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
                print("\n--- New card detected! ---")
                print("Card type: 0x%02x" % tag_type)
                print(f"Card UID: {uid_str}")

                # ตรวจสอบ UID กับรายการที่ได้รับอนุญาต
                if uid_str in AUTHORIZED_UIDS:
                    print("Access Granted! Opening Relay...")
                    relay.value(1) # เปิด Relay (ปรับเป็น 0 ถ้าเป็น Active LOW)
                    utime.sleep(RELAY_ON_DURATION) # เปิดค้างไว้ตามเวลาที่กำหนด
                    relay.value(0) # ปิด Relay (ปรับเป็น 1 ถ้าเป็น Active LOW)
                    print("Relay closed.")
                else:
                    print("Access Denied! Unknown card.")

                utime.sleep_ms(1000) # หน่วงเวลาหลังจากประมวลผลบัตร เพื่อไม่ให้สแกนซ้ำทันที

    except Exception as e:
        print(f"An error occurred: {e}")
        utime.sleep_ms(100) # หน่วงเวลาหากเกิดข้อผิดพลาด

    utime.sleep_ms(50) # หน่วงเวลารอบ Loop สั้นๆ
