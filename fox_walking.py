import cv2
import mediapipe as mp
import numpy as np
import time

# Setup
cap = cv2.VideoCapture(0)
mp_pose = mp.solutions.pose.Pose()
step_count = 0
target_steps = 10
goal_reached = False
goal_time = None
sushi_x = 0
step_pixels = 0
leg_lifted = False

# Load assets
sushi_raw = cv2.imread("assets/fox.png", cv2.IMREAD_UNCHANGED)
beach_raw = cv2.imread("assets/beach.png", cv2.IMREAD_UNCHANGED)

def overlay_transparent(bg, overlay, x, y):
    bh, bw = bg.shape[:2]
    oh, ow = overlay.shape[:2]
    if x + ow > bw or y + oh > bh:
        return bg
    alpha = overlay[:, :, 3] / 255.0
    for c in range(3):
        bg[y:y+oh, x:x+ow, c] = (
            alpha * overlay[:, :, c] + (1 - alpha) * bg[y:y+oh, x:x+ow, c]
        )
    return bg

# Wait for camera
ret, frame = cap.read()
if not ret:
    print("Camera error")
    cap.release()
    exit()

frame_h, frame_w = frame.shape[:2]

# 🏝️ New: Make beach taller (80% of screen height)
beach_height = int(frame_h * 0.9)

# 🦊 New: Make Sushi bigger (25% of screen height)
sushi_size = int(frame_h * 0.25)

# Resize assets
beach = cv2.resize(beach_raw, (frame_w, beach_height), interpolation=cv2.INTER_AREA)
sushi = cv2.resize(sushi_raw, (sushi_size, sushi_size), interpolation=cv2.INTER_AREA)

# Lower Sushi: Position her right on top of beach
# Sushi bottom at 50% height of beach
sushi_y = frame_h - beach_height + int(beach_height*0.98) - sushi.shape[0]

 # fine-tuned

step_pixels = int((frame_w - sushi_size) / target_steps)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)

    # Draw beach
    frame = overlay_transparent(frame, beach, 0, frame_h - beach_height)

    # Pose detection
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = mp_pose.process(rgb)

    if not goal_reached and results.pose_landmarks:
        lm = results.pose_landmarks.landmark
        left_ankle = lm[mp.solutions.pose.PoseLandmark.LEFT_ANKLE]
        right_ankle = lm[mp.solutions.pose.PoseLandmark.RIGHT_ANKLE]

        if left_ankle.visibility > 0.6 and right_ankle.visibility > 0.6:
            diff = abs(left_ankle.y - right_ankle.y)

            # Count only one step per lift
            if diff > 0.05 and not leg_lifted:
                step_count += 1
                sushi_x += step_pixels
                if sushi_x > frame_w - sushi_size:
                    sushi_x = frame_w - sushi_size
                leg_lifted = True
            elif diff <= 0.05:
                leg_lifted = False

    # Draw Sushi
    frame = overlay_transparent(frame, sushi, sushi_x, sushi_y)

    # Display counter
    cv2.putText(
        frame,
        f"Steps: {step_count}",
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        (255, 100, 255),
        3,
    )

    # Goal check
    if step_count >= target_steps and not goal_reached:
        goal_reached = True
        goal_time = time.time()

    if goal_reached:
        text = "Sushi reached home!"
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 2, 4)
        x = (frame_w - tw) // 2
        y = int(frame_h * 0.4)

        cv2.putText(
            frame,
            text,
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            2,
            (0, 255, 0),
            4,
            cv2.LINE_AA
        )

        if time.time() - goal_time > 3:
            break


    cv2.imshow("Sushi's Turtle Walk", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
