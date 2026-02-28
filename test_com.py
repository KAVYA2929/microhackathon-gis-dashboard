import serial
import time

try:
    with open('com_output_clean.txt', 'w', encoding='utf-8') as f:
        ser = serial.Serial('COM3', 115200, timeout=1)
        f.write("Connected to COM3 at 115200.\n")
        time.sleep(2) # wait for boot
        start_time = time.time()
        while time.time() - start_time < 3:
            raw = ser.readline()
            if raw:
                try:
                    f.write(raw.decode('utf-8', errors='ignore').strip() + "\n")
                except:
                    pass
        ser.close()
except Exception as e:
    print(f"Error: {e}")
