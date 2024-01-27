import sys

from moviepy.video.fx import resize

from logic_v2.PresentationInfo import PresentationInfo
from logic_v2.collate_video import collate_main_part

"""
Prepare real video by cropping and concatenating successive videos

1. Background
2. Add Video Title
2b. add music intro
2a. Add logo
3. connect with fade to real video

4. produce a thumbnail for the video as a separate artefact

"""


def do_it_all(video_info: PresentationInfo, filename: str) -> None:

    full_video = collate_main_part(video_info)

    video_name = filename.removesuffix(".yml")
    write_thumbnail(full_video, video_name+".png")
    write_video(full_video, video_name + ".mp4")


def write_video(full_video, output_file):
    full_video.write_videofile(output_file, fps=25, codec='libx264')  # Many options...



def write_thumbnail(full_video, output_file):
    intro_length = 6
    resize.resize(full_video, .5).save_frame(output_file, t=intro_length+2)


if __name__ == '__main__':
    assert len(sys.argv) >= 2
    filename = sys.argv[1]
    max_length = int(sys.argv[2]) if len(sys.argv) > 2 else None

    video_info = PresentationInfo.load_video_info(filename, max_length)
    do_it_all(video_info, filename)