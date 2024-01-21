from dataclasses import dataclass

from logic_v2.VideoInfo import VideoInfo, ClipFile


@dataclass
class VideoCollageInfo:
    presentation_file_path: str
    slides_file: ClipFile
    sound_file: ClipFile
    presentation_start_stop_seconds: (float, float)
    target_resolution: (int, int)

    def get_start_length(self):
        start, stop = self.presentation_start_stop_seconds
        return start, stop - start

    @classmethod
    def from_video_info(cls, video_info: VideoInfo)->"VideoCollageInfo":
        first_part = video_info.speaker.parts[0]
        return VideoCollageInfo(
            presentation_file_path=video_info.speaker.file_name,
            slides_file=video_info.slides,
            presentation_start_stop_seconds=(first_part.start_seconds(), first_part.stop_seconds()),
            sound_file=video_info.sound,
            target_resolution=(1920, 1080)
        )
