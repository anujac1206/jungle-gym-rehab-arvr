import cv2
import mediapipe as mp
import numpy as np

# Overlay function WITHIN the same file
def overlay_transparent(background, overlay, x, y):
    bg_h, bg_w = background.shape[:2]
    if x >= bg_w or y >= bg_h:
        return background

    h, w = overlay.shape[:2]
    if x + w > bg_w:
        w = bg_w - x
        overlay = overlay[:, :w]
    if y + h > bg_h:
        h = bg_h - y
        overlay = overlay[:h]

    if overlay.shape[2] < 4:
        return background  # No alpha channel

    overlay_rgb = overlay[..., :3].astype(float)
    mask = overlay[..., 3:] / 255.0

    roi = background[y:y+h, x:x+w].astype(float)
    roi_bgr = roi[..., :3]

    blended = (1.0 - mask) * roi_bgr + mask * overlay_rgb
    background[y:y+h, x:x+w, :3] = blended.astype(np.uint8)
    return background

# Load assets
chad_img = cv2.imread("assets/chad.png", cv2.IMREAD_UNCHANGED)
banana_img = cv2.imread("assets/banana.png", cv2.IMREAD_UNCHANGED)
jungle_bg = cv2.imread("assets/path.png", cv2.IMREAD_UNCHANGED)  # Transparent PNG

# Setup MediaPipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
cap = cv2.VideoCapture(0)

score = 0
chad_y_ratio = 0.7
frame_counter = 0
bubble_shown = False

def is_overhead(landmarks):
    left = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
    right = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
    nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
    return left.y < nose.y and right.y < nose.y

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w = frame.shape[:2]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    res = pose.process(rgb)

    # Resize and overlay transparent jungle background over live video
    display = frame.copy()
    if jungle_bg is not None and jungle_bg.shape[2] == 4:
        resized_path = cv2.resize(jungle_bg, (w, h), interpolation=cv2.INTER_AREA)
        display = overlay_transparent(display, resized_path, 0, 0)

    # Resize Chad character
    chad = cv2.resize(chad_img, (int(w * 0.2), int(h * 0.3)))

    # Arm raise detection
    if res.pose_landmarks:
        lms = res.pose_landmarks.landmark
        if is_overhead(lms):
            frame_counter += 1
            if frame_counter % 8 == 0 and score < 10:
                chad_y_ratio = max(0.05, chad_y_ratio - 0.02)
                score += 1
        else:
            frame_counter = 0

    # Chad's position
    chad_x = int((w - chad.shape[1]) / 2)
    chad_y = int(h * chad_y_ratio)
    display = overlay_transparent(display, chad, chad_x, chad_y)

    # Bananas for score
    banana_size = int(w * 0.05)
    banana_resized = cv2.resize(banana_img, (banana_size, banana_size))
    for i in range(score):
        x_pos = int(w * 0.05) + i * (banana_size + 5)
        y_pos = int(h * 0.1)
        display = overlay_transparent(display, banana_resized, x_pos, y_pos)

    # Score text
    cv2.putText(display, f"Climb Score: {score}", (int(0.05 * w), int(0.08 * h)),
                cv2.FONT_HERSHEY_SIMPLEX, w / 1000, (255, 255, 255), 3)

    # Initial message
    if score < 1:
        cv2.rectangle(display, (int(0.05 * w), int(0.85 * h)),
                      (int(0.95 * w), int(0.95 * h)), (0, 0, 0), -1)
        cv2.putText(display, "Raise Both Arms to Help Chad Climb!",
                    (int(0.07 * w), int(0.93 * h)),
                    cv2.FONT_HERSHEY_SIMPLEX, w / 1100, (0, 255, 0), 2)

    # Motivational message
    if score > 5 and not bubble_shown:
        cv2.putText(display, "You're doing great! Chad is proud 🐵",
                    (int(0.15 * w), int(0.5 * h)),
                    cv2.FONT_HERSHEY_SIMPLEX, w / 1200, (255, 255, 0), 2)
        bubble_shown = True

    # Completion message
    if score >= 10:
        cv2.putText(display, "🎉 Climb Complete! Chad loves your energy! 🎉",
                    (int(0.08 * w), int(0.5 * h)),
                    cv2.FONT_HERSHEY_SIMPLEX, w / 1000, (0, 255, 255), 2)

    cv2.imshow("Chad's Jungle Climb", display)
    if cv2.waitKey(1) & 0xFF == ord('q') or score >= 10:
        break

cap.release()
cv2.destroyAllWindows()
