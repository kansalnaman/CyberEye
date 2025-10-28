# cybereye_face.py
import cv2
import os
import time
from datetime import datetime
import sys
import yagmail
import numpy as np
import requests  # ✅ added for location

# -------- CONFIG ----------
CAPTURE_DIR = "captures"
TRAINER_FILE = "trainer.yml"
CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
OWNER_ID = 1
CONFIDENCE_THRESHOLD = 60   # lower = stricter (0 best)
COOLDOWN_SECONDS = 5
YOUR_EMAIL = os.environ.get("CYBEREYE_EMAIL")
APP_PASSWORD = os.environ.get("CYBEREYE_APP_PASSWORD")
TO_EMAIL = YOUR_EMAIL
SEND_EMAIL = True if (YOUR_EMAIL and APP_PASSWORD) else False
LOG_FILE = "cyber_eye.log"
# --------------------------

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

def ensure_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)

def last_alert_time():
    if not os.path.exists(CAPTURE_DIR):
        return None
    files = [os.path.join(CAPTURE_DIR, f) for f in os.listdir(CAPTURE_DIR) if f.lower().endswith(".jpg")]
    if not files:
        return None
    latest = max(files, key=os.path.getmtime)
    return datetime.fromtimestamp(os.path.getmtime(latest))

# ✅ STEP 1: Get Location function
def get_location():
    try:
        res = requests.get("https://ipinfo.io/json", timeout=8)
        if res.status_code == 200:
            data = res.json()
            city = data.get("city", "Unknown City")
            region = data.get("region", "Unknown Region")
            country = data.get("country", "Unknown Country")
            loc = data.get("loc", "0,0")
            location_info = f"{city}, {region}, {country} (Lat/Long: {loc})"
            log(f"Fetched location: {location_info}")
            return location_info
        else:
            log(f"Location fetch failed - status {res.status_code}")
            return "Location unavailable"
    except Exception as e:
        log(f"Location fetch error: {e}")
        return "Location unavailable"


def send_email(photo_path):
    if not SEND_EMAIL:
        log("Email not configured. Skipping email.")
        return False
    try:
        log("Sending email...")
        yag = yagmail.SMTP(YOUR_EMAIL, APP_PASSWORD)

        # ✅ STEP 2: include location in mail body
        location_info = get_location()
        time.sleep(3)  # wait a bit to ensure location fetched properly

        subj = "⚠️ Cyber Eye Alert - Stranger detected"
        body = (
            f"CyberEye detected an unrecognized face at "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.\n\n"
            f"🌍 Approximate Location: {location_info}\n\n"
            f"📸 Attached is the captured image."
        )

        yag.send(to=TO_EMAIL, subject=subj, contents=body, attachments=photo_path)
        log("Email sent successfully (with location).")
        return True
    except Exception as e:
        log(f"Email error: {e}")
        return False

def capture_frame_and_check():
    if not os.path.exists(TRAINER_FILE):
        log(f"[ERROR] Trainer file {TRAINER_FILE} missing. Run train_model.py first.")
        return

    face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(TRAINER_FILE)

    ensure_dir(CAPTURE_DIR)
    log("Opening camera for recognition...")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    time.sleep(0.25)
    if not cap.isOpened():
        log("ERROR: Camera not available.")
        return

    for _ in range(3):
        ret, frame = cap.read()
    ret, frame = cap.read()
    cap.release()
    if not ret or frame is None:
        log("ERROR: Failed to capture frame.")
        return

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(40,40))
    if len(faces) == 0:
        log("No face detected in frame → treat as stranger.")
        fname = os.path.join(CAPTURE_DIR, f"intruder_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
        cv2.imwrite(fname, frame)
        send_email(fname)
        return

    owner_found = False
    for (x,y,w,h) in faces:
        face_img = gray[y:y+h, x:x+w]
        try:
            pred_id, confidence = recognizer.predict(face_img)
            log(f"Predict -> id: {pred_id}, confidence: {confidence:.2f}")
            if pred_id == OWNER_ID and confidence <= CONFIDENCE_THRESHOLD:
                owner_found = True
                break
        except Exception as e:
            log(f"[warn] recognizer.predict error: {e}")

    if owner_found:
        log("Owner recognized → skipping alert.")
        return
    else:
        log("Owner NOT recognized → saving photo & sending alert.")
        fname = os.path.join(CAPTURE_DIR, f"intruder_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
        cv2.imwrite(fname, frame)
        last = last_alert_time()
        if last and (datetime.now() - last).total_seconds() < COOLDOWN_SECONDS:
            log("Suppressed: within cooldown period.")
            return
        send_email(fname)
        return

if __name__ == "__main__":
    capture_frame_and_check()
