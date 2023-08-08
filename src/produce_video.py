import sys

import yaml
from moviepy.audio.AudioClip import concatenate_audioclips
from moviepy.video.VideoClip import VideoClip
from yaml import load
from moviepy.editor import VideoFileClip, CompositeVideoClip, concatenate_videoclips

from compose_audio import compose_audio
from logic.ConfFileContents import ConfFileContents
from logic.VideoInfo import VideoInfo
from logic.intro import intro_clip

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


def create_video_with_intro(video_info: VideoInfo, resource_dir: str):
    clips = video_info.conf_file_contents.clips
    start = clips[0].start_seconds()
    end_time = clips[0].stop_seconds()
    target_resolution = (1080, 1920)
    presentation_clip: VideoClip = VideoFileClip(video_info.full_path_on_disk, target_resolution=target_resolution) \
        .subclip(start, end_time)
    intro_duration = 7
    intro: CompositeVideoClip = intro_clip(video_info, intro_duration, resource_dir)
    full_audio = compose_audio(video_info, intro_duration, presentation_clip, resource_dir)
    if len(clips) > 1:
        second_presentation_clip = VideoFileClip(video_info.full_path_on_disk, target_resolution=target_resolution) \
            .subclip(clips[1].start_seconds(), clips[1].stop_seconds())
        full_audio = concatenate_audioclips([full_audio, second_presentation_clip.audio])
    # speed trick: use compose for fade and avoid it for speed for the rest of the video
    first_part = concatenate_videoclips([intro.crossfadeout(2), presentation_clip.crossfadein(2)], method="compose") \
        .set_duration(intro_duration) \
        .set_audio(full_audio)
    video_parts = [first_part, presentation_clip.set_start(first_part.end)]
    if len(clips) > 1:
        video_parts.append(second_presentation_clip)
    full_video: VideoClip = concatenate_videoclips(video_parts).set_audio(full_audio)
    return full_video


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