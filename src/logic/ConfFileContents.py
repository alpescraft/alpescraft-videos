import typing
from dataclasses import dataclass

from logic.ClipSection import ClipSection
from logic.SoundFile import SoundFile


@dataclass
class ConfFileContents:
    title: str
    clips: typing.List[ClipSection]
    sound_file: SoundFile

    @classmethod
    def from_dict(cls, param: dict):
        sound_file_spec = param["sound_file"]
        sound_file = SoundFile.from_sound_file_spec(sound_file_spec["file_name"], sound_file_spec["start"])
        clips = [ClipSection.from_clip_spec(x["start"], x["stop"]) for x in param["clip"]]
        return cls(
            title=param["title"],
            clips=clips,
            sound_file=sound_file
        )
