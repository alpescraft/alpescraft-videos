import cv2
from moviepy.video.io.VideoFileClip import VideoFileClip

from logic_v2.tracking import tracking_crop_of_presenter


def detect_person(first_image):

    initial_detection_image = first_image.copy()
    # Convert into grayscale
    gray = cv2.cvtColor(initial_detection_image, cv2.COLOR_BGR2GRAY)
    # # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    return faces[0]


if __name__ == "__main__":
    original = VideoFileClip(
        "/Users/johan/Documents/alpescraft videos 2024/sessions/cyrille martraire/speaker.mp4",
        target_resolution=(1920, 1080))

    face_cascade = cv2.CascadeClassifier('logic_v2/tracking/haarcascade_upperbody.xml')
    # Read the input image
    first_image = original.get_frame(0).copy()

    # img = cv2.imread('test.jpg')
    (x, y, w, h) = detect_person(first_image)
    cv2.rectangle(first_image, (x, y), (x + w, y + h), (255, 0, 0), 2)
    # Display the output
    cv2.imshow('img', first_image)
    cv2.waitKey()

    # tracked_clip = tracking_crop_of_presenter(original)
    # tracked_clip.subclip(0, 3).write_videofile("tracked_clip.mp4", codec="libx264", fps=24)
