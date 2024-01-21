from dataclasses import dataclass
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


@dataclass
class VideoInfo:
    # conference:
        # jingle: "/Users/johan/Documents/alpescraft videos 2023/music/bensound-onceagain.mp3"
        # logo: "/Volumes/files/alpescraft/ht/ht-logo.webp"


    # intro:
        # title: "La charge mentale des dèvs"
        # speaker_name: "Julien LENORMAND"

    speaker: ReferenceFile

    sound: ClipFile

    slides: ClipFile

    @classmethod
    def from_dict(cls, param) -> "VideoInfo":
        parts_ = param["speaker"]["parts"]
        parts = [ClipSection.from_clip_spec(x["start"], x["stop"]) for x in parts_]
        return VideoInfo(
            speaker=ReferenceFile(
                file_name=param["speaker"]["file_name"],
                parts=parts
            ),
            sound=ClipFile(
                file_name=param["sound"]["file_name"]
            ),
            slides=ClipFile(
                file_name=param["slides"]["file_name"]
            )
        )

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


