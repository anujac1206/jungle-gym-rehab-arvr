# rehab_app/exercises/arm/shoulder_raise.py
name = "Shoulder Raise"

def is_done(landmarks):
    # Compare wrist (15) height to shoulder (11) height
    return landmarks[15].y < landmarks[11].y
