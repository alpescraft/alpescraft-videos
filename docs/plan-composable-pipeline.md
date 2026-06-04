# Plan: Composable generation pipeline

## Context

`produce_video_v2.py` and `collate_video.py` have two problems to fix before adding OBS-merged-clip support:

1. **Double if on `task`**: `get_generation_strategy()` maps CLI args to a task string, then `do_it_all()` branches on it again. Adding a new task requires touching both.
2. **Duplication**: `collate_main_part` and `collate_main_part_without_intro` share ~8 lines of identical setup code.

## Target design

Replace `GenerationStrategy(task, conference_theme)` with a `GenerationPipeline` of two phases.
Output decisions (video, thumbnail) belong to the caller, not the pipeline.

```python
@dataclass
class GenerationPipeline:
    main_part:  MainPartBuilder   # builds (VideoClip, AudioClip)
    intro:      IntroPhase        # prepends intro + blends, or identity
```

### Phase: MainPartBuilder

Produces `(VideoClip, AudioClip)` from a `PresentationInfo`.

- `CompositeMainPartBuilder`: current behaviour — loads speaker clip + slides clip, crops and composes them side-by-side. Resolves audio from `VideoCollageInfo.sound_file` (a `ClipFile` with `extra_offset`).
- `SingleClipMainPartBuilder` *(new — OBS)*: loads one video file. Sets `sound_file = ClipFile(file_name=video_file, extra_offset=audio_offset)` so the embedded audio is handled by the existing `create_sound_clip` path unchanged. `audio_offset` (default 0) handles the 1-2 s sync correction.

### Phase: IntroPhase

Combines intro creation and blending into one coupled unit, preventing illegal combinations.

```python
class IntroPhase(ABC):
    def apply(self, main_video, main_audio, video_info) -> tuple[VideoClip, AudioClip]: ...

class WithIntro(IntroPhase):    # creates intro clip + crossfades into main
    theme: ConferenceTheme
    fade_duration: float = 1.6

class NoIntro(IntroPhase):      # identity — returns main unchanged
    pass
```

`WithIntro` owns the logic currently split across `blend_intro_and_main_clip` and `compose_audio`.

### build_final_clip — no output concerns

```python
def build_final_clip(video_info, pipeline: GenerationPipeline) -> VideoClip:
    main_video, main_audio = pipeline.main_part.build(video_info)
    final_video, final_audio = pipeline.intro.apply(main_video, main_audio, video_info)
    return final_video.set_audio(final_audio)
```

No conditionals. The caller decides what to write:

```python
"video"         → build_final_clip + write_video + write_thumbnail(t=3)
"video-nointro" → build_final_clip + write_video + write_thumbnail(t=10)
"thumbnail"     → build_final_clip + write_thumbnail(t=3)
"obs-video"     → build_final_clip + write_video + write_thumbnail(t=3)
```

"Thumbnail only" requires no special flag — just don't call `write_video`.

## Migration steps

1. Extract `_build_main_composition(video_info, strategy) -> tuple[VideoClip, AudioClip]` from the shared body of the two collate functions. Make both call it. Tests still pass.
2. Define `MainPartBuilder` ABC and `IntroPhase` ABC.
3. Implement `CompositeMainPartBuilder` wrapping `_build_main_composition`.
4. Implement `WithIntro` (absorbing `blend_intro_and_main_clip` + `compose_audio`) and `NoIntro`.
5. Implement `build_final_clip`.
6. Replace `do_it_all` with per-preset call sites that invoke `build_final_clip` then write what they need.
7. Replace `GenerationStrategy` construction in `get_generation_strategy()` with preset factories returning a `GenerationPipeline`.
8. Delete `collate_main_part`, `collate_main_part_without_intro`, `_build_main_composition`, `GenerationStrategy`, `do_it_all`.
9. Add `SingleClipMainPartBuilder` for OBS support.

## Audio offset (OBS sync correction)

The existing `ClipFile.extra_offset` field already models this. `SingleClipMainPartBuilder` takes an optional `audio_offset: float = 0` and sets:

```python
sound_file = ClipFile(file_name=video_file_path, extra_offset=audio_offset)
```

`create_sound_clip` handles it unchanged. No new infrastructure needed.
