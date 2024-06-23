import sys
import typing
from dataclasses import dataclass
from os.path import dirname, basename

from moviepy.video.fx import resize

from logic_v2.PresentationInfo import PresentationInfo
from logic_v2.collate_video import collate_main_part, collate_main_part_without_intro

"""
Prepare real video by cropping and concatenating successive videos

1. Background
2. Add Video Title
2b. add music intro
2a. Add logo
3. connect with fade to real video

4. produce a thumbnail for the video as a separate artefact

"""


@dataclass
class GenerationStrategy:
    task: typing.Literal["video", "video-nointro", "thumbnail"]


def do_it_all(video_info: PresentationInfo, filename: str, generation_strategy: GenerationStrategy) -> None:

    filename_without_suffix = filename.removesuffix(".yml")
    video_dir = dirname(filename_without_suffix)
    directore_name = basename(video_dir)
    output_file_prefix = f"{video_dir}/{directore_name}"
    if generation_strategy.task == "video":
        full_video = collate_main_part(video_info)
        write_video(full_video, output_file_prefix + "-out.mp4")
        write_thumbnail(full_video, output_file_prefix + "-thumbnail.png", 3)
    elif generation_strategy.task == "video-nointro":
        full_video = collate_main_part_without_intro(video_info)
        write_video(full_video, output_file_prefix + "-out.mp4")
        write_thumbnail(full_video, output_file_prefix + "-thumbnail.png", 3+5)



def write_video(full_video, output_file):
    full_video.write_videofile(output_file, fps=25, codec='libx264', threads=8)  # Many options...


def write_thumbnail(full_video, output_file, thumbnail_time):
    resize.resize(full_video, .5).save_frame(output_file, t=thumbnail_time)
    # resize.resize(full_video, .5).save_frame(output_file, t=intro_length+2)


def get_generation_strategy():
    if len(sys.argv) <= 3:
        generation_strategy = GenerationStrategy(task="video")
    elif sys.argv[3] == "--no-intro":
        generation_strategy = GenerationStrategy(task="video-nointro")
    # elif sys.argv[3] == "--thumbnail":
    #     generation_strategy = GenerationStrategy(task="thumbnail")
    else:
        raise ValueError("Unknown option argument")
    return generation_strategy


def parse_commandline():
    assert len(sys.argv) >= 2
    filename = sys.argv[1]
    max_length = int(sys.argv[2]) if len(sys.argv) > 2 else None
    video_info = PresentationInfo.load_video_info(filename, max_length)
    generation_strategy = get_generation_strategy()
    return filename, video_info, generation_strategy


if __name__ == '__main__':
    filename, video_info, generation_strategy = parse_commandline()

    do_it_all(video_info, filename, generation_strategy)