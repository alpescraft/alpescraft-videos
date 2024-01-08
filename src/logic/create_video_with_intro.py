from moviepy.audio.AudioClip import concatenate_audioclips, CompositeAudioClip
from moviepy.audio.fx import audio_fadeout, audio_normalize
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import VideoClip
from moviepy.editor import VideoFileClip, CompositeVideoClip, concatenate_videoclips
from logic.VideoInfo import VideoInfo
from logic.intro import intro_clip


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
    # speed trick: use compose for fade and avoid it for speed for the rest of the video
    first_part = concatenate_videoclips([intro.crossfadeout(2), presentation_clip.crossfadein(2)], method="compose") \
        .set_duration(intro_duration) \
        .set_audio(full_audio)
    video_parts = [first_part, presentation_clip.set_start(first_part.end)]
    full_video: VideoClip = concatenate_videoclips(video_parts).set_audio(full_audio)
    return full_video


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
