# train_faces.py
import cv2
import os

dataset_path = "dataset"
os.makedirs(dataset_path, exist_ok=True)

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

user_id = 1    # owner ID (fixed)
count = 0
target_count = 5

print("Look at the camera. Press SPACE to capture each image. Press ESC to finish early.")

while True:
    ret, frame = camera.read()
    if not ret:
        print("Camera read failed. Close other apps using camera.")
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

    cv2.putText(frame, f"Captured: {count}/{target_count}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
    cv2.imshow("Enrollment - Press SPACE to capture", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == 27:  # ESC
        print("Enrollment cancelled by user.")
        break
    elif key == ord(' '):  # SPACE to capture
        if len(faces) == 0:
            print("No face detected, try again.")
            continue
        # take first detected face
        (x, y, w, h) = faces[0]
        face_img = gray[y:y+h, x:x+w]
        count += 1
        fname = os.path.join(dataset_path, f"User.{user_id}.{count}.jpg")
        cv2.imwrite(fname, face_img)
        print("[+] Saved:", fname)
        if count >= target_count:
            print("✅ Captured required images.")
            break

camera.release()
cv2.destroyAllWindows()
