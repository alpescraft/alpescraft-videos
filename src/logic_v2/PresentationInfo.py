from dataclasses import dataclass, field
from typing import List, Optional

from logic.ClipSection import ClipSection
from logic.MinutesAndSeconds import MinutesSeconds


@dataclass
class ReferenceFile:
    file_name: str
    parts: List[ClipSection]

@dataclass
class ClipFile:
    file_name: str
    extra_offset: float = field(default=0.0)


@dataclass
class PresentationInfo:
    # conference:
        # jingle: "/Users/johan/Documents/alpescraft videos 2023/music/jingle_humantalks.mp4"
        # logo: "/Volumes/files/alpescraft/ht/ht-logo.webp"

    title: str
    speaker_name: str

    speaker: ReferenceFile

    sound: ClipFile

    slides: ClipFile

    def __post_init__(self):
        # TODO make this configurable
        self.jingle = "/Volumes/files/alpescraft/ht/jingle_humantalks.mp4"
        self.logo = "/Volumes/files/alpescraft/ht/ht_logo.webp"
        self.background_image = "/Volumes/files/alpescraft/ht/HT background image.jpeg"


    @classmethod
    def from_dict(cls, param) -> "PresentationInfo":
        parts_ = param["speaker"]["parts"]
        parts = [ClipSection.from_clip_spec(x["start"], x["stop"]) for x in parts_]
        sound = param["sound"]
        slides = param["slides"]
        return PresentationInfo(
            title=param["title"],
            speaker_name=param["speaker_name"],
            speaker=ReferenceFile(
                file_name=param["speaker"]["file_name"],
                parts=parts
            ),
            sound=ClipFile(
                file_name=sound["file_name"],
                extra_offset=PresentationInfo.get_extra_offset(sound)
            ),
            slides=ClipFile(
                file_name=slides["file_name"],
                extra_offset=PresentationInfo.get_extra_offset(slides)
            )
        )

    @classmethod
    def get_extra_offset(cls, track):
        return track["extra_offset"] if "extra_offset" in track else 0.0

    @classmethod
    def load_video_info(cls, conf_path: str, max_length_seconds: Optional[int] = None):
        import yaml
        from yaml import load
        video_info = cls.from_dict(load(open(conf_path), yaml.Loader))


        video_info.speaker.parts[0].stop = cls.calculate_stop_position(video_info, max_length_seconds)
        print(video_info)
        return video_info

    @classmethod
    def calculate_stop_position(cls, video_info, max_length_seconds: Optional[int] = None):
        print(max_length_seconds)
        first_part = video_info.speaker.parts[0]
        if max_length_seconds is None:
            return first_part.stop
        stop_minutes_seconds = first_part.stop
        new_stop_seconds = min(stop_minutes_seconds.total_seconds(), first_part.start_seconds()+ max_length_seconds)
        stop_position = MinutesSeconds.from_total_seconds(new_stop_seconds)
        print(stop_position)
        return stop_position


