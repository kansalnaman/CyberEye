# cybereye.py
import cv2
import yagmail
from datetime import datetime, timedelta
import os
import time
import sys

# ---------- CONFIG ----------
YOUR_EMAIL = "Write mail from which you want to sent a mail"       # apna gmail
APP_PASSWORD = "Your App Password here"  # Gmail App Password (16 chars)
TO_EMAIL = "On this mail you will receive an alert"         # jahan alert chahiye
CAPTURE_DIR = "captures"
DAYS_TO_KEEP = 7                         # images automatically delete after X days
# ----------------------------

def ensure_dir():
    if not os.path.exists(CAPTURE_DIR):
        os.makedirs(CAPTURE_DIR)

def capture_photo():
    ensure_dir()
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # use DirectShow on Windows
    if not cap.isOpened():
        print("ERROR: Webcam not available.")
        return None
    # small warm-up
    for _ in range(5):
        ret, frame = cap.read()
    ret, frame = cap.read()
    cap.release()
    if not ret:
        print("ERROR: Could not read frame from webcam.")
        return None
    filename = os.path.join(CAPTURE_DIR, f"intruder_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
    cv2.imwrite(filename, frame)
    print("Photo saved:", filename)
    return filename

def send_email(photo_path):
    try:
        yag = yagmail.SMTP(YOUR_EMAIL, APP_PASSWORD)
        subject = "⚠️ Cyber Eye Alert: Someone opened your laptop!"
        body = f"Someone opened your laptop at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.\n\nThis is an automated alert from Cyber Eye."
        yag.send(to=TO_EMAIL, subject=subject, contents=body, attachments=photo_path)
        print("Alert email sent.")
    except Exception as e:
        print("ERROR sending email:", e)

def cleanup_old_files():
    cutoff = datetime.now() - timedelta(days=DAYS_TO_KEEP)
    for fname in os.listdir(CAPTURE_DIR) if os.path.exists(CAPTURE_DIR) else []:
        path = os.path.join(CAPTURE_DIR, fname)
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(path))
            if mtime < cutoff:
                os.remove(path)
                print("Deleted old file:", path)
        except Exception as e:
            print("Cleanup error for", path, e)

# ---------- MAIN ----------
if __name__ == "__main__":
    # This script when run will take a photo and send email.
    # You can place it to run at startup or call it from an event.
    photo = capture_photo()
    if photo:
        send_email(photo)
    cleanup_old_files()
