from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.fx import audio_fadeout, audio_normalize
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import VideoClip

from logic.VideoInfo import VideoInfo


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
