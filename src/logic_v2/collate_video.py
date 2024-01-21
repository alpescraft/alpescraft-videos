from moviepy.video.VideoClip import VideoClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx import resize
from moviepy.video.io.VideoFileClip import VideoFileClip

from logic_v2.VideoCollageInfo import VideoCollageInfo
from logic_v2.start_time import get_relative_start_time


def collate_main_part(video_collage_info: VideoCollageInfo):
    start, length = video_collage_info.get_start_length()

    presentation_file_path = video_collage_info.presentation_file_path
    presentation_clip = make_video_clip(presentation_file_path, .25, start, length)

    slides_file_path = video_collage_info.slides_file_path
    slides_relative_start = get_relative_start_time(presentation_file_path, slides_file_path, start)
    slides_clip: VideoClip = make_video_clip(slides_file_path, .75, slides_relative_start, length)

    target_resolution = video_collage_info.target_resolution
    final_clip = CompositeVideoClip([
            presentation_clip.set_position(("left", "bottom")),
            slides_clip.set_position(("right", "top"))],
        size=target_resolution).subclip(0, length)
    return final_clip


def make_video_clip(presentation_file_path, ratio, start, length):
    presentation_clip: VideoClip = VideoFileClip(presentation_file_path) \
        .subclip(start, start + length)
    resized_presentation_clip = resize.resize(presentation_clip, newsize=ratio)
    return resized_presentation_clip
