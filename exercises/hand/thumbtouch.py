import math

class ThumbTouchExercise:
    name = "Touch Thumb to Palm"

    def is_done(self, landmarks):
        thumb = landmarks[4]
        palm = landmarks[0]
        dist = math.sqrt((thumb.x - palm.x) ** 2 + (thumb.y - palm.y) ** 2)
        return dist < 0.05

thumb_touch = ThumbTouchExercise()
