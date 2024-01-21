from typing import Tuple

from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video import fx
from moviepy.video.VideoClip import VideoClip, ImageClip, TextClip, ColorClip
from moviepy.video.compositing import transitions
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx import resize, crop
from moviepy.video.io.VideoFileClip import VideoFileClip

from logic_v2.PresentationInfo import PresentationInfo
from logic_v2.VideoCollageInfo import VideoCollageInfo
from logic_v2.intro import intro_clip
from logic_v2.start_time import get_relative_start_time


def collate_main_part(video_info: PresentationInfo, presenter_slide_ratio: Tuple[float, float]):
    video_collage_info = VideoCollageInfo.from_video_info(video_info)
    start, length = video_collage_info.get_start_length()

    presentation_file_path = video_collage_info.presentation_file_path
    target_resolution = video_collage_info.target_resolution

    slides_clip = create_slides_clip(length, presentation_file_path, presenter_slide_ratio, start,
                                     video_collage_info.slides_file)

    sound_clip = create_sound_clip(length, presentation_file_path, start, video_collage_info.sound_file)

    presentation_composition = create_presentation_clip(length, presentation_file_path, slides_clip, start,
                                                        target_resolution, video_info)

    intro_duration = 2
    fade_duration = 2
    intro = intro_clip(video_info, intro_duration)

    final_audio = compose_audio(fade_duration, intro_duration, sound_clip, video_info)

    final_clip = blend_intro_and_main_clip(fade_duration, intro, intro_duration, presentation_composition)

    return final_clip.set_audio(final_audio)


def create_presentation_clip(length, presentation_file_path, slides_clip, start, target_resolution, video_info):
    presentation_clip = make_video_clip(presentation_file_path, .5, start, length)
    w, h = 1920 * .5, 1080 * .5
    presentation_clip = crop.crop(presentation_clip, width=w * .5, height=h, x_center=w / 2, y_center=h / 2)
    presentation_composition = compose_main_video(length, presentation_clip, slides_clip, target_resolution, video_info)
    return presentation_composition


def create_slides_clip(length, presentation_file_path, presenter_slide_ratio, start, track_file):
    slides_file_path = track_file.file_name
    slides_relative_start = get_relative_start_time(presentation_file_path, slides_file_path,
                                                    start) + track_file.extra_offset
    slides_clip: VideoClip = make_video_clip(slides_file_path, presenter_slide_ratio[1], slides_relative_start, length)
    return slides_clip


def create_sound_clip(length, presentation_file_path, start, track_file):
    sound_file_path = track_file.file_name
    sound_relative_start = get_relative_start_time(presentation_file_path, sound_file_path,
                                                   start) + track_file.extra_offset
    sound_clip = AudioFileClip(sound_file_path).subclip(sound_relative_start, sound_relative_start + length)
    print("start ", start)
    print("sound_start", sound_relative_start)
    return sound_clip


def compose_main_video(length, presentation_clip, slides_clip, target_resolution, video_info):
    logo_250x600 = crop.crop(ImageClip(video_info.logo), y1=175, y2=600 - 175)
    log_100x240 = resize.resize(logo_250x600, .4)
    logo_clip_above_speaker = log_100x240.set_position((120, 135))
    location_clip = (
        TextClip("GRENOBLE", fontsize=60, color='white', stroke_color='grey', stroke_width=2)).set_position(
        (100, 1080 * .75 + 40))
    background_color = ColorClip(target_resolution, color=(110, 20, 86))
    presentation_clips = [
        background_color,
        slides_clip.set_position(("right", "center")),
        presentation_clip.set_position(("left", "center")),
        logo_clip_above_speaker,
        location_clip,
    ]
    presentation_composition = (CompositeVideoClip(presentation_clips, size=target_resolution)
                                .subclip(0, length))
    return presentation_composition


def blend_intro_and_main_clip(fade_duration, intro, intro_duration, presentation_composition):
    final_clip = CompositeVideoClip(
        [transitions.crossfadeout(intro, fade_duration), transitions.crossfadein(presentation_composition.set_start(
            intro_duration), fade_duration)])
    return final_clip


def compose_audio(fade_duration, intro_duration, sound_clip, video_info):
    jingle = AudioFileClip(video_info.jingle).subclip(0, intro_duration + fade_duration)
    from moviepy.audio.fx import audio_fadeout, audio_normalize
    audio_clips = [audio_fadeout.audio_fadeout(jingle, fade_duration), sound_clip.set_start(intro_duration)]
    # normalized_audio_clips = [audio_normalize.audio_normalize(normalized) for normalized in [jingle, sound_clip]]
    final_audio = CompositeAudioClip(audio_clips)
    return final_audio


def make_video_clip(presentation_file_path, ratio, start, length):
    presentation_clip: VideoClip = VideoFileClip(presentation_file_path) \
        .subclip(start, start + length)
    presentation_clip.set_audio(None)
    resized_presentation_clip = resize.resize(presentation_clip, newsize=ratio)
    return resized_presentation_clip

def make_video_clip_(presentation_file_path, ratio, start, length):
    presentation_clip: VideoClip = VideoFileClip(presentation_file_path) \
        .subclip(start, start + length)
    presentation_clip.set_audio(None)
    resized_presentation_clip = resize.resize(presentation_clip, newsize=ratio)
    return resized_presentation_clip