import enum
from typing import Optional


class MediaType(enum.Enum):
    IMAGE = "image"
    VIDEO = "video"
    SOUND = "sound"


class MediaSearcher:
    def __init__(self, directory_content: list[str]) -> None:
        self.directory_content = directory_content

    def search_for_media(self, base_name: str, media_type) -> Optional[str]:
        allowed_extensions = ["mp3", "m4a", "avi", "mp4", "mkv", "wav"]
        if media_type == MediaType.VIDEO:
            allowed_extensions = ["avi", "mp4", "mkv"]
        if media_type == MediaType.IMAGE:
            allowed_extensions = ["jpg", "jpeg", "png", "webp"]
        for file in self.directory_content:
            filename_parts = file.split(".")
            if filename_parts[0] == base_name and filename_parts[1] in allowed_extensions:
                return file
