import cv2
import numpy as np
import mediapipe as mp
import os
import time

# Simple local face & hand utilities using only OpenCV + MediaPipe.
# This is not perfect "real" face-recognition but works as a fun prototype.

FACE_DIR = "faces"
os.makedirs(FACE_DIR, exist_ok=True)

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils


def _capture_frame_from_camera(timeout_sec: float = 5.0):
    """Capture a single frame from default webcam. Returns frame (BGR) or None."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[vision] Cannot access webcam.")
        return None

    start = time.time()
    frame = None

    # Give camera some time to adjust exposure and actually return frames
    while time.time() - start < timeout_sec:
        ret, frame = cap.read()
        if ret and frame is not None:
            break

    cap.release()

    if frame is None:
        print("[vision] Failed to capture frame from webcam.")
    return frame


def _load_face_cascade():
    """Load Haar cascade for face detection."""
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    if not os.path.exists(cascade_path):
        print("[vision] Haar cascade not found at:", cascade_path)
        return None

    face_cascade = cv2.CascadeClassifier(cascade_path)
    if face_cascade.empty():
        print("[vision] Failed to load Haar cascade.")
        return None
    return face_cascade


def _crop_face(frame):
    """
    Detect the largest face in the frame and return the cropped region.
    If no face is found, return the original frame.
    """
    face_cascade = _load_face_cascade()
    if face_cascade is None:
        print("[vision] No cascade, returning full frame for face.")
        return frame

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) == 0:
        print("[vision] No face found to crop, using full frame.")
        return frame

    # pick the largest face (by area)
    x, y, w, h = max(faces, key=lambda box: box[2] * box[3])
    face_roi = frame[y:y+h, x:x+w]
    print(f"[vision] Cropped face region: x={x}, y={y}, w={w}, h={h}")
    return face_roi


# ========= FACE "REGISTRATION" & MATCHING =========

def register_face(name: str = "owner") -> bool:
    """
    Capture one frame from webcam and save as this user's face image.
    Detects face and crops to that region.
    """
    frame = _capture_frame_from_camera()
    if frame is None:
        print("[vision] register_face: no frame captured.")
        return False

    try:
        face_region = _crop_face(frame)
        face_img = cv2.resize(face_region, (200, 200))
        path = os.path.join(FACE_DIR, f"{name}.jpg")
        cv2.imwrite(path, face_img)
        print(f"[vision] Saved face image for {name} at {path}")
        return True
    except Exception as e:
        print("[vision] Error while saving face:", e)
        return False


def recognize_face(name: str = "owner", threshold: float = 20000.0):
    """
    Capture a new frame and compare with stored reference face.
    Uses a simple L2 difference of grayscale images.
    threshold: lower means stricter match.
    Returns (is_same_person: bool, score: float or None)
    """
    ref_path = os.path.join(FACE_DIR, f"{name}.jpg")
    if not os.path.exists(ref_path):
        print(f"[vision] No stored face for {name}.")
        return False, None

    ref_img = cv2.imread(ref_path)
    if ref_img is None:
        print(f"[vision] Could not read stored face {ref_path}.")
        return False, None

    frame = _capture_frame_from_camera()
    if frame is None:
        print("[vision] recognize_face: no frame captured.")
        return False, None

    try:
        # Crop faces in both images
        ref_face = _crop_face(ref_img)
        cur_face = _crop_face(frame)

        ref_gray = cv2.cvtColor(cv2.resize(ref_face, (200, 200)), cv2.COLOR_BGR2GRAY)
        cur_gray = cv2.cvtColor(cv2.resize(cur_face, (200, 200)), cv2.COLOR_BGR2GRAY)

        # Compute simple L2 distance
        diff = cv2.norm(ref_gray, cur_gray, cv2.NORM_L2)
        print(f"[vision] Face diff score: {diff}")

        is_same = diff < threshold
        return is_same, diff
    except Exception as e:
        print("[vision] Error during face compare:", e)
        return False, None


# ========= HAND GESTURE (OPEN PALM vs UNKNOWN) =========

def detect_hand_gesture():
    """
    Try multiple frames from webcam, look for one hand, detect if it's an 'open palm'.
    Returns: "open_palm", "no_hand", or "unknown".
    """
    max_attempts = 10
    last_result = "no_hand"

    with mp_hands.Hands(
        static_image_mode=True,
        max_num_hands=1,
        min_detection_confidence=0.5
    ) as hands:
        for _ in range(max_attempts):
            frame = _capture_frame_from_camera()
            if frame is None:
                print("[vision] detect_hand_gesture: no frame captured.")
                continue

            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            try:
                results = hands.process(image_rgb)
            except Exception as e:
                print("[vision] Error in hand detection:", e)
                return "unknown"

            if not results.multi_hand_landmarks:
                print("[vision] No hand detected in this frame.")
                last_result = "no_hand"
                continue

            hand_landmarks = results.multi_hand_landmarks[0]

            # Finger tip & pip landmark indices
            # Index, Middle, Ring, Pinky
            finger_tips = [8, 12, 16, 20]
            finger_pips = [6, 10, 14, 18]

            extended_count = 0
            h, w, _ = frame.shape

            for tip_idx, pip_idx in zip(finger_tips, finger_pips):
                tip_y = hand_landmarks.landmark[tip_idx].y * h
                pip_y = hand_landmarks.landmark[pip_idx].y * h
                # In image coords, smaller y is "higher" in the image.
                if tip_y < pip_y:
                    extended_count += 1

            print(f"[vision] Extended fingers: {extended_count}")

            if extended_count >= 3:
                return "open_palm"
            else:
                last_result = "unknown"

    return last_result


# ========= SIMPLE "OBJECT" VIEW: DO I SEE A PERSON? =========

def see_any_person():
    """
    Use a basic Haar cascade to check whether a face is visible.
    Returns True if at least one face is detected.
    """
    face_cascade = _load_face_cascade()
    if face_cascade is None:
        return False

    frame = _capture_frame_from_camera()
    if frame is None:
        print("[vision] see_any_person: no frame captured.")
        return False

    try:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        print(f"[vision] Faces detected: {len(faces)}")
        return len(faces) > 0
    except Exception as e:
        print("[vision] Error in face detection:", e)
        return False
