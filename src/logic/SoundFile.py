from dataclasses import dataclass

from logic.MinutesAndSeconds import MinutesSeconds


@dataclass
class SoundFile:
    file_name: str
    start: MinutesSeconds

    def start_seconds(self) -> float:
        return self.start.total_seconds()

    @classmethod
    def from_sound_file_spec(cls, file_name: str, start: str):
        return cls(file_name=file_name, start=MinutesSeconds.from_comma_separated(start))
