import math
import sys
import typing
from dataclasses import dataclass
from os import path

import moviepy
import yaml
from moviepy.audio.AudioClip import CompositeAudioClip, concatenate_audioclips
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import VideoClip
from yaml import load, dump
from moviepy.editor import VideoFileClip, TextClip, ImageClip, CompositeVideoClip, concatenate_videoclips, AudioClip
from moviepy.video import fx
from moviepy.video.fx import crop, resize
from moviepy.audio.fx import audio_fadeout, audio_normalize





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

    def stop_seconds(self):
        [minutes, seconds] = self.stop.split(":")
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
        self.video_name = video_name
        self.output_file = video_name + ".mp4"
        self.full_path_on_disk = video_name + ".mkv"

        presenter = path.basename(video_name).split(" - ")[0]
        self.title = conf_file_contents.title
        self.presenter = presenter.title()

    def output_thumbnail(self):
        return self.video_name + ".png"


def do_it_all(video_info: VideoInfo) -> None:

    clips = video_info.conf_file_contents.clip
    start = clips[0].start_seconds()
    print("start " + str(start))

    # end time of video
    # max_duration_main_clip = 10
    # end_time = start + max_duration_main_clip
    end_time = clips[0].stop_seconds()

    presentation_clip: VideoClip = VideoFileClip(video_info.full_path_on_disk, target_resolution=(1080, 1920))\
        .subclip(start, end_time)

    intro_duration = 7
    intro = intro_clip(video_info, intro_duration)

    full_audio = compose_audio(intro_duration, presentation_clip)

    # speed trick: use compose for fade and avoid it for speed for the rest of the video
    first_part = concatenate_videoclips([intro.crossfadeout(2), presentation_clip.crossfadein(2)], method="compose")\
        .set_duration(intro_duration)\
        .set_audio(full_audio)

    full_video: VideoClip = concatenate_videoclips([first_part, presentation_clip.set_start(first_part.end)]).set_audio(full_audio)

    full_video.resize(.5).save_frame(video_info.output_thumbnail(), t=0.1)
    full_video.write_videofile(video_info.output_file, fps=25, codec='libx264')  # Many options...


def compose_audio(intro_duration: int, presentation_clip: VideoClip):
    sound_file_name = f"{resource_dir}/music/bensound-onceagain.mp3"
    fade_duration = 4
    music_clip = AudioFileClip(sound_file_name).subclip(0, intro_duration + fade_duration)

    faded = audio_fadeout.audio_fadeout(music_clip, fade_duration)
    presentation_audio = presentation_clip.audio.set_start(intro_duration)
    all_clips = [faded, presentation_audio]
    normalized_clips = [audio_normalize.audio_normalize(normalized) for normalized in all_clips]
    full_audio = CompositeAudioClip(normalized_clips)

    return full_audio


def intro_clip(video_info: VideoInfo, intro_duration):
    logo = f"{resource_dir}/Logo/03-AlpesCraft_Couleurs-M.png"
    logo_clip = ImageClip(logo).set_position(('center', 0.2), relative=True)

    background_image = f"{resource_dir}/Logo/bandeau.jpg"
    image_clip = ImageClip(background_image)
    cropped_image = crop.crop(image_clip, x1=0, y1=0, width=1920)
    resized = resize.resize(cropped_image, newsize=(1920, 1080))
    title = (TextClip(video_info.title, fontsize=52, color='white', stroke_width=3)
                  .set_position(('center', 0.5), relative=True))
    presenter_name = (TextClip(video_info.presenter, fontsize=45, color='white', stroke_width=2)
                      .set_position(('center', 0.60), relative=True))

    intro = CompositeVideoClip([resized, logo_clip, title, presenter_name])


    return intro.set_duration(intro_duration)



filename = sys.argv[1]
resource_dir = sys.argv[2]


conf_file_contents = ConfFileContents.from_dict(load(open(filename), yaml.Loader))


if __name__ == '__main__':
    video_info = VideoInfo(filename, conf_file_contents)
    do_it_all(video_info)