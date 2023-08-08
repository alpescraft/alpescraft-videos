from os import path

from logic.ConfFileContents import ConfFileContents
from logic.SoundSpec import SoundSpec


class VideoInfo:
    def __init__(self, filename: str, conf_file_contents: ConfFileContents) -> None:
        base_dir = path.dirname(filename)
        self.sound_file = SoundSpec(base_dir, conf_file_contents.sound_file, conf_file_contents.sound_file is not None)
        self.conf_file_contents = conf_file_contents

        video_name = filename.removesuffix(".yml")
        self.video_name = video_name
        self.output_file = video_name + ".mp4"
        self.full_path_on_disk = video_name + ".mkv"

        presenter = path.basename(video_name).split(" - ")[0]
        self.title = conf_file_contents.title
        self.presenter = presenter.title()

    def output_thumbnail(self):
        return self.video_name + ".png"
