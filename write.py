from machine import Pin, SPI
import mfrc522
import utime
import binascii # สำหรับแปลง bytes เป็น hex string ถ้าต้องการ

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
# นี่คือค่า 6 ไบต์ของ Key A ที่เป็นค่าเริ่มต้น
DEFAULT_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

# ข้อมูลที่จะเขียน (ต้องมีขนาด 16 ไบต์)
# ตัวอย่าง: "Hello World!Pico" (16 characters = 16 bytes)
# คุณสามารถแปลง String เป็น bytes ได้
data_to_write_str = "Hello Pico RFID!"
# ตรวจสอบความยาว ถ้าสั้นกว่า 16 ไบต์ให้เติมช่องว่าง ถ้าเกินให้ตัดออก
data_to_write_bytes = bytearray(data_to_write_str.encode('utf-8'))
if len(data_to_write_bytes) < 16:
    data_to_write_bytes.extend(bytearray([0x00] * (16 - len(data_to_write_bytes))))
elif len(data_to_write_bytes) > 16:
    data_to_write_bytes = data_to_write_bytes[:16]

# กำหนด Sector และ Block ที่ต้องการเขียน
# เลือก Sector 1, Block 0 (Block 0, 1, 2 ของ Sector 1 ใช้เก็บข้อมูลได้)
# หลีกเลี่ยง Sector 0, Block 0 เพราะเป็น Manufacturer Block (UID)
# หลีกเลี่ยง Block 3 ของทุก Sector เพราะเป็น Sector Trailer
SECTOR_TO_WRITE = 1
BLOCK_TO_WRITE = 0 # Block 0, 1, หรือ 2 ของ Sector 1


print("--- RFID Reader/Writer Started ---")
print("Scan an RFID tag to write data...")

def write_data_to_card(uid, sector, block, data, key):
    """
    Function to write data to a specific block on an RFID card.
    uid: The UID of the card (list of 4 bytes).
    sector: The sector number to write to.
    block: The block number within the sector (0, 1, or 2 for data blocks).
    data: A bytearray of 16 bytes to write.
    key: The 6-byte key for authentication (Key A).
    """
    print(f"\nAttempting to write to Sector {sector}, Block {block}...")

    # Calculate absolute block address
    # For Mifare Classic 1K, blocks are 0-3 in each sector.
    # Sector 0: Block 0,1,2,3
    # Sector 1: Block 4,5,6,7
    # ...
    # Sector N: Block (N*4), (N*4)+1, (N*4)+2, (N*4)+3
    absolute_block_address = (sector * 4) + block

    # Authenticate with Key A
    # The authenticate method requires the absolute block address of the Sector Trailer
    # (which is Block 3 of the current sector)
    sector_trailer_block_address = (sector * 4) + 3

    print(f"Authenticating Sector Trailer Block {sector_trailer_block_address} with Key A...")
    status = rdr.select_tag(uid) # Select the tag first
    if status == rdr.OK:
        status = rdr.authenticate(rdr.PICC_AUTHENT1A, sector_trailer_block_address, key, uid)
        if status == rdr.OK:
            print("Authentication successful!")

            # Write data
            print(f"Writing data to block {absolute_block_address}: {binascii.hexlify(data).decode('utf-8')}")
            status = rdr.write(absolute_block_address, list(data)) # Library expects list of ints

            if status == rdr.OK:
                print("Data written successfully!")
                # Read back to verify
                print("Reading back to verify...")
                (stat, read_data_list) = rdr.read(absolute_block_address)
                if stat == rdr.OK:
                    read_data_bytes = bytearray(read_data_list)
                    print(f"Data read back: {binascii.hexlify(read_data_bytes).decode('utf-8')} / {read_data_bytes.decode('utf-8', 'ignore')}")
                else:
                    print("Error reading back data.")
            else:
                print("Error writing data.")
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

                # เรียกฟังก์ชันเขียนข้อมูล
                write_data_to_card(raw_uid, SECTOR_TO_WRITE, BLOCK_TO_WRITE, data_to_write_bytes, DEFAULT_KEY)

                utime.sleep_ms(2000) # หน่วงเวลาหลังจากเขียนข้อมูล เพื่อไม่ให้เขียนซ้ำทันที

    except Exception as e:
        print(f"An error occurred: {e}")
        utime.sleep_ms(100) # หน่วงเวลาหากเกิดข้อผิดพลาด

    utime.sleep_ms(50) # หน่วงเวลารอบ Loop สั้นๆ
