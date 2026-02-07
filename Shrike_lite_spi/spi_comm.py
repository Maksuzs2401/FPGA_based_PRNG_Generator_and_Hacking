import machine
import struct
import time

# --- SETUP ---
SCK, CS, MOSI, MISO = 2, 1, 3, 0
cs = machine.Pin(CS, machine.Pin.OUT, value=1)
spi = machine.SPI(0, baudrate=1_000_000, polarity=0, phase=0, bits=8, firstbit=machine.SPI.MSB,
                  sck=machine.Pin(SCK), mosi=machine.Pin(MOSI), miso=machine.Pin(MISO))

def spi_transfer_u64(val_int):
    tx_data = struct.pack('>Q', val_int)
    rx_data = bytearray(8)
    cs.value(0)
    spi.write_readinto(tx_data, rx_data)
    cs.value(1)
    return struct.unpack('>Q', rx_data)[0]

# --- CAPTURE SEQUENCE ---
KEY = 0x123456789ABCDEF0
spi_transfer_u64(KEY)
time.sleep_ms(1)

print("Capturing 64 steps of history...")
captured_ints = []

# 1. Capture Step 0
val = spi_transfer_u64(0)
captured_ints.append(val)

# 2. Capture Steps 1-63
# We need this long history to let the 'hidden' lower bits ripple up to the window.
for i in range(63):
    val = spi_transfer_u64(0)
    captured_ints.append(val)

print(f"Captured {len(captured_ints)} steps.")

# --- SAVE TO FILE ---
FILENAME = "fpga_dump.txt"
print(f"Saving to '{FILENAME}'...")

with open(FILENAME, "w") as f:
    # Save as comma-separated numbers
    f.write(",".join(str(x) for x in captured_ints))

print("Done.")