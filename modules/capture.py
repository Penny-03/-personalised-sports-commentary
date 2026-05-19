import mss
from PIL import Image
import time, base64, io

def capture_frame():
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # primary screen
        shot = sct.grab(monitor)
        img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
        img = img.resize((1280, 720))  # reduce size for API
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=75)
        return base64.b64encode(buf.getvalue()).decode()

if __name__ == "__main__":
    while True:
        frame_b64 = capture_frame()
        print(f"Captured frame: {len(frame_b64)} chars")
        time.sleep(30)
