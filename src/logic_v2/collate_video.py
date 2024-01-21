from typing import Tuple

from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import VideoClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx import resize
from moviepy.video.io.VideoFileClip import VideoFileClip

from logic_v2.VideoCollageInfo import VideoCollageInfo
from logic_v2.start_time import get_relative_start_time


def collate_main_part(video_collage_info: VideoCollageInfo, presenter_slide_ratio: Tuple[float, float]):
    start, length = video_collage_info.get_start_length()

    presentation_file_path = video_collage_info.presentation_file_path
    presentation_clip = make_video_clip(presentation_file_path, presenter_slide_ratio[0], start, length)

    track_file = video_collage_info.slides_file
    slides_file_path = track_file.file_name
    slides_relative_start = get_relative_start_time(presentation_file_path, slides_file_path,
                                                    start) + track_file.extra_offset
    slides_clip: VideoClip = make_video_clip(slides_file_path, presenter_slide_ratio[1], slides_relative_start, length)

    track_file = video_collage_info.sound_file
    sound_file_path = track_file.file_name
    sound_relative_start = get_relative_start_time(presentation_file_path, sound_file_path,
                                                   start) + track_file.extra_offset
    sound_clip = AudioFileClip(sound_file_path).subclip(sound_relative_start, sound_relative_start + length)

    print("start ", start)
    print("sound_start", sound_relative_start)
    # exit(0)
    target_resolution = video_collage_info.target_resolution
    final_clip = (CompositeVideoClip([

        slides_clip.set_position(("right", "top")),
        presentation_clip.set_position(("left", "bottom"))
    ],
        size=target_resolution).subclip(0, length)
                  .set_audio(sound_clip))
    return final_clip


def make_video_clip(presentation_file_path, ratio, start, length):
    presentation_clip: VideoClip = VideoFileClip(presentation_file_path) \
        .subclip(start, start + length)
    presentation_clip.set_audio(None)
    resized_presentation_clip = resize.resize(presentation_clip, newsize=ratio)
    return resized_presentation_clip
