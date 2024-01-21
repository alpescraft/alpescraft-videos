from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import ImageClip, TextClip, ColorClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx import crop, resize

from logic_v2.PresentationInfo import PresentationInfo


def intro_clip(video_info: PresentationInfo, intro_duration: int) -> CompositeVideoClip:
    logo_clip = ImageClip(video_info.logo).set_position(('left', 'bottom'))
    logo_clip = resize.resize(logo_clip, newsize=(150, 150))

    image_clip = ImageClip(video_info.background_image)

    background_photo = crop.crop(image_clip, x1=0, y1=0, width=1920, height=900).set_position(('center', 'top'))

    background_color = ColorClip((1920, 1080), color=(110, 20, 86))

    title = (TextClip(video_info.title, fontsize=40, color='white', stroke_width=3)
                  .set_position((.1, 0.85), relative=True))

    presenter_name = (TextClip(video_info.speaker_name, fontsize=35, color='white', stroke_width=2)
                      .set_position((.1, 0.92), relative=True))

    intro = CompositeVideoClip([background_color, background_photo, logo_clip, title, presenter_name])
    return intro.subclip(0, intro_duration)
