from dataclasses import dataclass

from logic_v2.MinutesAndSeconds import MinutesSeconds


@dataclass
class ClipSection:

    start: MinutesSeconds
    stop: MinutesSeconds

    def start_seconds(self) -> float:
        return self.start.total_seconds()

    def stop_seconds(self):
        return self.stop.total_seconds();

    @classmethod
    def from_clip_spec(cls, start: str, stop: str):
        return cls(start=MinutesSeconds.from_comma_separated(start), stop=MinutesSeconds.from_comma_separated(stop))
