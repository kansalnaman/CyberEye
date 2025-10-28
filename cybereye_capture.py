# cybereye_capture.py
# CyberEye — Immediate capture on unlock + email (with small cooldown)
# Usage: python cybereye_capture.py

import cv2
import os
import time
from datetime import datetime, timedelta
import sys
import yagmail

# ---------- CONFIG (env vars recommended) ----------
YOUR_EMAIL = os.environ.get("CYBEREYE_EMAIL")               # set via setx
APP_PASSWORD = os.environ.get("CYBEREYE_APP_PASSWORD")      # set via setx (app password, no spaces)
TO_EMAIL = YOUR_EMAIL
CAPTURE_DIR = "captures"
LOG_FILE = "cyber_eye.log"
COOLDOWN_SECONDS = 30   # don't send another alert if last alert was within this many seconds
# ---------------------------------------------------

SEND_EMAIL = True if (YOUR_EMAIL and APP_PASSWORD) else False

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

def ensure_dir():
    if not os.path.exists(CAPTURE_DIR):
        os.makedirs(CAPTURE_DIR)

def last_alert_time():
    """Return datetime of last saved capture (if any) to implement cooldown."""
    if not os.path.exists(CAPTURE_DIR):
        return None
    files = [os.path.join(CAPTURE_DIR, f) for f in os.listdir(CAPTURE_DIR) if f.lower().endswith(".jpg")]
    if not files:
        return None
    latest = max(files, key=os.path.getmtime)
    return datetime.fromtimestamp(os.path.getmtime(latest))

def should_send_alert():
    last = last_alert_time()
    if last is None:
        return True
    diff = datetime.now() - last
    return diff.total_seconds() >= COOLDOWN_SECONDS

def capture_photo(wait_seconds=0.3, warmup_frames=5):
    ensure_dir()
    log("Opening camera...")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    time.sleep(wait_seconds)
    if not cap.isOpened():
        log("ERROR: Camera not available or blocked.")
        return None
    frame = None
    for i in range(warmup_frames):
        ret, frame = cap.read()
        if not ret:
            log(f"[warn] warmup frame {i} failed")
        time.sleep(0.03)
    ret, frame = cap.read()
    if not ret or frame is None:
        log("ERROR: Could not capture frame.")
        cap.release()
        return None
    filename = os.path.join(CAPTURE_DIR, f"intruder_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
    saved = cv2.imwrite(filename, frame)
    cap.release()
    if saved:
        log(f"Photo captured and saved: {filename}")
        return filename
    else:
        log("ERROR: Failed to write image file.")
        return None

def send_email(photo_path):
    if not SEND_EMAIL:
        log("Email not configured (env vars missing). Skipping email.")
        return False
    try:
        log("Sending email...")
        yag = yagmail.SMTP(YOUR_EMAIL, APP_PASSWORD)
        subject = "⚠️ Cyber Eye Alert: Unlock detected"
        body = f"CyberEye detected an unlock at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."
        yag.send(to=TO_EMAIL, subject=subject, contents=body, attachments=photo_path)
        log(f"Email sent to {TO_EMAIL}")
        return True
    except Exception as e:
        log(f"ERROR sending email: {e}")
        return False

if __name__ == "__main__":
    log("CyberEye triggered.")
    # Check cooldown to avoid duplicate alerts if recent capture exists
    if not should_send_alert():
        log(f"Alert suppressed: within cooldown of {COOLDOWN_SECONDS}s.")
        sys.exit(0)

    photo = capture_photo()
    if photo:
        send_email(photo)
    else:
        log("No photo captured.")
