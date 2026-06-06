import abc
from abc import ABC
from dataclasses import dataclass, field

from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import VideoClip, ImageClip, ColorClip
from moviepy.video.compositing import transitions
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.fx import resize, crop
from moviepy.video.io.VideoFileClip import VideoFileClip

from logic_v2.PresentationInfo import PresentationInfo, ClipFile
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

    @abc.abstractmethod
    def make_right_size_logo_clip(self, logo_file_path):
        pass


class HTConferenceTheme(ConferenceTheme):
    conference_title = "Grenoble"
    background_color = (121, 2, 87)

    def create_intro_clip(self, video_info: PresentationInfo) -> VideoClip:
        return VideoFileClip(video_info.jingle)

    def make_right_size_logo_clip(self, logo_file_path):
        logo_250x600 = crop.crop(ImageClip(logo_file_path), y1=175, y2=600 - 175)
        return resize.resize(logo_250x600, .4)


ALPESCRAFT_COLOR_DARK = (20, 32, 44)


class AlpesCraftConferenceTheme(ConferenceTheme):

    conference_title = "AlpesCraft"
    background_color = ALPESCRAFT_COLOR_DARK

    def create_intro_clip(self, video_info: PresentationInfo) -> VideoClip:
        ALPESCRAFT_COLOR_LIGHT = (36, 75, 112)
        TARGET_W, TARGET_H = 1920, 1080

        background_image = ImageClip(video_info.background_image)
        bg_w, bg_h = background_image.size
        scale = max(TARGET_W / bg_w, TARGET_H / bg_h)
        background_image = resize.resize(background_image, scale)
        background_image = crop.crop(background_image, width=TARGET_W, height=TARGET_H,
                                     x_center=background_image.size[0] / 2,
                                     y_center=background_image.size[1] / 2)

        logo = ImageClip(video_info.logo)
        logo = resize.resize(logo, newsize=(200, 200))
        logo = logo.set_position(('left', 'bottom'))

        presenter_photo = ImageClip(video_info.speaker_image)
        presenter_photo = resize.resize(presenter_photo, newsize=(400, 400))
        photo_mask = ImageClip("./src/scripts/circular-mask-400x400.png", ismask=True)
        presenter_photo = presenter_photo.set_mask(photo_mask)

        black_ring = ColorClip((430, 430), color=(0, 0, 0))
        black_ring = black_ring.set_mask(ImageClip("./src/scripts/circular-mask-430x430.png", ismask=True))

        white_ring = ColorClip((420, 420), color=(255, 255, 255))
        white_ring = white_ring.set_mask(ImageClip("./src/scripts/circular-mask-420x420.png", ismask=True))

        presenter_photo_with_frame = CompositeVideoClip([
            black_ring.set_position(('center', 'center')),
            white_ring.set_position(('center', 'center')),
            presenter_photo.set_position(('center', 'center')),
        ], size=(430, 430))
        presenter_photo_with_frame = presenter_photo_with_frame.set_position(('center', 'center'))

        blue_bar = ColorClip((TARGET_W, 100), color=ALPESCRAFT_COLOR_LIGHT)
        blue_bar = blue_bar.set_position(('center', 'bottom'))

        text_style = dict(color='white', stroke_color='grey', stroke_width=1)
        logo_width = 100
        region = Region(logo_width, TARGET_H - 100, TARGET_W - logo_width, 100)
        title = create_centered_textclip_with_respect_to_region(region, video_info.title, text_style)

        intro_clip = CompositeVideoClip([
            background_image,
            blue_bar,
            logo,
            presenter_photo_with_frame,
            title,
        ], size=(TARGET_W, TARGET_H))

        return intro_clip.set_duration(5)

    def make_right_size_logo_clip(self, logo_file_path):
        logo = ImageClip(logo_file_path)
        return resize.resize(logo, newsize=(120, 120))


# ---------------------------------------------------------------------------
# MainPartBuilder
# ---------------------------------------------------------------------------

class MainPartBuilder(ABC):
    @abc.abstractmethod
    def build(self, video_info: PresentationInfo) -> tuple[VideoClip, VideoClip]:
        """Return (video_clip, audio_clip)."""


@dataclass
class CompositeMainPartBuilder(MainPartBuilder):
    theme: ConferenceTheme

    def build(self, video_info: PresentationInfo) -> tuple[VideoClip, VideoClip]:
        video_collage_info = VideoCollageInfo.from_video_info(video_info)
        start, length = video_collage_info.get_start_length()
        presentation_file_path = video_collage_info.presentation_file_path
        target_resolution = video_collage_info.target_resolution

        slides_clip = create_slides_clip(length, presentation_file_path, start, video_collage_info.slides_file)
        presentation_clip = create_presentation_clip(length, presentation_file_path, start)
        video = compose_main_video(length, presentation_clip, slides_clip, target_resolution, video_info, self.theme)
        audio = create_sound_clip(length, presentation_file_path, start, video_collage_info.sound_file)
        return video, audio


@dataclass
class SingleClipMainPartBuilder(MainPartBuilder):
    """OBS-merged clip: one video file carries both video and audio."""
    video_file_path: str
    audio_offset: float = 0.0

    def build(self, video_info: PresentationInfo) -> tuple[VideoClip, VideoClip]:
        video_collage_info = VideoCollageInfo.from_video_info(video_info)
        start, length = video_collage_info.get_start_length()
        sound_file = ClipFile(file_name=self.video_file_path, extra_offset=self.audio_offset)
        video = VideoFileClip(self.video_file_path).subclip(start, start + length)
        audio = create_sound_clip(length, self.video_file_path, start, sound_file)
        return video, audio


# ---------------------------------------------------------------------------
# IntroPhase
# ---------------------------------------------------------------------------

class IntroPhase(ABC):
    @abc.abstractmethod
    def apply(self, main_video: VideoClip, main_audio, video_info: PresentationInfo) -> tuple[VideoClip, object]:
        """Return (final_video, final_audio)."""


@dataclass
class WithIntro(IntroPhase):
    theme: ConferenceTheme
    fade_duration: float = 1.6

    def apply(self, main_video: VideoClip, main_audio, video_info: PresentationInfo) -> tuple[VideoClip, object]:
        intro = self.theme.create_intro_clip(video_info)
        final_audio = _compose_audio(self.fade_duration, intro.duration, main_audio, video_info)
        final_video = _blend_intro_and_main_clip(self.fade_duration, intro, intro.duration, main_video)
        return final_video, final_audio


class NoIntro(IntroPhase):
    def apply(self, main_video: VideoClip, main_audio, video_info: PresentationInfo) -> tuple[VideoClip, object]:
        return main_video, main_audio


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

@dataclass
class GenerationPipeline:
    main_part: MainPartBuilder
    intro: IntroPhase


def build_final_clip(video_info: PresentationInfo, pipeline: GenerationPipeline) -> VideoClip:
    main_video, main_audio = pipeline.main_part.build(video_info)
    final_video, final_audio = pipeline.intro.apply(main_video, main_audio, video_info)
    return final_video.set_audio(final_audio)


# ---------------------------------------------------------------------------
# Clip helpers
# ---------------------------------------------------------------------------

def create_presentation_clip(length, presentation_file_path, start):
    h = int(1080 * .75)
    w = int(1920 * .75)
    base_clip = VideoFileClip(presentation_file_path, target_resolution=(h, w))
    presentation_clip: VideoClip = crop.crop(base_clip, width=480, height=810, x_center=w / 2, y_center=h / 2) \
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
                       theme: ConferenceTheme):
    w, h = target_resolution
    presentation_clip_480x540 = presentation_clip

    left_quarter_width = w * .25
    upper_band_height = h * .125

    logo_region = Region(0, 0, left_quarter_width, upper_band_height)
    right_size_clip = theme.make_right_size_logo_clip(video_info.logo)
    logo_clip = right_size_clip.set_position(logo_region.calculate_center(*right_size_clip.size))

    background_color = ColorClip(target_resolution, color=theme.background_color)

    text_style = dict(color='white', stroke_color='grey', stroke_width=0)

    region = Region(left_quarter_width, 0, w * .75, upper_band_height)
    location_clip = create_centered_textclip_with_respect_to_region(region, theme.conference_title, text_style)

    region = Region(0, h * .875, left_quarter_width, upper_band_height)
    presenter_name_clip = create_centered_textclip_with_respect_to_region_multiline(region, video_info.speaker_name, text_style)

    title_text = video_info.title
    region = Region(left_quarter_width, h * .875, w * .75, upper_band_height)
    title_clip = create_centered_textclip_with_respect_to_region(region, title_text, text_style)

    presentation_clips = [
        background_color,
        logo_clip,
        slides_clip.set_position(("right", "center")),
        presentation_clip_480x540.set_position(("left", "center")),
        location_clip,
        fade_in_and_cut_to_length(presenter_name_clip, length, 1),
        fade_in_and_cut_to_length(title_clip, length, 1),
    ]
    return CompositeVideoClip(presentation_clips, size=target_resolution).subclip(0, length)


def _blend_intro_and_main_clip(fade_duration, intro, intro_duration, presentation_composition):
    def fadeout(clip):
        return transitions.crossfadeout(clip, fade_duration)

    def fadein(clip):
        return transitions.crossfadein(clip, fade_duration)

    first_part = concatenate_videoclips([fadeout(intro), fadein(presentation_composition)], method="compose") \
        .set_duration(intro_duration + fade_duration)
    video_parts = [first_part, presentation_composition.subclip(fade_duration)]
    return concatenate_videoclips(video_parts)


def _compose_audio(fade_duration, intro_duration, sound_clip, video_info):
    from moviepy.audio.fx import audio_fadeout, audio_fadein

    def fadeout(clip):
        return audio_fadeout.audio_fadeout(clip, fade_duration)

    def fadein(clip):
        return audio_fadein.audio_fadein(clip, fade_duration)

    intro = AudioFileClip(video_info.jingle).subclip(0, intro_duration)
    main_clip = sound_clip.set_start(intro_duration)
    return CompositeAudioClip([fadeout(intro), fadein(fadeout(main_clip))])
