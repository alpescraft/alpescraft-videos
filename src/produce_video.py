import sys

import yaml
from moviepy.audio.AudioClip import CompositeAudioClip, concatenate_audioclips
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import VideoClip
from yaml import load
from moviepy.editor import VideoFileClip, TextClip, ImageClip, CompositeVideoClip, concatenate_videoclips
from moviepy.video.fx import crop, resize
from moviepy.audio.fx import audio_fadeout, audio_normalize

from logic.ConfFileContents import ConfFileContents
from logic.VideoInfo import VideoInfo

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
    intro = intro_clip(video_info, intro_duration, resource_dir)
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


def compose_audio(video_info: VideoInfo, intro_duration: int, presentation_clip: VideoClip, resource_dir: str):
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


def intro_clip(video_info: VideoInfo, intro_duration: int, resource_dir: str):
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
    do_it_all(video_info, resource_dir)