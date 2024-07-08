from os import path
from os.path import dirname
from typing import Tuple

import cv2
from moviepy.video.VideoClip import VideoClip


def tracking_highlight_of_presenter(presentation_clip: VideoClip):

    first_image = presentation_clip.get_frame(0).copy()

    zone = detect_person(first_image)
    print("zone", zone)
    tracker = cv2.TrackerCSRT.create()
    tracker.init(first_image, zone)

    def track_presenter(frame):
        success, box = tracker.update(frame)

        print(success, box)
        if success:
            frame = frame.copy()
            (x, y, w, h) = box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        return frame

    return presentation_clip.fl_image(track_presenter)

def tracking_crop_of_presenter(presentation_clip: VideoClip):
    first_image = presentation_clip.get_frame(0).copy()

    tracker_holder = {"tracker": cv2.TrackerKCF.create()}
    zone = detect_person(first_image)
    print("zone", zone)
    tracker_holder["tracker"].init(first_image, zone)

    def track_presenter(frame):
        print(frame.size)
        success, box = tracker_holder["tracker"].update(frame)
        if not success:
            zone = detect_person(frame)
            if zone is None:
                box = tracker_holder["last_box"]
            else:
                print("zone", zone)
                tracker_holder["tracker"] = cv2.TrackerKCF.create()
                tracker_holder["tracker"].init(frame, zone)
                box = zone
        #     success, box = tracker.update(frame)

        print(success, box)
        box_scaled_to_480x810 = portrait_box_within_bounds_480x810(box)

        (x, y, w, h) = box_scaled_to_480x810
        tracker_holder["last_box"] = box
        return frame[y:y + h, x:x + w]

    return presentation_clip.fl_image(track_presenter)


def detect_person(image):
    face_cascade = cv2.CascadeClassifier(path.join(dirname(__file__), 'tracking/haarcascade_upperbody.xml'))

    # Convert into grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 6)
    if len(faces) == 0:
        return None
    return faces[0]


BoundingBox = Tuple[int, int, int, int]

def portrait_box_within_bounds_480x810(box: BoundingBox):
    """"
    :box is a tuple of 4 integers, x, y, w, h

    Returns the box of size, 480x810 that is the closest to the given box but always inside the bounds

    bounds are within x=0-(1080-480), and y=0-(1920-810)

    width is always 480, height is always 810
    """
    (x, y, w, h) = box
    box_center = (x + w // 2, y + h // 2)
    box_scaled_to_480x810 = (box_center[0] - 240, box_center[1] - 405, 480, 810)
    scaled_box_inside_bounds = (
        max(0, min(1080 - 480, box_scaled_to_480x810[0])),
        max(0, min(1920 - 810, box_scaled_to_480x810[1])),
        480,
        810
    )
    return scaled_box_inside_bounds
