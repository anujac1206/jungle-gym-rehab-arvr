import cv2
import mediapipe as mp
import numpy as np
import random
from transparent import overlay_transparent

# Load assets
coconut_img = cv2.imread("assets/coconut.png", cv2.IMREAD_UNCHANGED)
chad_img = cv2.imread("assets/chad.png", cv2.IMREAD_UNCHANGED)
jungle_bg = cv2.imread("assets/path.png", cv2.IMREAD_UNCHANGED)

# Mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.6, min_tracking_confidence=0.6)
mp_drawing = mp.solutions.drawing_utils

# Game variables
coconut = {"x": random.randint(100, 500), "y": 0, "speed": 3}
score = 0
max_score = 10
frame_counter = 0
cooldown_frames = 3

# For temporary tracking when landmarks disappear
prev_wrist = {"Left": None, "Right": None}
wrist_cache = {"Left": None, "Right": None}
lost_count = {"Left": 0, "Right": 0}

# Camera
cap = cv2.VideoCapture(0)

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    frame_h, frame_w = frame.shape[:2]
    display = frame.copy()

    # Jungle background
    jungle_scale = 0.28
    jungle_h = int(frame_h * jungle_scale)
    jungle_resized = cv2.resize(jungle_bg, (frame_w, jungle_h), interpolation=cv2.INTER_AREA)
    display = overlay_transparent(display, jungle_resized, 0, frame_h - jungle_h)

    # MediaPipe detection
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    detected_hands = set()

    # Coconut movement
    coconut["y"] += coconut["speed"]
    if coconut["y"] > frame_h - 100:
        coconut["y"] = 0
        coconut["x"] = random.randint(100, frame_w - 100)
        coconut["speed"] = random.randint(2, 4)

    # Draw coconut
    coconut_resized = cv2.resize(coconut_img, (100, 100))
    display = overlay_transparent(display, coconut_resized, coconut["x"], coconut["y"])

    # Landmark handling
    if results.multi_hand_landmarks and results.multi_handedness:
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            handedness = results.multi_handedness[idx].classification[0].label
            wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
            wrist_x = int(wrist.x * frame_w)
            wrist_y = int(wrist.y * frame_h)
            detected_hands.add(handedness)
            wrist_cache[handedness] = (wrist_x, wrist_y)
            lost_count[handedness] = 0

            mp_drawing.draw_landmarks(display, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Fallback for lost landmarks
    for hand in ["Left", "Right"]:
        if hand not in detected_hands:
            lost_count[hand] += 1
        if wrist_cache[hand] and lost_count[hand] <= cooldown_frames:
            wrist_x, wrist_y = wrist_cache[hand]
            if prev_wrist[hand]:
                dx = wrist_x - prev_wrist[hand][0]
                dy = wrist_y - prev_wrist[hand][1]
                speed = np.sqrt(dx ** 2 + dy ** 2)

                # Sensitive detection
                if speed > 6:
                    cx = coconut["x"] + 50
                    cy = coconut["y"] + 50
                    if abs(wrist_x - cx) < 90 and abs(wrist_y - cy) < 90:
                        score += 1
                        coconut["y"] = 0
                        coconut["x"] = random.randint(100, frame_w - 100)
                        coconut["speed"] = random.randint(2, 4)
            prev_wrist[hand] = (wrist_x, wrist_y)

    # Draw Chad
    chad = cv2.resize(chad_img, (int(frame_w * 0.2), int(frame_h * 0.4)))
    display = overlay_transparent(display, chad, frame_w - chad.shape[1], frame_h - chad.shape[0])

    # Score
    cv2.putText(display, f"Score: {score}/{max_score}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)

    # Game end
    if score >= max_score:
        cv2.putText(display, "All coconuts smashed!", (int(frame_w * 0.2), int(frame_h * 0.5)),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 255, 0), 4)
        cv2.imshow("Jungle Punch: Chad's Coconut Smash", display)
        cv2.waitKey(3000)
        break

    cv2.imshow("Jungle Punch: Chad's Coconut Smash", display)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
