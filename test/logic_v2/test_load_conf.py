from logic.ClipSection import ClipSection
from logic.MinutesAndSeconds import MinutesSeconds
from logic_v2.VideoInfo import VideoInfo, ReferenceFile, ClipFile

CONF_PATH = "../examples/example-conf.yml"


def test_load_conf() -> None:
    start_seconds = 1
    stop_seconds = 4

    video_info = VideoInfo.load_video_info(CONF_PATH)

    expected_stop = MinutesSeconds(0, stop_seconds)
    expected_start = MinutesSeconds(0, start_seconds)
    assert video_info == expected_video_info(expected_stop, expected_start)


def test_load_conf_max_length() -> None:
    start_seconds = 1
    max_length = 2

    video_info = VideoInfo.load_video_info(CONF_PATH, max_length)

    expected_start = MinutesSeconds(0, start_seconds)
    expected_stop = MinutesSeconds(0, max_length + start_seconds)
    assert video_info == expected_video_info(expected_stop, expected_start)


def expected_video_info(expected_stop, expected_start):
    return VideoInfo(
        speaker=ReferenceFile(
            file_name="./speaker.mp4",
            parts=[
                ClipSection(expected_start, expected_stop)
            ]
        ),
        sound=ClipFile(
            file_name="./sound.m4a"
        ),
        slides=ClipFile(
            file_name="./slides.mp4"
        )
    )


