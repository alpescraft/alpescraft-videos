import datetime
import os.path
from typing import Tuple


def get_offset_seconds_old(reference_file_ctime: float, reference_file_offset: int, file_ctime: float) -> float:
    return reference_file_ctime + reference_file_offset - file_ctime
def get_offset_seconds(reference_file: Tuple[float, int, int], file: Tuple[float, int]) -> float:
    reference_file_ctime, reference_file_offset, reference_file_length = reference_file
    file_ctime, file_length = file
    return (reference_file_ctime - reference_file_length) + reference_file_offset - (file_ctime - file_length)

def get_relative_start_time(reference_file_path: str, other_file_path: str, start_seconds_in_reference_file: float) -> float:
    reference_time, reference_duration = get_media_info(reference_file_path)
    other_time, other_duration = get_media_info(other_file_path)
    print(reference_time, other_time)
    print("diff " + str(reference_time.timestamp() - other_time.timestamp()))
    other_relative_start = get_offset_seconds((reference_time.timestamp(), start_seconds_in_reference_file, reference_duration),
                                               (other_time.timestamp(), other_duration))
    return other_relative_start


def get_media_info(absolute_file_path: str) -> (datetime.datetime, int):
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


        duration
        [Matroska]      Duration                        : 0:10:45.117
        [QuickTime]     Duration                        : 15.18 


        """

        assert os.path.exists(absolute_file_path), f"File {absolute_file_path} does not exist"
        if absolute_file_path.endswith(".mkv"):
            tags = et.get_tags([absolute_file_path], ["FileModifyDate", "Duration"])[0]
            created_time = datetime.datetime.strptime(tags["File:FileModifyDate"], '%Y:%m:%d %H:%M:%S%z')

            raw_duration = tags["Matroska:Duration"]
            [hours, minutes, seconds] = raw_duration.split(":")
            total_seconds = int(hours) * 3600 + int(minutes) * 60 + float(seconds)

            return created_time, total_seconds

        tags = et.get_tags([absolute_file_path], ["CreateDate", "Duration"])[0]
        created_date = datetime.datetime.strptime(tags["QuickTime:CreateDate"], '%Y:%m:%d %H:%M:%S').replace(
            tzinfo=datetime.timezone.utc)
        raw_duration = tags["QuickTime:Duration"]
        print(f"start date {absolute_file_path}: {created_date - datetime.timedelta(seconds=raw_duration)}")
        print("created_date, raw_duration: ", created_date, raw_duration, absolute_file_path)
        return created_date, float(raw_duration)


