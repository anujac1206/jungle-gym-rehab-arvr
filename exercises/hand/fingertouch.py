import math

class FingerTouchExercise:
    name = "Touch Index to Thumb"

    def is_done(self, landmarks):
        thumb = landmarks[4]
        index = landmarks[8]
        dist = math.sqrt((thumb.x - index.x) ** 2 + (thumb.y - index.y) ** 2)
        return dist < 0.05

finger_touch = FingerTouchExercise()
