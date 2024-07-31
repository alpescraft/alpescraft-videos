import os
import sys
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip


def do_crop(files_to_crop: list):
    """make short clips from all videos that are passed as argument"""
    clips = [VideoFileClip(file) for file in files_to_crop]

    for clip in clips:
        subclip : VideoFileClip = clip.subclip(200, 230)
        filename = os.path.basename(clip.filename)
        destdir = os.path.dirname(clip.filename) + "/clips/"
        subclip.write_videofile( destdir + "/" +  filename, codec='libx264')

if __name__ == '__main__':
    files_to_crop = sys.argv[1:]
    print(files_to_crop)
    do_crop(files_to_crop)