from moviepy.audio.AudioClip import CompositeAudioClip, concatenate_audioclips
from moviepy.audio.fx import audio_normalize
from moviepy.audio.fx.volumex import volumex
from moviepy.audio.io.AudioFileClip import AudioFileClip


def merge_audio(clip1_fullpath, clip1_end: float, clip2_fullpath: str):
    clip1 = AudioFileClip(clip1_fullpath).subclip(0, clip1_end)
    clip2 = AudioFileClip(clip2_fullpath).subclip(0)
    clip2 = volumex(clip2, 3.4)
    normalized_clips = [clip for clip in [clip1, clip2]]
    return concatenate_audioclips(normalized_clips)



def merge_and_write():
    merged_audio = merge_audio(
        "/Users/johan/Downloads/pascal-audio - improved.mp3",
        3.6,
        "/Users/johan/Documents/alpescraft videos 2023/pascal le merrer - extreme programming, la methode agile.wav"

    )
    merged_audio.write_audiofile("/Users/johan/Documents/alpescraft videos 2023/pascal le merrer - extreme programming, la methode agile_merged.wav")


if __name__ == '__main__':
    merge_and_write()