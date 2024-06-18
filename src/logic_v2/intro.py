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


def intro_ht(video_info: PresentationInfo) -> VideoClip:
    return VideoFileClip(video_info.jingle)


def create_intro_clip(video_info: PresentationInfo):
    # Load the background image
    ALPESCRAFT_COLOR_DARK = (20, 32, 44)
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
        ImageClip("./src/scripts/circular-mask-430x430.png").set_position(('center', 'center')) ,
        ImageClip("./src/scripts/circular-mask-420x420.png").set_position(('center', 'center')),
        presenter_photo.set_position(('center', 'center'))
    ])
    presenter_photo_with_frame = presenter_photo_with_frame.set_position(('center', 'center'))
    # Create the session title text
    # title = TextClip(video_info.title, fontsize=50, color='white')
    text_style = dict(color='white', stroke_color='grey', stroke_width=1)
    logo_width = 100
    region = Region(logo_width, background_image.size[1] - 100, 1920-logo_width, 100)
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
