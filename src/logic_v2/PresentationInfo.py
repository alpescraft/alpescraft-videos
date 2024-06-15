from dataclasses import dataclass, field
from os import path
from os.path import dirname
from typing import List, Optional, Any

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
class Conference:
    jingle: str
    logo: str

@dataclass
class PresentationInfo:

    title: str

    jingle: str
    logo: str

    # TODO type this better, it is split later on
    speaker_name: str

    speaker: ReferenceFile

    sound: ClipFile

    slides: ClipFile

    def __post_init__(self):
        self.background_image = "/Volumes/files/alpescraft/ht/HT background image.jpeg"


    @classmethod
    def from_dict(cls, param: dict) -> "PresentationInfo":

        get_in_param = lambda k1, k2: param[k1][k2]

        parts_ = param["speaker"]["parts"]
        parts = [ClipSection.from_clip_spec(x["start"], x["stop"]) for x in parts_]
        sound = param["sound"]
        slides = param["slides"]
        return PresentationInfo(
            title=param["title"],
            jingle=get_in_param("conference","jingle"),
            logo=get_in_param("conference","logo"),
            speaker_name=param["speaker_name"],
            speaker=ReferenceFile(
                file_name=get_in_param("speaker","file_name"),
                parts=parts
            ),
            sound=ClipFile(
                file_name=get_in_param("sound", "file_name"),
                extra_offset=PresentationInfo.get_extra_offset(sound)
            ),
            slides=ClipFile(
                file_name=get_in_param("slides", "file_name"),
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
        presentation_dir = dirname(conf_path)
        conference_dir = dirname(presentation_dir)

        defaults = {
            "conference": {
                "jingle": path.join(conference_dir, "jingle.mp4"),
                "logo": path.join(conference_dir, "logo.png")
            },
            "speaker": {
                "file_name": path.join(presentation_dir, "speaker.mp4"),
            },
            "sound": {
                "file_name": path.join(presentation_dir, "sound.m4a"),
            },
            "slides": {
                "file_name": path.join(presentation_dir, "slides.mkv"),
            }
        }
        param = load(open(conf_path), yaml.Loader)
        if not param:
            raise ValueError("No data in the conf file: " + conf_path)
        merged = recursive_merge(param, defaults)
        video_info = cls.from_dict(merged)

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

def recursive_merge(dict1, dict2):
    result = dict1.copy()  # Start with a copy of dict1
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = recursive_merge(result[key], value)
        else:
            result[key] = value
    return result