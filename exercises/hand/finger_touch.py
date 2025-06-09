# rehab_app/exercises/hand/finger_touch.py
name = "Finger Touch"

def is_done(landmarks):
    # Check if index fingertip (landmark 8) touches thumb tip (landmark 4)
    dx = landmarks[8].x - landmarks[4].x
    dy = landmarks[8].y - landmarks[4].y
    distance = (dx*dx + dy*dy) ** 0.5
    return distance < 0.05
