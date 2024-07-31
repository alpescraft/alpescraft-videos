import sys

import yaml
from yaml import load

from logic.ConfFileContents import ConfFileContents
from logic.VideoInfo import VideoInfo
from logic.create_video_with_intro import create_video_with_intro

"""
Prepare real video by cropping and concatenating successive videos

1. Background
2. Add Video Title
2b. add music intro
2a. Add logo
3. connect with fade to real video

4. produce a thumbnail for the video as a separate artefact

"""


def do_it_all(video_info: VideoInfo, resource_dir: str) -> None:

    full_video = create_video_with_intro(video_info, resource_dir)

    write_thumbnail(full_video, video_info)
    write_video(full_video, video_info)


def write_video(full_video, video_info):
    full_video.write_videofile(video_info.output_file, fps=25, codec='libx264')  # Many options...


def write_thumbnail(full_video, video_info):
    full_video.resize(.5).save_frame(video_info.output_thumbnail(), t=0.1)


# options
# calculate a list of clips with audio, then join everything


filename = sys.argv[1]
resource_dir = sys.argv[2]


conf_file_contents = ConfFileContents.from_dict(load(open(filename), yaml.Loader))


if __name__ == '__main__':
    video_info = VideoInfo(filename, conf_file_contents)
    do_it_all(video_info, resource_dir)