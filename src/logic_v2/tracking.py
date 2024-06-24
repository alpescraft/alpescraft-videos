import cv2
from moviepy.video.VideoClip import VideoClip


def tracking_crop_of_presenter(presentation_clip: VideoClip):
    first_image = presentation_clip.get_frame(0).copy()
    # img = cv2.imread('test.jpg')
    zone = detect_person(first_image)
    tracker = cv2.TrackerCSRT.create()
    tracker.init(first_image, zone)

    def track_presenter(frame):
        success, box = tracker.update(frame)
        (x, y, w, h) = box
        box_center = (x + w // 2, y + h // 2)
        box_scaled_to_480x810 = (box_center[0] - 240, box_center[1] - 405, 480, 810)

        (x, y, w, h) = box_scaled_to_480x810
        newframe= frame.copy()
        cv2.rectangle(newframe, (x, y), (x + w, y + h), (255, 0, 0), 2)

        return newframe
    return presentation_clip.fl_image(track_presenter)


def detect_person(image):
    face_cascade = cv2.CascadeClassifier('logic_v2/tracking/haarcascade_upperbody.xml')

    # Convert into grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    return faces[0]
