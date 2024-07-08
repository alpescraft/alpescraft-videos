import abc
import typing
from abc import ABC
from dataclasses import dataclass

from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import VideoClip, ImageClip, ColorClip
from moviepy.video.compositing import transitions
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.fx import resize, crop
from moviepy.video.io.VideoFileClip import VideoFileClip

from logic_v2.PresentationInfo import PresentationInfo
from logic_v2.VideoCollageInfo import VideoCollageInfo
from logic_v2.region import Region, create_centered_textclip_with_respect_to_region_multiline, \
    create_centered_textclip_with_respect_to_region
from logic_v2.start_time import get_relative_start_time


class ConferenceTheme(ABC):

    conference_title: str
    background_color: tuple[int, int, int]

    @abc.abstractmethod
    def create_intro_clip(self, video_info: PresentationInfo) -> VideoClip:
        pass


class HTConferenceTheme(ConferenceTheme):
    conference_title = "Human Talks"
    background_color = (121, 2, 87)

    def create_intro_clip(self, video_info: PresentationInfo) -> VideoClip:
        return VideoFileClip(video_info.jingle)


ALPESCRAFT_COLOR_DARK = (20, 32, 44)


class AlpesCraftConferenceTheme(ConferenceTheme):

    conference_title = "AlpesCraft"
    background_color = ALPESCRAFT_COLOR_DARK
    def create_intro_clip(self, video_info: PresentationInfo) -> VideoClip:
        # Load the background image
        ALPESCRAFT_COLOR_LIGHT = (36, 75, 112)

        background_image = ImageClip(video_info.background_image)

        # Load and resize the logo
        logo = ImageClip(video_info.logo)
        logo = resize.resize(logo, newsize=(200, 200))

        # Load the presenter photo
        presenter_photo = ImageClip(video_info.speaker_image)
        presenter_photo = resize.resize(presenter_photo, newsize=(400, 400))
        # Create a mask for the presenter photo to make it round
        mask = ImageClip("./src/scripts/circular-mask-400x400.png", ismask=True)
        presenter_photo: ImageClip = presenter_photo.set_mask(mask)

        # Create a blue-colored bar
        blue_bar = ColorClip((1920, 100), color=ALPESCRAFT_COLOR_LIGHT)
        blue_bar = blue_bar.set_position(('center', 'bottom'))

        # Position the elements on the screen
        logo = logo.set_position(('left', 'bottom'))

        presenter_photo_with_frame = CompositeVideoClip([
            ImageClip("./src/scripts/circular-mask-430x430.png").set_position(('center', 'center')),
            ImageClip("./src/scripts/circular-mask-420x420.png").set_position(('center', 'center')),
            presenter_photo.set_position(('center', 'center'))
        ])
        presenter_photo_with_frame = presenter_photo_with_frame.set_position(('center', 'center'))
        # Create the session title text
        # title = TextClip(video_info.title, fontsize=50, color='white')
        text_style = dict(color='white', stroke_color='grey', stroke_width=1)
        logo_width = 100
        region = Region(logo_width, background_image.size[1] - 100, 1920 - logo_width, 100)
        title = create_centered_textclip_with_respect_to_region(region, video_info.title, text_style)

        # Create a composite video clip
        intro_clip = CompositeVideoClip([
            background_image,
            blue_bar,
            logo,
            presenter_photo_with_frame,
            title
        ])

        return intro_clip.set_duration(5)

@dataclass
class GenerationStrategy:
    task: typing.Literal["video", "video-nointro", "thumbnail"]
    conference_theme: ConferenceTheme

    def create_intro_clip(self, video_info):
        return self.conference_theme.create_intro_clip(video_info)


def collate_main_part_without_intro(video_info: PresentationInfo,  generation_strategy: GenerationStrategy):
    video_collage_info = VideoCollageInfo.from_video_info(video_info)
    start, length = video_collage_info.get_start_length()

    presentation_file_path = video_collage_info.presentation_file_path
    target_resolution = video_collage_info.target_resolution

    # main part
    slides_clip = create_slides_clip(length, presentation_file_path, start, video_collage_info.slides_file)
    presentation_clip = create_presentation_clip(length, presentation_file_path, start)
    presentation_composition = compose_main_video(length, presentation_clip, slides_clip, target_resolution, video_info,
                                                  generation_strategy)
    sound_clip = create_sound_clip(length, presentation_file_path, start, video_collage_info.sound_file)
    return presentation_composition.set_audio(sound_clip)


def collate_main_part(video_info: PresentationInfo, generation_strategy: GenerationStrategy):
    video_collage_info = VideoCollageInfo.from_video_info(video_info)
    start, length = video_collage_info.get_start_length()

    presentation_file_path = video_collage_info.presentation_file_path
    target_resolution = video_collage_info.target_resolution

    # main part
    slides_clip = create_slides_clip(length, presentation_file_path, start, video_collage_info.slides_file)
    presentation_clip = create_presentation_clip(length, presentation_file_path, start)
    presentation_composition = compose_main_video(length, presentation_clip, slides_clip, target_resolution, video_info, generation_strategy)
    sound_clip = create_sound_clip(length, presentation_file_path, start, video_collage_info.sound_file)

    fade_duration = 1.1
    intro = generation_strategy.create_intro_clip(video_info)

    # blend intro and main part
    final_audio = compose_audio(fade_duration, intro.duration, sound_clip, video_info)
    final_clip = blend_intro_and_main_clip(fade_duration, intro, intro.duration, presentation_composition)

    return final_clip.set_audio(final_audio)


def create_presentation_clip(length, presentation_file_path, start):
    presentation_clip: VideoClip = VideoFileClip(presentation_file_path, target_resolution=(960, 540)) \
        .subclip(start, start + length)
    presentation_clip.set_audio(None)
    return presentation_clip


def create_slides_clip(length, presentation_file_path, start, track_file):
    slides_file_path = track_file.file_name
    slides_relative_start = (get_relative_start_time(presentation_file_path, slides_file_path, start)
                             + track_file.extra_offset)
    resize_factor = .75
    slides_resolution = (int(1080 * resize_factor), int(1920 * resize_factor))
    presentation_clip: VideoClip = VideoFileClip(slides_file_path, target_resolution=slides_resolution) \
        .subclip(slides_relative_start, slides_relative_start + length)
    presentation_clip.set_audio(None)
    return presentation_clip


def create_sound_clip(length, presentation_file_path, start, track_file):
    sound_file_path = track_file.file_name
    sound_relative_start = (get_relative_start_time(presentation_file_path, sound_file_path, start)
                            + track_file.extra_offset)
    return AudioFileClip(sound_file_path).subclip(sound_relative_start, sound_relative_start + length)


def fade_in_and_cut_to_length(clip, length, fade_duration):
    seconds_after_main_part = 4
    start_and_duration_adjusted = clip.set_start(seconds_after_main_part).set_duration(length - seconds_after_main_part)
    return transitions.crossfadein(start_and_duration_adjusted, fade_duration)


def compose_main_video(length, presentation_clip, slides_clip, target_resolution, video_info: PresentationInfo,
                       strategy: GenerationStrategy):

    w, h = target_resolution
    presentation_clip_480x540 = crop.crop(presentation_clip, width=480, height=810, x_center=540/2, y_center=480)

    logo_200x200 = ImageClip(video_info.logo)
    # logo_250x600 = crop.crop(ImageClip(video_info.logo), y1=175, y2=600 - 175)
    logo_100x240 = resize.resize(logo_200x200, .65)

    background_color = ColorClip(target_resolution, color=strategy.conference_theme.background_color)

    text_style = dict(color='white', stroke_color='grey', stroke_width=0)

    region = Region(w * .25, 0, w * .75, h * .125)  # Presenter name region
    location_clip = create_centered_textclip_with_respect_to_region(region, strategy.conference_theme.conference_title, text_style)

    region = Region(0, h * .875, w * .25, h * .125)  # Presenter name region
    presenter_name_clip = create_centered_textclip_with_respect_to_region_multiline(region, video_info.speaker_name, text_style)

    title_text = video_info.title
    region = Region(w * .25, h * .875, w * .75, h * .125)  # Presenter name region
    title_clip = create_centered_textclip_with_respect_to_region(region, title_text, text_style)

    # TODO center the title and the town name

    presentation_clips = [
        background_color,
        logo_100x240.set_position((175, 0)), #  region-width / 2 - size/2 = 175
        slides_clip.set_position(("right", "center")),
        presentation_clip_480x540.set_position(("left", "center")),
        location_clip,
        fade_in_and_cut_to_length(presenter_name_clip, length, 1),
        fade_in_and_cut_to_length(title_clip, length, 1),
    ]
    return CompositeVideoClip(presentation_clips, size=target_resolution).subclip(0, length)


def blend_intro_and_main_clip(fade_duration, intro, intro_duration, presentation_composition):
    def fadeout(clip):
        return transitions.crossfadeout(clip,  fade_duration)

    def fadein(clip):
        return transitions.crossfadein(clip,  fade_duration)

    # speed trick: use compose for fade and avoid it for speed for the rest of the video
    first_part = concatenate_videoclips([fadeout(intro), fadein(presentation_composition)], method="compose") \
        .set_duration(intro_duration)
    video_parts = [first_part, presentation_composition.set_start(first_part.end)]
    full_video: VideoClip = concatenate_videoclips(video_parts)

    return full_video



def compose_audio(fade_duration, intro_duration, sound_clip, video_info):
    from moviepy.audio.fx import audio_fadeout, audio_fadein

    def fadeout(clip):
        return audio_fadeout.audio_fadeout(clip,  fade_duration)

    def fadein(clip):
        return audio_fadein.audio_fadein(clip,  fade_duration)

    intro = AudioFileClip(video_info.jingle).subclip(0, intro_duration)
    main_clip = sound_clip.set_start(intro_duration)

    return CompositeAudioClip([fadeout(intro), fadein(fadeout(main_clip))])
