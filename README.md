## โค้ด MicroPython สำหรับ Raspberry Pi Pico (RFID-RC522)

สิ่งที่คุณต้องมี:
  Raspberry Pi Pico ที่ลงเฟิร์มแวร์ MicroPython แล้ว
  โมดูล RFID-RC522
  การเชื่อมต่อ (Wiring):
  คุณจะต้องเชื่อมต่อโมดูล RC522 เข้ากับขา SPI ของ Pico

ตัวอย่างการเชื่อมต่อ (Pico SPI0 - แนะนำ):

RC522 VCC -> Pico 3V3_OUT (Pin 36)

RC522 RST -> Pico GP22 (Pin 29, สามารถใช้ขา GPIO อื่นๆ ได้ตามต้องการ)

RC522 GND -> Pico GND (Pin 3 หรือ 8 หรือ 13 หรือ 18 หรือ 23 หรือ 28 หรือ 33 หรือ 38)

RC522 MOSI -> Pico GP19 (MOSI0) (Pin 25)

RC522 MISO -> Pico GP16 (MISO0) (Pin 21)

RC522 SCK -> Pico GP18 (SCK0) (Pin 24)

RC522 SDA (SS) -> Pico GP17 (CS0) (Pin 22, หรือขา GPIO อื่นๆ ที่เลือกเป็น Chip Select)

RC522 IRQ -> (ไม่ต้องต่อก็ได้ ถ้าไม่ใช้ Interrupt)

หมายเหตุ: Raspberry Pi Pico มี SPI bus สองชุดคือ SPI0 และ SPI1. โดยทั่วไปจะนิยมใช้ SPI0 เพราะขา GPIO อยู่ใกล้กัน.
