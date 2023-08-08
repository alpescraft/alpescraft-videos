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

TARGET_RESOLUTION = (1080, 1920)

"""
Prepare real video by cropping and concatenating successive videos

1. Background
2. Add Video Title
2b. add music intro
2a. Add logo
3. connect with fade to real video

4. produce a thumbnail for the video as a separate artefact

"""

class MinutesSeconds:


    def __init__(self, spec: str) -> None:
        """
        :arg spec of the form mm:ss
        """
        [minutes, seconds] = spec.split(":")
        self.minutes = minutes
        self.seconds = seconds

    def seconds(self) -> int:
        return int(self.minutes) * 60 + int(self.seconds)


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
class SoundFile:
    file_name: str
    start: str

    def start_seconds(self) -> int:
        [minutes, seconds] = self.start.split(":")
        return int(minutes) * 60 + int(seconds)

@dataclass
class ConfFileContents:
    title: str
    clip: typing.List[ClipSection]
    sound_file: SoundFile


    @classmethod
    def from_dict(cls, param: dict):
        return cls(
            title=param["title"],
            clip=[ClipSection(**x) for x in param["clip"]],
            sound_file=SoundFile(**param["sound_file"])
        )


class SoundSpec:
    full_path_on_disk: str
    start: str
    is_separate: bool

    def __init__(self, base_dir: str, sound_file: SoundFile, exists: bool) -> None:
        self.full_path_on_disk = path.join(base_dir, sound_file.file_name)
        self.start = sound_file.start
        self.is_separate = exists


class VideoInfo:
    def __init__(self, filename: str, conf_file_contents: ConfFileContents) -> None:
        base_dir = path.dirname(filename)
        self.sound_file = SoundSpec(base_dir, conf_file_contents.sound_file, conf_file_contents.sound_file is not None)
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
    end_time = clips[0].stop_seconds()

    presentation_clip: VideoClip = VideoFileClip(video_info.full_path_on_disk, target_resolution=TARGET_RESOLUTION)\
        .subclip(start, end_time)

    intro_duration = 7
    intro = intro_clip(video_info, intro_duration)

    full_audio = compose_audio(video_info, intro_duration, presentation_clip)
    if len(clips) > 1:
        second_presentation_clip = VideoFileClip(video_info.full_path_on_disk, target_resolution=TARGET_RESOLUTION)\
            .subclip(clips[1].start_seconds(), clips[1].stop_seconds())
        full_audio = concatenate_audioclips([full_audio, second_presentation_clip.audio])

    # speed trick: use compose for fade and avoid it for speed for the rest of the video
    first_part = concatenate_videoclips([intro.crossfadeout(2), presentation_clip.crossfadein(2)], method="compose")\
        .set_duration(intro_duration)\
        .set_audio(full_audio)

    video_parts = [first_part, presentation_clip.set_start(first_part.end)]
    if len(clips) > 1:
        video_parts.append(second_presentation_clip)
    full_video: VideoClip = concatenate_videoclips(video_parts).set_audio(full_audio)

    write_thumbnail(full_video, video_info)
    write_video(full_video, video_info)


def write_video(full_video, video_info):
    full_video.write_videofile(video_info.output_file, fps=25, codec='libx264')  # Many options...


def write_thumbnail(full_video, video_info):
    full_video.resize(.5).save_frame(video_info.output_thumbnail(), t=0.1)


# options
# calculate a list of clips with audio, then join everything


def compose_audio(video_info: VideoInfo, intro_duration: int, presentation_clip: VideoClip):
    sound_file_name = f"{resource_dir}/music/bensound-onceagain.mp3"
    fade_duration = 4
    music_clip = AudioFileClip(sound_file_name).subclip(0, intro_duration + fade_duration)

    faded = audio_fadeout.audio_fadeout(music_clip, fade_duration)

    if video_info.sound_file.is_separate:
        presentation_audio = AudioFileClip(video_info.sound_file.full_path_on_disk).subclip(0, presentation_clip.duration)
    else:
        presentation_audio = presentation_clip.audio
    all_clips = [faded, presentation_audio.set_start(intro_duration)]
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