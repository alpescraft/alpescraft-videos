from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import VideoClip, ImageClip, TextClip, ColorClip
from moviepy.video.compositing import transitions
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx import resize, crop
from moviepy.video.io.VideoFileClip import VideoFileClip

from logic_v2.PresentationInfo import PresentationInfo
from logic_v2.VideoCollageInfo import VideoCollageInfo
from logic_v2.intro import intro_ht
from logic_v2.start_time import get_relative_start_time

HT_COLOR = (121, 2, 87)

def collate_main_part_without_intro(video_info: PresentationInfo):
    video_collage_info = VideoCollageInfo.from_video_info(video_info)
    start, length = video_collage_info.get_start_length()

    presentation_file_path = video_collage_info.presentation_file_path
    target_resolution = video_collage_info.target_resolution

    # main part
    slides_clip = create_slides_clip(length, presentation_file_path, start, video_collage_info.slides_file)
    presentation_clip = create_presentation_clip(length, presentation_file_path, start)
    presentation_composition = compose_main_video(length, presentation_clip, slides_clip, target_resolution, video_info)
    sound_clip = create_sound_clip(length, presentation_file_path, start, video_collage_info.sound_file)
    return presentation_composition.set_audio(sound_clip)


def collate_main_part(video_info: PresentationInfo):
    video_collage_info = VideoCollageInfo.from_video_info(video_info)
    start, length = video_collage_info.get_start_length()

    presentation_file_path = video_collage_info.presentation_file_path
    target_resolution = video_collage_info.target_resolution

    # main part
    slides_clip = create_slides_clip(length, presentation_file_path, start, video_collage_info.slides_file)
    presentation_clip = create_presentation_clip(length, presentation_file_path, start)
    presentation_composition = compose_main_video(length, presentation_clip, slides_clip, target_resolution, video_info)
    sound_clip = create_sound_clip(length, presentation_file_path, start, video_collage_info.sound_file)

    fade_duration = 1.1
    intro = intro_ht(video_info)

    # blend intro and main part
    final_audio = compose_audio(fade_duration, intro.duration, sound_clip, video_info)
    final_clip = blend_intro_and_main_clip(fade_duration, intro, intro.duration, presentation_composition)

    return final_clip.set_audio(final_audio)


def create_presentation_clip(length, presentation_file_path, start):
    return make_video_clip(presentation_file_path, start, length)


def create_slides_clip(length, presentation_file_path, start, track_file):
    slides_file_path = track_file.file_name
    slides_relative_start = (get_relative_start_time(presentation_file_path, slides_file_path, start)
                             + track_file.extra_offset)
    return make_video_clip(slides_file_path, slides_relative_start, length)


def create_sound_clip(length, presentation_file_path, start, track_file):
    sound_file_path = track_file.file_name
    sound_relative_start = (get_relative_start_time(presentation_file_path, sound_file_path, start)
                            + track_file.extra_offset)
    return AudioFileClip(sound_file_path).subclip(sound_relative_start, sound_relative_start + length)


def fade_in_and_cut_to_length(clip, length, fade_duration):
    seconds_after_main_part = 4
    start_and_duration_adjusted = clip.set_start(seconds_after_main_part).set_duration(length - seconds_after_main_part)
    return transitions.crossfadein(start_and_duration_adjusted, fade_duration)


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


def compose_main_video(length, presentation_clip, slides_clip, target_resolution, video_info: PresentationInfo):
    slides_clip = resize.resize(slides_clip, newsize=.75)

    w, h = target_resolution
    presentation_clip = resize.resize(presentation_clip, newsize=.5)
    presentation_clip_540x540 = crop.crop(presentation_clip, width=w * .25, height=h*.5, x_center=w * .25, y_center=h * .25)

    logo_250x600 = crop.crop(ImageClip(video_info.logo), y1=175, y2=600 - 175)
    logo_100x240 = resize.resize(logo_250x600, .4)

    background_color = ColorClip(target_resolution, color=HT_COLOR)

    text_style = dict(color='white', stroke_color='grey', stroke_width=0)

    region = Region(0, h * .75 , w*.25, h * .125)  # Presenter name region
    location_clip = create_centered_textclip_with_respect_to_region(region, "GRENOBLE", len("GRENOBLE"), text_style)

    # location_clip = TextClip("GRENOBLE", fontsize=60, **text_style)


    speaker_names = video_info.speaker_name.split(" ")
    text = '\n'.join(speaker_names)
    text_len = max(len(speaker_names[0]), len(speaker_names[1]))


    region = Region(0, h * .875 , w*.25, h * .125)  # Presenter name region
    presenter_name_clip = create_centered_textclip_with_respect_to_region(region, text, text_len, text_style)

    title_text = video_info.title
    title_clip = TextClip(title_text, fontsize=2300 / len(speaker_names), **text_style)

    # TODO center the title and the town name

    presentation_clips = [
        background_color,
        slides_clip.set_position(("right", "center")),
        presentation_clip_540x540.set_position(("left", "center")),
        logo_100x240.set_position((120, 135)),
        location_clip.set_position((100, 1080 * .75 + 40)),
        fade_in_and_cut_to_length(presenter_name_clip, length, 1),
        fade_in_and_cut_to_length(title_clip.set_position((480, 1080 * .75 + 40 + 145)), length, 1),
    ]
    return CompositeVideoClip(presentation_clips, size=target_resolution).subclip(0, length)


def create_centered_textclip_with_respect_to_region(region, text, text_len, text_style):
    presenter_name_clip = TextClip(text, fontsize=region.region_width / text_len, align='center', **text_style)
    center_pos = region.calculate_center(*presenter_name_clip.size)
    presenter_name_clip = presenter_name_clip.set_position(center_pos)
    return presenter_name_clip


def blend_intro_and_main_clip(fade_duration, intro, intro_duration, presentation_composition):
    def fadeout(clip):
        return transitions.crossfadeout(clip,  fade_duration)

    def fadein(clip):
        return transitions.crossfadein(clip,  fade_duration)

    main_part = presentation_composition.set_start(intro_duration)

    return CompositeVideoClip([fadeout(intro), fadeout(fadein(main_part))])


def compose_audio(fade_duration, intro_duration, sound_clip, video_info):
    from moviepy.audio.fx import audio_fadeout, audio_fadein

    def fadeout(clip):
        return audio_fadeout.audio_fadeout(clip,  fade_duration)

    def fadein(clip):
        return audio_fadein.audio_fadein(clip,  fade_duration)

    intro = AudioFileClip(video_info.jingle).subclip(0, intro_duration)
    main_clip = sound_clip.set_start(intro_duration)
    # normalized_audio_clips = [audio_normalize.audio_normalize(normalized) for normalized in [jingle, sound_clip]]

    return CompositeAudioClip([fadeout(intro), fadein(fadeout(main_clip))])


def make_video_clip(presentation_file_path, start, length):
    presentation_clip: VideoClip = VideoFileClip(presentation_file_path) \
        .subclip(start, start + length)
    presentation_clip.set_audio(None)
    return presentation_clip
