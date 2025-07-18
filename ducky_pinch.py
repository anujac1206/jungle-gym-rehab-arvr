import cv2
import mediapipe as mp
import numpy as np
from transparent import *

# Load overlay images with alpha channel
ducky = cv2.imread("assets/ducky.png", cv2.IMREAD_UNCHANGED)
ducky=cv2.flip(ducky,1)
path = cv2.imread("assets/path.png", cv2.IMREAD_UNCHANGED)
egg_img = cv2.imread("assets/egg.png", cv2.IMREAD_UNCHANGED)
basket_img = cv2.imread("assets/basket.png", cv2.IMREAD_UNCHANGED)

# MediaPipe Hands setup
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

# Webcam
cap = cv2.VideoCapture(0)
success, frame = cap.read()
if not success:
    print("Error: Could not read from camera.")
    cap.release()
    exit()

frame_h, frame_w = frame.shape[:2]

# Resize overlays relative to frame
path_h = int(0.35 * frame_h)
path = cv2.resize(path, (frame_w, path_h))

# Estimate the visible height of path's colored ground section
visible_ground_y = frame_h - int(path_h * 0.22)

ducky_h = int(path_h * 0.9)
ducky_w = int(ducky_h * ducky.shape[1] / ducky.shape[0])
ducky = cv2.resize(ducky, (ducky_w, ducky_h))

egg_size = int(0.18 * frame_h)
egg_img = cv2.resize(egg_img, (egg_size, egg_size))

basket_h = int(path_h * 0.9)
basket_w = int(basket_h * basket_img.shape[1] / basket_img.shape[0])
basket_img = cv2.resize(basket_img, (basket_w, basket_h))

# Position overlays so they sit exactly on the colored part of path
ducky_x = int(0.02 * frame_w)
ducky_y = visible_ground_y - ducky_h

basket_x = frame_w - basket_w - int(0.02 * frame_w)
basket_y = visible_ground_y - basket_h
basket_zone = (basket_x - 40, basket_y - 40, basket_w + 80, basket_h + 80)  # Larger basket zone

# Egg state
egg = {
    'x': np.random.randint(int(0.2 * frame_w), int(0.7 * frame_w)),
    'y': 0,
    'dragging': False,
    'placed': False,
    'falling': True
}
egg_speed = int(0.01 * frame_h)

score = 0
max_score = 10

def is_pinching(lm):
    tip = lm[8]   # Index tip
    thumb = lm[4] # Thumb tip
    dist = np.linalg.norm(np.array([tip.x - thumb.x, tip.y - thumb.y]))
    return dist < 0.05

# Main loop
while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    frame_h, frame_w = frame.shape[:2]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    pinch = False
    pinch_x, pinch_y = 0, 0

    if result.multi_hand_landmarks:
        for hand in result.multi_hand_landmarks:
            lm = hand.landmark
            pinch = is_pinching(lm)
            pinch_x = int(lm[8].x * frame.shape[1])
            pinch_y = int(lm[8].y * frame.shape[0])
            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

    # Egg logic
    if egg['falling']:
        egg['y'] += egg_speed
        if pinch and abs(pinch_x - egg['x']) < egg_size and abs(pinch_y - egg['y']) < egg_size:
            egg['dragging'] = True
            egg['falling'] = False
    elif egg['dragging'] or (not egg['placed'] and pinch and abs(pinch_x - egg['x']) < egg_size and abs(pinch_y - egg['y']) < egg_size):
        egg['dragging'] = True
        egg['falling'] = False
        if pinch:
            egg['x'], egg['y'] = pinch_x - egg_size // 2, pinch_y - egg_size // 2
        else:
            egg['dragging'] = False
            if (basket_zone[0] < egg['x'] < basket_zone[0] + basket_zone[2] and
                basket_zone[1] < egg['y'] < basket_zone[1] + basket_zone[3]):
                egg['placed'] = True
                score += 1

    # Reset for next egg
    if egg['placed'] or egg['y'] > frame_h:
        if score < max_score:
            egg = {
                'x': np.random.randint(int(0.2 * frame_w), int(0.7 * frame_w)),
                'y': 0,
                'dragging': False,
                'placed': False,
                'falling': True
            }

    # Text
    text = "Pinch your thumb and index finger to drag the egg"
    text_x = max(int(0.05 * frame_w), 10)
    text_y = max(int(0.06 * frame_h), 30)
    cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 120, 255), 2)
    cv2.putText(frame, f"Score: {score}/{max_score}", (text_x, text_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 255), 3)

    # Draw overlays
    if score < max_score:
        frame = overlay_transparent(frame, egg_img, egg['x'], egg['y'])
    frame = overlay_transparent(frame, path, 0, frame_h - path_h)
    frame = overlay_transparent(frame, ducky, ducky_x, ducky_y)
    frame = overlay_transparent(frame, basket_img, basket_x, basket_y)

    if score >= max_score:
        cv2.putText(frame, "All eggs delivered!", (int(0.2 * frame_w), int(0.5 * frame_h)),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 4)
        cv2.imshow("Ducky Egg Drop", frame)
        cv2.waitKey(2000)
        break

    cv2.imshow("Ducky Egg Drop", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()