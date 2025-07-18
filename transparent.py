import cv2
import numpy as np

def overlay_transparent(background, overlay, x, y):
    bh, bw = background.shape[:2]
    h, w = overlay.shape[:2]

    if x + w > bw:
        w = bw - x
        overlay = overlay[:, :w]
    if y + h > bh:
        h = bh - y
        overlay = overlay[:h]

    overlay_rgb = overlay[..., :3]
    mask = overlay[..., 3:] / 255.0

    roi = background[y:y+h, x:x+w]
    blended = (1.0 - mask) * roi + mask * overlay_rgb
    background[y:y+h, x:x+w] = blended.astype(np.uint8)

    return background
