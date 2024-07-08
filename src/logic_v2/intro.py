from moviepy.video.VideoClip import ImageClip, TextClip, ColorClip, VideoClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx import crop, resize
from moviepy.video.io.VideoFileClip import VideoFileClip

from logic_v2.PresentationInfo import PresentationInfo
from logic_v2.region import Region, create_centered_textclip_with_respect_to_region


def intro_clip(video_info: PresentationInfo, intro_duration: int) -> CompositeVideoClip:
    HT_COLOR = (121, 2, 87)

    logo_clip = ImageClip(video_info.logo).set_position(('left', 'bottom'))
    logo_clip = resize.resize(logo_clip, newsize=(175, 175))

    image_clip = ImageClip(video_info.background_image)

    background_photo = crop.crop(image_clip, x1=0, y1=0, width=1920, height=900).set_position(('center', 'top'))

    background_color = ColorClip((1920, 1080), color=HT_COLOR)

    title = (TextClip(video_info.title, fontsize=50, color='white', stroke_width=3)
                  .set_position((.1, 0.86), relative=True))

    presenter_name = (TextClip(video_info.speaker_name, fontsize=50, color='white', stroke_width=2)
                      .set_position((.1, 0.93), relative=True))

    intro = CompositeVideoClip([background_color, background_photo, logo_clip, title, presenter_name])
    return intro.subclip(0, intro_duration)


