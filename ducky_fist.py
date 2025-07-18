import time
import cv2
import mediapipe as mp
from transparent import overlay_transparent

# --- MediaPipe setup ---
mp_drawing = mp.solutions.drawing_utils
mp_hands   = mp.solutions.hands
hands      = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

# --- Load assets ---
ducky_raw   = cv2.imread("assets/ducky.png", cv2.IMREAD_UNCHANGED)
path_raw    = cv2.imread("assets/path.png",  cv2.IMREAD_UNCHANGED)
basket_raw  = cv2.imread("assets/basket.png", cv2.IMREAD_UNCHANGED)

# --- Game state ---
ducky_x = 0
score = 0
last_score_time = 0
score_delay = 1.0  # seconds

# --- Fist detection helper ---
def is_fist(landmarks):
    tips = [4, 8, 12, 16, 20]
    folded = sum(1 for i in tips[1:] if landmarks[i].y > landmarks[i - 2].y)
    return folded >= 4

# --- Start webcam ---
cap = cv2.VideoCapture(0)

# Read first frame to get actual size
ret, frame = cap.read()
if not ret:
    print("Camera not found")
    cap.release()
    exit()

frame_h, frame_w = frame.shape[:2]

# Resize assets based on webcam size
ducky   = cv2.flip(cv2.resize(ducky_raw,   (int(frame_w*0.18), int(frame_h*0.4))), 1)
path    = cv2.resize(path_raw,    (frame_w, int(frame_h*0.7)))
basket  = cv2.resize(basket_raw,  (int(frame_w*0.1), int(frame_h*0.2)))

ducky_h, ducky_w = ducky.shape[:2]

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frame_h, frame_w = frame.shape[:2]

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    # Draw path and basket
    path_y = frame_h - path.shape[0]
    frame = overlay_transparent(frame, path, 0, path_y)

    bx = frame_w - basket.shape[1]
    by = frame_h - basket.shape[0] - int(frame_h * 0.15)
    frame = overlay_transparent(frame, basket, bx, by)

    # Draw ducky
    y_ducky = frame_h - ducky_h - int(frame_h * 0.15)
    frame = overlay_transparent(frame, ducky, ducky_x, y_ducky)

    # Hand detection
    if results.multi_hand_landmarks:
        hand = results.multi_hand_landmarks[0]
        mp_drawing.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

        if is_fist(hand.landmark):
            now = time.time()
            if now - last_score_time > score_delay:
                if ducky_x + ducky_w + 10 < frame_w:
                    ducky_x += int(frame_w * 0.04)
                score += 10
                last_score_time = now

    # Score
    cv2.putText(frame, f"Score: {score}",
                (int(frame_w * 0.02), int(frame_h * 0.07)),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)

    # Victory
    if ducky_x + ducky_w >= bx:
        cv2.putText(frame, "You Passed :)",
                    (int(frame_w * 0.3), int(frame_h * 0.5)),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

    cv2.imshow("Fist Game", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
