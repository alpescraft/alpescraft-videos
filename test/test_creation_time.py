from os.path import getctime

import pytest


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
