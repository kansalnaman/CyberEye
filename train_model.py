# train_model.py
import cv2
import os
import numpy as np

DATASET_DIR = "dataset"     # folder where your 7 phone images are
TRAINER_FILE = "trainer.yml"
CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

def collect_faces():
    face_detector = cv2.CascadeClassifier(CASCADE_PATH)
    face_samples = []
    ids = []
    # We'll assign ID = 1 for owner (single-person project)
    owner_id = 1

    files = [f for f in os.listdir(DATASET_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    print(f"[i] Found {len(files)} images in {DATASET_DIR}")

    for f in files:
        path = os.path.join(DATASET_DIR, f)
        img = cv2.imread(path)
        if img is None:
            print("[!] Could not read", path, "- skipping")
            continue
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # optional: resize large images to speed up and improve detection
        h, w = gray.shape
        if max(h, w) > 1000:
            scale = 1000.0 / max(h, w)
            gray = cv2.resize(gray, (int(w*scale), int(h*scale)))
        faces = face_detector.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(50,50))
        if len(faces) == 0:
            print("[!] No face detected in", f, "- try another photo or better lighting")
            continue
        for (x,y,w,h) in faces:
            face_img = gray[y:y+h, x:x+w]
            face_samples.append(face_img)
            ids.append(owner_id)
            print("[+] Added face from", f)
            # For each image we only need one face — break after first
            break
    return face_samples, ids

def train_and_save():
    faces, ids = collect_faces()
    if len(faces) == 0:
        print("[ERROR] No faces collected. Fix dataset images and retry.")
        return
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, np.array(ids))
    recognizer.write(TRAINER_FILE)
    print(f"[OK] Training complete. Trainer saved to {TRAINER_FILE}")
    print(f"[INFO] Number of face samples: {len(faces)}")

if __name__ == "__main__":
    if not os.path.exists(DATASET_DIR):
        print(f"[ERROR] Dataset folder '{DATASET_DIR}' not found. Create it and put images inside.")
    else:
        train_and_save()
