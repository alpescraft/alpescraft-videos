import cv2
from moviepy.video.io.VideoFileClip import VideoFileClip

from logic_v2.tracking import tracking_crop_of_presenter, detect_person


def do_it():
    original = VideoFileClip(
        "/Users/johan/Documents/alpescraft videos 2024/sessions/cyrille martraire/speaker.mp4",
        target_resolution=(1920, 1080))
    # Read the input image
    first_image = original.get_frame(0).copy()
    # img = cv2.imread('test.jpg')
    zone = detect_person(first_image)
    visualize_detection(first_image, zone)


def visualize_detection(first_image, zone):
    (x, y, w, h) = zone
    cv2.rectangle(first_image, (x, y), (x + w, y + h), (255, 0, 0), 2)
    # Display the output
    cv2.imshow('img', first_image)
    cv2.waitKey()


if __name__ == "__main__":
    # do_it()
    original = VideoFileClip(
        "/Users/johan/Documents/alpescraft videos 2024/sessions/cyrille martraire/speaker.mp4",
        target_resolution=(1920, 1080))

    tracked_clip = tracking_crop_of_presenter(original)
    tracked_clip.subclip(0, 7).write_videofile("tracked_clip.mp4", codec="libx264", fps=24)
