import datetime
from dataclasses import dataclass
from os.path import getctime

import pytest
from moviepy.video.VideoClip import VideoClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx import resize
from moviepy.video.io.VideoFileClip import VideoFileClip

AUDIO_FILE_EXAMPLE = "/Users/johan/Downloads/Vocal 001.m4a"
MKV_FILE_EXAMPLE = "/Users/johan/Movies/2024-01-09 19-07-11.mkv"


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

    def test_gettime_exif(self) -> None:
        absolute_file_path = AUDIO_FILE_EXAMPLE
        created_date = get_created_date(absolute_file_path)
        assert created_date == datetime.datetime(2024, 1,8, 21,37,23, tzinfo=datetime.timezone(datetime.timedelta(seconds=0)))

        created_date = get_created_date(MKV_FILE_EXAMPLE)
        assert created_date == datetime.datetime(2024, 1,9, 19,7,22, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600))) # + 1

        print()
        print(get_created_date("../test_files/ht-jan-01-speaker.mp4"))
        print(get_created_date("../test_files/ht-jan-01-slides.mkv"))



    def test_timestamp_with_utc(self) -> None:
        normal_date = datetime.datetime.strptime("2024:01:08 21:37:20", '%Y:%m:%d %H:%M:%S')
        utc_date = datetime.datetime.strptime("2024:01:08 22:37:20+01:00", '%Y:%m:%d %H:%M:%S%z')
        assert normal_date.replace(tzinfo=datetime.timezone.utc).timestamp() == utc_date.timestamp()

    def test_time(self) -> None:
        ctime = getctime(AUDIO_FILE_EXAMPLE)
        assert datetime.datetime.fromtimestamp(ctime) == datetime.datetime(2024, 1, 9, 0, 34, 55, 234462)

    @pytest.mark.skip
    def test_assemble_videos(self):
        final_clip = compose_video()
        final_clip.write_videofile("../test_files/ht-jan-01-composed.mp4", threads=4, codec = "h264_videotoolbox")



def get_created_date(absolute_file_path: str) -> datetime.datetime:
    from exiftool import ExifToolHelper
    """    
    Get the actual creation date of a media file
    """
    with ExifToolHelper() as et:

        """
        
        The following code stems from the fact that mkv files has different metadata than mp4/m4a files.
        For instance 
    
        MKV files ex :
            exiftool -G1 -s -a -time:all ht-jan-01-slides.mkv
            [System]        FileModifyDate                  : 2024:01:08 22:37:26+01:00
            [System]        FileAccessDate                  : 2024:01:08 22:37:26+01:00
            [System]        FileInodeChangeDate             : 2024:01:08 22:37:26+01:00
    
        audio and mp4 files ex :
            exiftool -G1 -s -a -QuickTime:CreateDate ht-jan-01-speaker.mp4
            [QuickTime]     CreateDate                      : 2024:01:08 21:37:20
    
            exiftool -G1 -s -a -QuickTime:CreateDate ht-jan-01.m4a
            [QuickTime]     CreateDate                      : 2024:01:08 21:37:23

        """
        if absolute_file_path.endswith(".mkv"):
            tags = et.get_tags([absolute_file_path], ["FileModifyDate"])
            return datetime.datetime.strptime( tags[0]["File:FileModifyDate"],'%Y:%m:%d %H:%M:%S%z')
        tags = et.get_tags([absolute_file_path], ["CreateDate"])
        return datetime.datetime.strptime( tags[0]["QuickTime:CreateDate"],'%Y:%m:%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc)


@dataclass
class VideoCollageInfo:
    presentation_file_path: str
    slides_file_path: str
    presentation_start_stop_seconds: (float, float)
    target_resolution: (int, int)

    def get_start_length(self):
        start, stop = self.presentation_start_stop_seconds
        return start, stop - start


def compose_video(video_collage_info: VideoCollageInfo):
    start, length = video_collage_info.get_start_length()

    presentation_file_path = video_collage_info.presentation_file_path
    presentation_clip = make_video_clip(presentation_file_path, .25, start, length)

    slides_file_path = video_collage_info.slides_file_path
    slides_relative_start = get_relative_start_time(presentation_file_path, slides_file_path, start)
    slides_clip: VideoClip = make_video_clip(slides_file_path, .75, slides_relative_start, length)

    target_resolution = video_collage_info.target_resolution
    final_clip = CompositeVideoClip([
            presentation_clip.set_position(("left", "bottom")),
            slides_clip.set_position(("right", "top"))],
        size=target_resolution).subclip(0, length)
    return final_clip


def make_video_clip(presentation_file_path, ratio, start, length):
    presentation_clip: VideoClip = VideoFileClip(presentation_file_path) \
        .subclip(start, start + length)
    resized_presentation_clip = resize.resize(presentation_clip, newsize=ratio)
    return resized_presentation_clip


def get_relative_start_time(presentation_file_path, slides_file_path, start):
    presentation_ctime = get_created_date(presentation_file_path)
    slides_ctime = get_created_date(slides_file_path)
    print(presentation_ctime.timestamp(), slides_ctime.timestamp())
    print("diff " + str(presentation_ctime.timestamp() - slides_ctime.timestamp()))
    slides_relative_start = get_offset_seconds(slides_ctime.timestamp(), start,
                                               presentation_ctime.timestamp())
    print(slides_relative_start)
    return slides_relative_start

