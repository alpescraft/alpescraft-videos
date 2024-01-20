import datetime


def get_offset_seconds(reference_file_ctime: float, reference_file_offset: int, file_ctime: float) -> float:
    return reference_file_ctime + reference_file_offset - file_ctime

def get_relative_start_time(presentation_file_path: str, slides_file_path: str, start: float) -> float:
    presentation_ctime = get_created_date(presentation_file_path)
    slides_ctime = get_created_date(slides_file_path)
    print(presentation_ctime.timestamp(), slides_ctime.timestamp())
    print("diff " + str(presentation_ctime.timestamp() - slides_ctime.timestamp()))
    slides_relative_start = get_offset_seconds(slides_ctime.timestamp(), start,
                                               presentation_ctime.timestamp())
    print(slides_relative_start)
    return slides_relative_start


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
            return datetime.datetime.strptime(tags[0]["File:FileModifyDate"], '%Y:%m:%d %H:%M:%S%z')
        tags = et.get_tags([absolute_file_path], ["CreateDate"])
        return datetime.datetime.strptime(tags[0]["QuickTime:CreateDate"], '%Y:%m:%d %H:%M:%S').replace(
            tzinfo=datetime.timezone.utc)


