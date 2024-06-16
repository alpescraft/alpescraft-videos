from moviepy.video.VideoClip import TextClip


class Region:

    def __init__(self, region_x, region_y, region_width, region_height):
        super().__init__()
        self.region_height = region_height
        self.region_width = region_width
        self.region_y = region_y
        self.region_x = region_x

    def calculate_center(self, element_width, element_height):
        # # Calculate the center position for the text clip within the specified region

        element_x = self.region_x + (self.region_width - element_width) / 2
        element_y = self.region_y + (self.region_height - element_height) / 2
        return element_x, element_y


def create_centered_textclip_with_respect_to_region_multiline(region, text, text_style):
    speaker_names = text.split(" ")
    text = '\n'.join(speaker_names)
    text_len = max(len(speaker_names[0]), len(speaker_names[1]))

    fontsize_width = region.region_width / text_len * 1.45
    fontsize_height = region.region_height / (len(speaker_names)+.3)
    fontsize = min(fontsize_width, fontsize_height)
    presenter_name_clip = TextClip(text, fontsize=fontsize, align='center', **text_style)
    center_pos = region.calculate_center(*presenter_name_clip.size)
    presenter_name_clip = presenter_name_clip.set_position(center_pos)
    return presenter_name_clip


def create_centered_textclip_with_respect_to_region(region, text, text_style):
    text_len = len(text)
    fontsize_width = region.region_width / text_len * 1.45
    fontsize_height = region.region_height / 1.7
    fontsize = min(fontsize_width, fontsize_height)
    presenter_name_clip = TextClip(text, fontsize=fontsize, align='center', **text_style)
    center_pos = region.calculate_center(*presenter_name_clip.size)
    presenter_name_clip = presenter_name_clip.set_position(center_pos)
    return presenter_name_clip
