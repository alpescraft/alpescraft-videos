from logic.ClipSection import ClipSection
from logic.MinutesAndSeconds import MinutesSeconds
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


# write test that is using a minimal conf file and gets most data from defaults
def test_load_conf_minimal() -> None:

    video_info = PresentationInfo.load_video_info("../examples/minimal-conf.yml")

    expected_presentation_info = PresentationInfo(
        jingle="../jingle.mp3",
        logo="../logo.png",
        title="awesome session",
        speaker_name="John Doe",
        speaker_image="../examples/speaker.png",
        background_image="../background.jpg",
        speaker=ReferenceFile(
            file_name="../examples/speaker.mp4",
            parts=[
                ClipSection(MinutesSeconds(0, 0.0), MinutesSeconds(0, 4.0))
            ]
        ),
        sound=ClipFile(
            file_name="../examples/sound.m4a",
            extra_offset=0.0
        ),
        slides=ClipFile(
            file_name="../examples/slides.mkv",
            extra_offset=0.0
        )
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


