import datetime
from os.path import getctime

import pytest
from moviepy.video.VideoClip import VideoClip
from moviepy.video.io.VideoFileClip import VideoFileClip


def get_offset_seconds(reference_file_ctime: float, reference_file_offset: int, file_ctime: float) -> float:
    return reference_file_ctime + reference_file_offset - file_ctime


class TestCase:

    @pytest.mark.parametrize(
        ("reference_file_ctime", "reference_file_offset", "file_ctime", "expected_offset_seconds"),
        (
            [10, 2, 12, 0],
            [10, 1, 10, 1],
            [10, 1, 0, 11],
            [0, 11, 10, 1],
            [0.5, 7, 2.3, 5.2],
        ),
    )
    def test_get_offset_seconds(self, reference_file_ctime: float, reference_file_offset: int, file_ctime: float, expected_offset_seconds: float):
        # result = getctime("./test_creation_time.py")
        offset_seconds = get_offset_seconds(reference_file_ctime, reference_file_offset, file_ctime)
        assert offset_seconds == expected_offset_seconds

    def test_time(self) -> None:
        ctime = getctime("/Users/johan/Downloads/Vocal 001.m4a")
        assert datetime.datetime.fromtimestamp(ctime) == 0

    @pytest.mark.skip
    def test_assemble_videos(self):
        target_resolution = (1080, 1920)
        reference_file_offset = 1
        presentation_clip: VideoClip = VideoFileClip("/Volumes/files/alpescraft/ht/ht-jan-1-speaker.mp4", target_resolution=target_resolution) \
            .subclip(reference_file_offset, 4)
        slides_ctime = getctime("/Volumes/files/alpescraft/ht/ht-jan-1-slides.mp4")
        reference_ctime = getctime("/Volumes/files/alpescraft/ht/ht-jan-1-speaker.mp4")
        slides_clip: VideoClip = VideoFileClip("/Volumes/files/alpescraft/ht/ht-jan-1-slides.mp4", target_resolution=target_resolution) \
            .subclip(get_offset_seconds(reference_ctime, 1, slides_ctime), 4)


"""
exiftool -G1 -s -a -time:all ht-jan-01-slides.mkv
[System]        FileModifyDate                  : 2024:01:08 22:37:26+01:00
[System]        FileAccessDate                  : 2024:01:08 22:37:26+01:00
[System]        FileInodeChangeDate             : 2024:01:08 22:37:26+01:00
exiftool -G1 -s -a -QuickTime:CreateDate ht-jan-01-slides.mkv
exiftool -G1 -s -a -QuickTime:CreateDate ht-jan-01-speaker.mp4
[QuickTime]     CreateDate                      : 2024:01:08 21:37:20
exiftool -G1 -s -a -QuickTime:CreateDate ht-jan-01.m4a
[QuickTime]     CreateDate                      : 2024:01:08 21:37:23
"""