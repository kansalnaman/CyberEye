import cv2

cam = cv2.VideoCapture(0)
if not cam.isOpened():
    print("❌ Camera not detected!")
else:
    print("✅ Camera working! Press Q to quit.")
    while True:
        ret, frame = cam.read()
        cv2.imshow('CyberEye Camera Test', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cam.release()
    cv2.destroyAllWindows()
