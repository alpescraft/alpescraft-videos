from dataclasses import dataclass, field
from os import path
from os.path import dirname
from pprint import pprint
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
    speaker_image: str

    sound: ClipFile

    slides: ClipFile
    background_image: str


    @classmethod
    def from_dict(cls, param: dict) -> "PresentationInfo":

        get_in_param1 = lambda k1: param[k1]
        def get_in_param(k1, k2):
            if k1 not in param :
                return None
            elif param[k1] is None or k2 not in param[k1]:
                return None
            else:
                return param[k1][k2]

        print(param, param["sound"])
        parts_ = param["speaker"]["parts"]
        parts = [ClipSection.from_clip_spec(x["start"], x["stop"]) for x in parts_]
        sound = param["sound"]
        slides = param["slides"]
        return PresentationInfo(
            title=param["title"],
            jingle=get_in_param("conference","jingle"),
            logo=get_in_param("conference","logo"),
            background_image=get_in_param("conference","background_image"),
            speaker_name=param["speaker_name"],
            speaker_image=get_in_param1("speaker_image"),
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
        return track["extra_offset"] if track is not None and "extra_offset" in track else 0.0

    @classmethod
    def load_video_info(cls, conf_path: str, max_length_seconds: Optional[int] = None):
        import yaml
        from yaml import load
        presentation_dir = dirname(conf_path)
        conference_dir = dirname(presentation_dir)

        defaults = {
            "conference": {
                "jingle": path.join(conference_dir, "jingle.mp3"),
                "logo": path.join(conference_dir, "logo.png"),
                "background_image": path.join(conference_dir, "background.jpg")
            },
            "speaker_image": path.join(presentation_dir, "speaker.png"),
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
        merged = recursive_merge(defaults, param)
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
        elif value is not None:
            result[key] = value
    return result