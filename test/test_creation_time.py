import datetime
from os.path import getctime

import pytest

from logic_v2.collate_video import collate_main_part
from logic_v2.start_time import get_offset_seconds, get_media_info, get_relative_start_time, get_offset_seconds_old

SLIDES_FILE = "../test_files/ht-jan-01-slides.mkv"

SPEAKER_REFERENCE_FILE = "../test_files/ht-jan-01-speaker.mp4"

AUDIO_FILE_EXAMPLE = "../test_files/ht-jan-01.m4a"
MKV_FILE_EXAMPLE = "../test_files/ht-jan-01-slides.mkv"




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
    def test_get_offset_seconds_old(self, reference_file_ctime: float, reference_file_offset: int, file_ctime: float, expected_offset_seconds: float):
        # result = getctime("./test_creation_time.py")
        offset_seconds = get_offset_seconds_old(reference_file_ctime, reference_file_offset, file_ctime)
        assert offset_seconds == expected_offset_seconds

    @pytest.mark.parametrize(
        ("case_name", "reference_file_ctime", "reference_file_offset",  "reference_file_length", "file_ctime", "file_length", "expected_offset_seconds"),
        (
            ["both 0", 10, 0, 5, 10, 5, 0],
            ["different length", 10, 3, 6, 10, 4, 1],
            ["reference created b4", 10, 7, 10, 12, 10, 5],
            ["reference created after", 12, 7, 10, 10, 10, 9],
            # [10, 1, 0, 11],
            # [0, 11, 10, 1],
            # [0.5, 7, 2.3, 5.2],
        ),
    )
    def test_get_offset_seconds(self, case_name: str,
                                reference_file_ctime: float, reference_file_offset: int, reference_file_length: int,
                                file_ctime: float, file_length: int,
                                expected_offset_seconds: float):
        # result = getctime("./test_creation_time.py")
        offset_seconds = get_offset_seconds((reference_file_ctime, reference_file_offset, reference_file_length),
                                            (file_ctime, file_length))
        assert offset_seconds == expected_offset_seconds

    def test_get_relative_start_time(self) -> None:
        offset_in_slides_file = get_relative_start_time(SPEAKER_REFERENCE_FILE, SLIDES_FILE, 1)
        assert offset_in_slides_file == 7

    def test_get_created_date(self) -> None:
        absolute_file_path = AUDIO_FILE_EXAMPLE
        created_date, duration = get_media_info(absolute_file_path)
        assert created_date == datetime.datetime(2024, 1,8, 21,37,23, tzinfo=datetime.timezone(datetime.timedelta(seconds=0)))

        created_date, duration = get_media_info(MKV_FILE_EXAMPLE)
        assert created_date == datetime.datetime(2024, 1, 8, 22, 37, 26, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600))) # + 1

        print()
        print(get_media_info(SPEAKER_REFERENCE_FILE))
        print(get_media_info(SLIDES_FILE))



    def test_timestamp_with_utc(self) -> None:
        normal_date = datetime.datetime.strptime("2024:01:08 21:37:20", '%Y:%m:%d %H:%M:%S')
        utc_date = datetime.datetime.strptime("2024:01:08 22:37:20+01:00", '%Y:%m:%d %H:%M:%S%z')
        assert normal_date.replace(tzinfo=datetime.timezone.utc).timestamp() == utc_date.timestamp()


    @pytest.mark.skip
    def test_assemble_videos(self):
        final_clip = collate_main_part()
        final_clip.write_videofile("../test_files/ht-jan-01-composed.mp4", threads=4, codec = "h264_videotoolbox")


