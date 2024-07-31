from os import path

from logic import MinutesAndSeconds
from logic.SoundFile import SoundFile


class SoundSpec:
    full_path_on_disk: str
    start: MinutesAndSeconds
    is_separate: bool

    def __init__(self, base_dir: str, sound_file: SoundFile, exists: bool) -> None:
        self.full_path_on_disk = path.join(base_dir, sound_file.file_name)
        self.start = sound_file.start
        self.is_separate = exists
