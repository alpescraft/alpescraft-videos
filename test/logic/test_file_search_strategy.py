import pytest

from logic.media_searcher import MediaType, MediaSearcher


@pytest.mark.parametrize("extension", [
    "m4a" ,
    "mp3",
    "avi",
    "mp4",
    "mkv",
    "wav",
])
def test_sound_file_gets_sound_or_video(extension) -> None:
    existing_file = "sound." + extension
    assert MediaSearcher([existing_file]).search_for_media("sound", MediaType.SOUND) == existing_file


@pytest.mark.parametrize("existing_files", [
    [],
    ["something_sound.mp3"],
    ["sound_something.mp3"],
    ["sound.bin"],
    ["sound.mp"],
    ["sound.av"],
    ["sound.m4"],
])
def test_sound_file_not_found(existing_files) -> None:
    assert MediaSearcher(existing_files).search_for_media("sound", MediaType.SOUND) is None

@pytest.mark.parametrize("extension", [
    "avi",
    "mp4",
    "mkv",
])
def test_video_file_gets_only_video_video(extension) -> None:
    existing_file = "speaker." + extension
    assert MediaSearcher([existing_file]).search_for_media("speaker", MediaType.VIDEO) == existing_file


@pytest.mark.parametrize("existing_files", [
    [],
    ["something_basename.mp3"],
    ["basename_something.mp3"],
    ["basename.bin"],
    ["basename.mp3"], # wrong filetype
    ["basename.m4a"], # wrong filetype
    ["basename.wav"], # wrong filetype
])
def test_video_file_not_found(existing_files) -> None:
    assert MediaSearcher(existing_files).search_for_media("basename", MediaType.VIDEO) is None


@pytest.mark.parametrize("extension", [
    "jpg",
    "jpeg",
    "png",
    "webp",
])
def test_image_file_gets_only_images(extension) -> None:
    existing_file = "speaker." + extension
    assert MediaSearcher([existing_file]).search_for_media("speaker", MediaType.IMAGE) == existing_file



@pytest.mark.parametrize("existing_files", [
    [],
    ["something_basename.mp3"],
    ["basename_something.mp3"],
    ["basename.bin"],
    ["basename.avi"], # wrong filetype
    ["basename.mkv"], # wrong filetype
    ["basename.mp4"], # wrong filetype
    ["basename.mp3"], # wrong filetype
    ["basename.m4a"], # wrong filetype
    ["basename.wav"], # wrong filetype
])
def test_video_file_not_found(existing_files) -> None:
    assert MediaSearcher(existing_files).search_for_media("basename", MediaType.IMAGE) is None


def test_finds_first_matching():
    existing_files = ["sound.mp3", "sound.m4a"]
    assert MediaSearcher(existing_files).search_for_media("sound", MediaType.SOUND) == "sound.mp3"

    existing_files = ["sound.m4a", "sound.mp3"]
    assert MediaSearcher(existing_files).search_for_media("sound", MediaType.SOUND) == "sound.m4a"