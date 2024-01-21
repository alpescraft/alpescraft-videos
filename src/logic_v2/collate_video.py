from typing import Tuple

from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.fx import audio_fadein
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video import fx
from moviepy.video.VideoClip import VideoClip, ImageClip, TextClip, ColorClip
from moviepy.video.compositing import transitions
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx import resize, crop
from moviepy.video.io.VideoFileClip import VideoFileClip

from logic_v2.PresentationInfo import PresentationInfo
from logic_v2.VideoCollageInfo import VideoCollageInfo
from logic_v2.intro import intro_clip, intro_ht
from logic_v2.start_time import get_relative_start_time

HT_COLOR = (121, 2, 87)




def collate_main_part(video_info: PresentationInfo):
    video_collage_info = VideoCollageInfo.from_video_info(video_info)
    start, length = video_collage_info.get_start_length()

    presentation_file_path = video_collage_info.presentation_file_path
    target_resolution = video_collage_info.target_resolution

    # main part
    slides_clip = create_slides_clip(length, presentation_file_path, start, video_collage_info.slides_file)
    presentation_clip = create_presentation_clip(length, presentation_file_path, start)
    presentation_composition = compose_main_video(length, presentation_clip, slides_clip, target_resolution, video_info)
    sound_clip = create_sound_clip(length, presentation_file_path, start, video_collage_info.sound_file)

    intro_duration = 5
    fade_duration = 1.1
    # intro = intro_clip(video_info, intro_duration)
    intro = intro_ht(video_info)

    # blend intro and main part
    final_audio = compose_audio(fade_duration, intro.duration-fade_duration, sound_clip, video_info)
    final_clip = blend_intro_and_main_clip(fade_duration, intro, intro.duration-fade_duration, presentation_composition)

    return final_clip.set_audio(final_audio)


def create_presentation_clip(length, presentation_file_path, start):
    presentation_clip = make_video_clip(presentation_file_path, start, length)
    return presentation_clip


def create_slides_clip(length, presentation_file_path, start, track_file):
    slides_file_path = track_file.file_name
    slides_relative_start = get_relative_start_time(presentation_file_path, slides_file_path,
                                                    start) + track_file.extra_offset
    return make_video_clip(slides_file_path, slides_relative_start, length)


def create_sound_clip(length, presentation_file_path, start, track_file):
    sound_file_path = track_file.file_name
    sound_relative_start = get_relative_start_time(presentation_file_path, sound_file_path,
                                                   start) + track_file.extra_offset
    sound_clip = AudioFileClip(sound_file_path).subclip(sound_relative_start, sound_relative_start + length)
    print("start ", start)
    print("sound_start", sound_relative_start)
    return sound_clip


def compose_main_video(length, presentation_clip, slides_clip, target_resolution, video_info):
    slides_clip = resize.resize(slides_clip, newsize=.75)

    presentation_clip = resize.resize(presentation_clip, newsize=.5)
    w, h = target_resolution
    presentation_clip_540x540 = crop.crop(presentation_clip, width=w * .25, height=h*.5, x_center=w * .25, y_center=h * .25)

    logo_250x600 = crop.crop(ImageClip(video_info.logo), y1=175, y2=600 - 175)
    log_100x240 = resize.resize(logo_250x600, .4)
    location_clip = TextClip("GRENOBLE", fontsize=60, color='white', stroke_color='grey', stroke_width=2)

    background_color = ColorClip(target_resolution, color=HT_COLOR)

    presentation_clips = [
        background_color,
        slides_clip.set_position(("right", "center")),
        presentation_clip_540x540.set_position(("left", "center")),
        log_100x240.set_position((120, 135)),
        location_clip.set_position((100, 1080 * .75 + 40)),
    ]
    presentation_composition = (CompositeVideoClip(presentation_clips, size=target_resolution)
                                .subclip(0, length))
    return presentation_composition


def blend_intro_and_main_clip(fade_duration, intro, intro_duration, presentation_composition):
    intro_with_fade = transitions.crossfadeout(intro, fade_duration)
    main_with_fade = transitions.crossfadein(presentation_composition.set_start(intro_duration), fade_duration)
    final_clip = CompositeVideoClip([intro_with_fade, main_with_fade])
    return final_clip


def compose_audio(fade_duration, intro_duration, sound_clip, video_info):
    jingle = AudioFileClip(video_info.jingle).subclip(0, intro_duration + fade_duration)
    from moviepy.audio.fx import audio_fadeout, audio_normalize
    audio_clips = [audio_fadeout.audio_fadeout(jingle, fade_duration), audio_fadein.audio_fadein(sound_clip, fade_duration).set_start(intro_duration)]
    # normalized_audio_clips = [audio_normalize.audio_normalize(normalized) for normalized in [jingle, sound_clip]]
    final_audio = CompositeAudioClip(audio_clips)
    return final_audio


def make_video_clip(presentation_file_path, start, length):
    presentation_clip: VideoClip = VideoFileClip(presentation_file_path) \
        .subclip(start, start + length)
    presentation_clip.set_audio(None)
    return presentation_clip

def make_video_clip_(presentation_file_path, ratio, start, length):
    presentation_clip: VideoClip = VideoFileClip(presentation_file_path) \
        .subclip(start, start + length)
    presentation_clip.set_audio(None)
    resized_presentation_clip = resize.resize(presentation_clip, newsize=ratio)
    return resized_presentation_clip