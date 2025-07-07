from machine import Pin, SPI
import mfrc522
import utime
import binascii # สำหรับแปลง bytes เป็น hex string

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

# Default Key (สำหรับบัตร Mifare Classic ที่ยังไม่ถูกเปลี่ยน Key)
DEFAULT_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

# กำหนด Sector และ Block ที่ต้องการอ่าน
# ต้องเป็น Block ที่มีข้อมูลอยู่ (Block 0, 1, หรือ 2)
# หลีกเลี่ยง Block 3 (Sector Trailer) หากไม่ต้องการข้อมูล Key/Access Bits
# ในตัวอย่างนี้จะอ่านจาก Sector 1, Block 0 ซึ่งเราเคยเขียนไปในโค้ดตัวอย่างที่แล้ว
SECTOR_TO_READ = 1
BLOCK_TO_READ = 0 # Block 0, 1, หรือ 2 ของ Sector 1


print("--- RFID Reader Started ---")
print("Scan an RFID tag to read data...")

def read_data_from_card(uid, sector, block, key):
    """
    Function to read data from a specific block on an RFID card.
    uid: The UID of the card (list of 4 bytes).
    sector: The sector number to read from.
    block: The block number within the sector (0, 1, or 2 for data blocks, or 3 for sector trailer).
    key: The 6-byte key for authentication (Key A).
    """
    print(f"\nAttempting to read from Sector {sector}, Block {block}...")

    # Calculate absolute block address
    absolute_block_address = (sector * 4) + block

    # Authenticate with Key A
    # The authenticate method requires the absolute block address of the Sector Trailer
    sector_trailer_block_address = (sector * 4) + 3

    print(f"Authenticating Sector Trailer Block {sector_trailer_block_address} with Key A...")
    status = rdr.select_tag(uid) # Select the tag first
    if status == rdr.OK:
        status = rdr.authenticate(rdr.PICC_AUTHENT1A, sector_trailer_block_address, key, uid)
        if status == rdr.OK:
            print("Authentication successful!")

            # Read data
            print(f"Reading data from block {absolute_block_address}...")
            (stat, read_data_list) = rdr.read(absolute_block_address)

            if stat == rdr.OK:
                read_data_bytes = bytearray(read_data_list)
                print(f"Data read: {binascii.hexlify(read_data_bytes).decode('utf-8')}")
                try:
                    # ลองแปลงเป็น String, หากมี non-printable characters อาจมีปัญหา
                    print(f"Decoded data: {read_data_bytes.decode('utf-8', 'ignore')}")
                except UnicodeDecodeError:
                    print("Could not decode data as UTF-8.")
            else:
                print("Error reading data from block.")
        else:
            print("Authentication failed!")
            print("Please ensure the card is a Mifare Classic 1K and the key is correct.")
    else:
        print("Error selecting tag for authentication.")


while True:
    try:
        (stat, tag_type) = rdr.request(rdr.REQIDL)

        if stat == rdr.OK:
            (stat, raw_uid) = rdr.anticoll()

            if stat == rdr.OK:
                uid_str = ("%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
                print("\n--- New card detected! ---")
                print("Card type: 0x%02x" % tag_type)
                print(f"Card UID: {uid_str} (raw: {raw_uid})")

                # เรียกฟังก์ชันอ่านข้อมูล
                read_data_from_card(raw_uid, SECTOR_TO_READ, BLOCK_TO_READ, DEFAULT_KEY)

                utime.sleep_ms(2000) # หน่วงเวลาหลังจากอ่านข้อมูล

    except Exception as e:
        print(f"An error occurred: {e}")
        utime.sleep_ms(100) # หน่วงเวลาหากเกิดข้อผิดพลาด

    utime.sleep_ms(50) # หน่วงเวลารอบ Loop สั้นๆ
