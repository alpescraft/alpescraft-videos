from dataclasses import dataclass


@dataclass
class MinutesSeconds:
    minutes: int
    seconds: float

    def total_seconds(self) -> float:
        return self.minutes * 60 + self.seconds

    @staticmethod
    def from_comma_separated(spec: str):
        """
        :arg spec of the form mm:ss
        """
        [minutes, seconds] = spec.split(":")
        return MinutesSeconds(minutes=int(minutes), seconds=float(seconds))
