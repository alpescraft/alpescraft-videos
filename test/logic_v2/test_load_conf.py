from logic_v2.ClipSection import ClipSection
from logic_v2.MinutesAndSeconds import MinutesSeconds
from logic_v2.PresentationInfo import PresentationInfo, ReferenceFile, ClipFile

CONF_PATH = "../examples/example-conf.yml"


def test_load_conf() -> None:
    start_seconds = 1.0
    stop_seconds = 4.0

    video_info = PresentationInfo.load_video_info(CONF_PATH)

    expected_stop = MinutesSeconds(0, stop_seconds)
    expected_start = MinutesSeconds(0, start_seconds)
    assert video_info == expected_video_info(expected_stop, expected_start)


def test_load_conf_max_length() -> None:
    start_seconds = 1.0
    max_length = 2.0

    video_info = PresentationInfo.load_video_info(CONF_PATH, max_length)

    expected_start = MinutesSeconds(0, start_seconds)
    expected_stop = MinutesSeconds(0, max_length + start_seconds)
    assert video_info == expected_video_info(expected_stop, expected_start)


def test_when_info_is_omitted_it_deduces_from_location_using_any_extensions_of_the_deduced_files() -> None:

        conf_file_location = "../test_files/search-strategy-for-defaults/search-strategy-session/minimal-conf.yml"
        video_info = PresentationInfo.load_video_info(conf_file_location)

        expected_presentation_info = PresentationInfo(
            jingle="../test_files/search-strategy-for-defaults/jingle.m4a", # not mp3
            logo="../test_files/search-strategy-for-defaults/logo.jpeg", # not png
            speaker_image="../test_files/search-strategy-for-defaults/search-strategy-session/speaker.jpeg", # not png
            background_image="../test_files/search-strategy-for-defaults/background.jpeg", # not jpg
            speaker=ReferenceFile(
                file_name="../test_files/search-strategy-for-defaults/search-strategy-session/speaker.avi", # not mp4
                parts=[
                    ClipSection(MinutesSeconds(0, 0.0), MinutesSeconds(0, 4.0))
                ]
            ),
            sound=ClipFile(
                file_name="../test_files/search-strategy-for-defaults/search-strategy-session/sound.mp3", # not m4a
                extra_offset=0.0
            ),
            slides=ClipFile(
                file_name="../test_files/search-strategy-for-defaults/search-strategy-session/slides.avi", # not mkv
                extra_offset=0.0
            ),
            title="awesome session",
            speaker_name="John Doe",
        )
        assert video_info == expected_presentation_info

def expected_video_info(expected_stop, expected_start):
    return PresentationInfo(
        jingle="./work/img/jingle_humantalks.mp4",
        logo="./work/img/ht-logo.webp",
        title="awesome session",
        speaker_name="John Doe",
        speaker_image="./work/img/speaker.jpg",
        background_image="./work/img/background.jpg",
        speaker=ReferenceFile(
            file_name="./speaker.mp4",
            parts=[
                ClipSection(expected_start, expected_stop)
            ]
        ),
        sound=ClipFile(
            file_name="./sound.m4a",
            extra_offset=0.9
        ),
        slides=ClipFile(
            file_name="./slides.mp4",
            extra_offset=0.0
        )
    )


