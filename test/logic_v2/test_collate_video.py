"""
Characterization tests for collate_video.py.

These tests pin the observable contract of build_final_clip with
CompositeMainPartBuilder + WithIntro/NoIntro so the composable-pipeline
refactor (docs/plan-composable-pipeline.md) cannot silently change behaviour.

All I/O (VideoFileClip, AudioFileClip, VideoCollageInfo) is mocked so
no real media files are needed and tests run in milliseconds.
"""
import pytest
from unittest.mock import MagicMock, patch

from logic_v2.PresentationInfo import PresentationInfo, ClipFile, ReferenceFile
from logic_v2.VideoCollageInfo import VideoCollageInfo
from logic_v2.collate_video import (
    build_final_clip,
    GenerationPipeline,
    CompositeMainPartBuilder,
    WithIntro,
    NoIntro,
    AlpesCraftConferenceTheme,
)
from logic.ClipSection import ClipSection
from logic.MinutesAndSeconds import MinutesSeconds


CLIP_DURATION = 60.0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_fake_video_clip(duration=CLIP_DURATION):
    clip = MagicMock()
    clip.duration = duration
    clip.size = (1440, 810)
    clip.audio = None
    clip.set_audio = lambda a: _with_audio(clip, a)
    clip.set_position = lambda *a, **kw: clip
    clip.set_start = lambda *a, **kw: clip
    clip.set_duration = lambda *a, **kw: clip
    clip.subclip = lambda *a, **kw: clip
    clip.set_mask = lambda *a, **kw: clip
    return clip


def _with_audio(clip, audio):
    out = MagicMock()
    out.duration = clip.duration
    out.audio = audio
    return out


def make_fake_audio_clip(duration=CLIP_DURATION):
    clip = MagicMock()
    clip.duration = duration
    clip.set_start = lambda *a, **kw: clip
    clip.subclip = lambda *a, **kw: clip
    return clip


def make_fake_collage_info():
    return VideoCollageInfo(
        presentation_file_path="speaker.mp4",
        slides_file=ClipFile(file_name="slides.mp4", extra_offset=0.0),
        sound_file=ClipFile(file_name="sound.m4a", extra_offset=0.0),
        presentation_start_stop_seconds=(0.0, CLIP_DURATION),
        target_resolution=(1920, 1080),
    )


def make_fake_presentation_info():
    part = ClipSection(
        start=MinutesSeconds.from_total_seconds(0),
        stop=MinutesSeconds.from_total_seconds(CLIP_DURATION),
    )
    return PresentationInfo(
        title="Test Talk",
        jingle="jingle.m4a",
        logo="logo.png",
        speaker_name="Jane Doe",
        speaker=ReferenceFile(file_name="speaker.mp4", parts=[part]),
        speaker_image="speaker.jpg",
        sound=ClipFile(file_name="sound.m4a"),
        slides=ClipFile(file_name="slides.mp4"),
        background_image="background.jpg",
    )


def make_theme():
    theme = MagicMock(spec=AlpesCraftConferenceTheme)
    theme.background_color = (20, 32, 44)
    theme.conference_title = "AlpesCraft"
    theme.make_right_size_logo_clip.return_value = make_fake_video_clip(duration=CLIP_DURATION)
    intro_clip = make_fake_video_clip(duration=5.0)
    intro_clip.duration = 5.0
    theme.create_intro_clip.return_value = intro_clip
    return theme


def make_pipeline_with_intro(theme=None):
    theme = theme or make_theme()
    return GenerationPipeline(
        main_part=CompositeMainPartBuilder(theme=theme),
        intro=WithIntro(theme=theme),
    )


def make_pipeline_without_intro(theme=None):
    theme = theme or make_theme()
    return GenerationPipeline(
        main_part=CompositeMainPartBuilder(theme=theme),
        intro=NoIntro(),
    )


# ---------------------------------------------------------------------------
# Patches applied to every test in this module
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def patch_io(monkeypatch):
    """Replace all moviepy I/O with fakes."""
    fake_video = make_fake_video_clip()
    fake_audio = make_fake_audio_clip()

    with (
        patch("logic_v2.collate_video.VideoFileClip", return_value=fake_video),
        patch("logic_v2.collate_video.AudioFileClip", return_value=fake_audio),
        patch("logic_v2.collate_video.ImageClip", return_value=make_fake_video_clip()),
        patch("logic_v2.collate_video.ColorClip", return_value=make_fake_video_clip()),
        patch("logic_v2.collate_video.CompositeVideoClip", return_value=fake_video),
        patch("logic_v2.collate_video.CompositeAudioClip", return_value=fake_audio),
        patch("logic_v2.collate_video.concatenate_videoclips", return_value=fake_video),
        patch("logic_v2.collate_video.transitions.crossfadein", return_value=fake_video),
        patch("logic_v2.collate_video.transitions.crossfadeout", return_value=fake_video),
        patch("logic_v2.collate_video.resize.resize", side_effect=lambda clip, *a, **kw: clip),
        patch("logic_v2.collate_video.crop.crop", side_effect=lambda clip, *a, **kw: clip),
        patch("logic_v2.collate_video.create_centered_textclip_with_respect_to_region",
              return_value=make_fake_video_clip()),
        patch("logic_v2.collate_video.create_centered_textclip_with_respect_to_region_multiline",
              return_value=make_fake_video_clip()),
        patch("logic_v2.VideoCollageInfo.VideoCollageInfo.from_video_info", return_value=make_fake_collage_info()),
    ):
        yield


# ---------------------------------------------------------------------------
# NoIntro pipeline
# ---------------------------------------------------------------------------

class TestBuildFinalClipNoIntro:

    def test_returns_clip_with_audio(self):
        result = build_final_clip(make_fake_presentation_info(), make_pipeline_without_intro())
        assert result.audio is not None, "clip must carry an audio track"

    def test_does_not_call_create_intro_clip(self):
        theme = make_theme()
        build_final_clip(make_fake_presentation_info(), make_pipeline_without_intro(theme))
        theme.create_intro_clip.assert_not_called()


# ---------------------------------------------------------------------------
# WithIntro pipeline
# ---------------------------------------------------------------------------

class TestBuildFinalClipWithIntro:

    def test_returns_clip_with_audio(self):
        result = build_final_clip(make_fake_presentation_info(), make_pipeline_with_intro())
        assert result.audio is not None, "clip must carry an audio track"

    def test_calls_create_intro_clip_exactly_once(self):
        theme = make_theme()
        build_final_clip(make_fake_presentation_info(), make_pipeline_with_intro(theme))
        theme.create_intro_clip.assert_called_once()
