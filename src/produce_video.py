import math
import sys
import typing
from dataclasses import dataclass
from os import path

import yaml
from yaml import load, dump
from moviepy.editor import VideoFileClip, TextClip, ImageClip, CompositeVideoClip, concatenate_videoclips
from moviepy.video import fx
from moviepy.video.fx import crop, resize


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
class ClipSection:

    start: str
    stop: str

    def start_seconds(self) -> int:
        [minutes, seconds] = self.start.split(":")
        return int(minutes) * 60 + int(seconds)


@dataclass
class ConfFileContents:
    title: str
    clip: typing.List[ClipSection]

    @classmethod
    def from_dict(cls, param: dict):
        return cls(
            title=param["title"],
            clip=[ClipSection(**x) for x in param["clip"]]
        )


class VideoInfo:
    def __init__(self, filename: str, conf_file_contents: ConfFileContents) -> None:
        self.conf_file_contents = conf_file_contents

        video_name = filename.removesuffix(".yml")
        self.output_file = video_name + ".mp4"
        self.full_path_on_disk = video_name + ".mkv"

        presenter = path.basename(video_name).split(" - ")[0]
        self.title = conf_file_contents.title
        self.presenter = presenter.title()


def do_it_all(video_info: VideoInfo) -> None:

    clips = video_info.conf_file_contents.clip
    start = clips[0].start_seconds()
    print("start " + str(start))
    presentation_clip: VideoFileClip = VideoFileClip(video_info.full_path_on_disk, target_resolution=(1080, 1920))\
        .subclip(start, start + 10)
    # Make the text. Many more options are available.


    intro = intro_clip(video_info, presentation_clip.size)

    clip = presentation_clip.set_duration(10)
    intro_transition = concatenate_videoclips([intro.crossfadeout(2), clip.crossfadein(2)], method="compose")

    # for i, video in enumerate(video_sections):
    #     video.write_videofile(str(i)+ ".mp4",  fps=10, codec='libx264')

    # result = concatenate_videoclips(video_sections)
    intro_transition.write_videofile(video_info.output_file, fps=25, codec='libx264')  # Many options...


def intro_clip(video_info: VideoInfo, size):
    logo = "/Users/johan/Documents/alpescraft videos 2023/Logo/03-AlpesCraft_Couleurs-M.png"
    logo_clip = ImageClip(logo).set_position(('center', 0.2), relative=True)

    background_image = "/Users/johan/Documents/alpescraft videos 2023/Logo/bandeau.jpg"
    image_clip = ImageClip(background_image)
    cropped_image = crop.crop(image_clip, x1=0, y1=0, width=1920)
    resized = resize.resize(cropped_image, newsize=(1920, 1080))
    title = (TextClip(video_info.title, fontsize=60, color='white', stroke_width=3)
                  .set_position(('center', 0.5), relative=True)

                  )
    presenter_name = (TextClip(video_info.presenter, fontsize=45, color='white', stroke_width=2)
                      .set_position(('center', 0.60), relative=True)
                      )
    intro = CompositeVideoClip([resized, logo_clip, title, presenter_name])
    title_duration = 5

    return intro.set_duration(title_duration)



filename = sys.argv[1]



conf_file_contents = ConfFileContents.from_dict(load(open(filename), yaml.Loader))



if __name__ == '__main__':
    video_info = VideoInfo(filename, conf_file_contents)
    do_it_all(video_info)