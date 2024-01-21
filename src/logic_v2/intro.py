from moviepy.video.VideoClip import ImageClip, TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx import crop, resize

from logic_v2.VideoInfo import PresentationInfo


def intro_clip(video_info: PresentationInfo, intro_duration: int, resource_dir: str) -> CompositeVideoClip:
    logo = f"{resource_dir}/Logo/03-AlpesCraft_Couleurs-M.png"
    logo_clip = ImageClip(logo).set_position(('center', 0.2), relative=True)

    background_image = f"{resource_dir}/Logo/bandeau.jpg"
    image_clip = ImageClip(background_image)
    cropped_image = crop.crop(image_clip, x1=0, y1=0, width=1920)
    resized = resize.resize(cropped_image, newsize=(1920, 1080))
    title = (TextClip(video_info.title, fontsize=52, color='white', stroke_width=3)
                  .set_position(('center', 0.5), relative=True))
    presenter_name = (TextClip(video_info.presenter, fontsize=45, color='white', stroke_width=2)
                      .set_position(('center', 0.60), relative=True))

    intro = CompositeVideoClip([resized, logo_clip, title, presenter_name])


    return intro.set_duration(intro_duration)
