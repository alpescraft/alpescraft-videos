from logic_v2.collate_video import collate_main_part
from logic_v2.VideoCollageInfo import VideoCollageInfo

if __name__ == '__main__':
    collage_info = VideoCollageInfo(
        presentation_file_path="../test_files/ht-jan-01-speaker.mp4",
        slides_file_path="../test_files/ht-jan-01-slides.mkv",
        presentation_start_stop_seconds=(0, 2.2),
        target_resolution=(1920, 1080))
    final_clip = collate_main_part(collage_info)
    final_clip.write_videofile("../test_files/ht-jan-01-composed.mp4", threads=4, codec="hevc_videotoolbox")
