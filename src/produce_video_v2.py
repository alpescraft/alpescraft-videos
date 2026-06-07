import sys
import PIL.Image
PIL.Image.ANTIALIAS = PIL.Image.LANCZOS  # moviepy 1.x / Pillow 10+ compatibility
from os.path import dirname, basename

from moviepy.video.fx import resize

from logic_v2.PresentationInfo import PresentationInfo
from logic_v2.collate_video import (
    build_final_clip,
    GenerationPipeline,
    CompositeMainPartBuilder,
    SingleClipMainPartBuilder,
    WithIntro,
    NoIntro,
    AlpesCraftConferenceTheme,
    HTConferenceTheme,
)

"""
Prepare real video by cropping and concatenating successive videos

1. Background
2. Add Video Title
2b. add music intro
2a. Add logo
3. connect with fade to real video

4. produce a thumbnail for the video as a separate artefact

"""


def write_video(full_video, output_file):
    full_video.write_videofile(output_file, fps=25, codec='libx264', audio_codec='aac', threads=8)


def write_thumbnail(full_video, output_file, thumbnail_time):
    resize.resize(full_video, .5).save_frame(output_file, t=thumbnail_time)


def get_output_prefix(filename):
    filename_without_suffix = filename.removesuffix(".yml")
    video_dir = dirname(filename_without_suffix)
    directory_name = basename(video_dir)
    return f"{video_dir}/{directory_name}"


def create_pipeline(conference: str, option: str, video_info: PresentationInfo) -> GenerationPipeline:
    if conference == "ht":
        theme = HTConferenceTheme()
    elif conference == "alpescraft":
        theme = AlpesCraftConferenceTheme()
    else:
        raise ValueError(f"Unknown conference: {conference}")

    main_part = SingleClipMainPartBuilder(theme=theme) if video_info.slides is None else CompositeMainPartBuilder(theme=theme)

    if option == "video-nointro":
        return GenerationPipeline(main_part=main_part, intro=NoIntro())
    else:
        return GenerationPipeline(main_part=main_part, intro=WithIntro(theme=theme))


def parse_commandline():
    assert len(sys.argv) >= 3

    conference = sys.argv[1]
    filename = sys.argv[2]
    max_length = int(sys.argv[3]) if len(sys.argv) > 3 else None

    if len(sys.argv) <= 4:
        option = "video"
    elif sys.argv[4] == "--no-intro":
        option = "video-nointro"
    elif sys.argv[4] == "--thumbnail":
        option = "thumbnail"
    else:
        raise ValueError("Unknown option argument")

    video_info = PresentationInfo.load_video_info(filename, max_length)
    pipeline = create_pipeline(conference, option, video_info)
    return filename, video_info, pipeline, option


if __name__ == '__main__':
    filename, video_info, pipeline, option = parse_commandline()

    full_video = build_final_clip(video_info, pipeline)
    output_prefix = get_output_prefix(filename)

    if option in ("video", "video-nointro"):
        write_video(full_video, output_prefix + "-out.mp4")

    write_thumbnail(full_video, output_prefix + "-thumbnail.png", 3)
