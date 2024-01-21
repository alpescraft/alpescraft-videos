import sys

from moviepy.video.fx import resize

from logic_v2.VideoInfo import VideoInfo
from logic_v2.collate_video import collate_main_part
from logic_v2.VideoCollageInfo import VideoCollageInfo

"""
Prepare real video by cropping and concatenating successive videos

1. Background
2. Add Video Title
2b. add music intro
2a. Add logo
3. connect with fade to real video

4. produce a thumbnail for the video as a separate artefact

"""


def do_it_all(video_info: VideoInfo, filename: str) -> None:

    full_video = collate_main_part(VideoCollageInfo.from_video_info(video_info))

    video_name = filename.removesuffix(".yml")
    write_thumbnail(full_video, video_name+".png")
    write_video(full_video, video_name + ".mp4")


def write_video(full_video, output_file):
    full_video.write_videofile(output_file, fps=25, codec='libx264')  # Many options...


def write_thumbnail(full_video, output_file):
    resize.resize(full_video, .5).save_frame(output_file, t=0.1)


if __name__ == '__main__':
    assert len(sys.argv) == 3
    filename = sys.argv[1]
    max_length = sys.argv[2]

    video_info = VideoInfo.load_video_info(filename, int(max_length))
    do_it_all(video_info, filename)