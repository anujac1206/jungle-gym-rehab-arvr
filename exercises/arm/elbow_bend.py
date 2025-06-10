# rehab_app/exercises/arm/elbow_bend.py
name = "Elbow Bend"

def angle_between_points(a, b, c):
    import math
    from math import degrees, acos

    def vec(p1, p2):
        return [p2.x - p1.x, p2.y - p1.y, p2.z - p1.z]

    def dot(u, v):
        return sum([u[i]*v[i] for i in range(3)])

    def length(v):
        return sum([x*x for x in v]) ** 0.5

    u = vec(b, a)
    v = vec(b, c)
    dot_prod = dot(u, v)
    lengths = length(u)*length(v)
    if lengths == 0:
        return 0
    angle = degrees(acos(dot_prod / lengths))
    return angle

def is_done(landmarks):
    # Calculate elbow angle between shoulder(11), elbow(13), wrist(15)
    angle = angle_between_points(landmarks[11], landmarks[13], landmarks[15])
    # Consider bent if angle < 90 degrees
    return angle < 90
