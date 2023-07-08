from moviepy.editor import VideoFileClip, TextClip, ImageClip, CompositeVideoClip


def test_intro() -> None:
    presentation_title = "eXtreme Programming : LA méthode Agile ? \n Pascal Le Merrer"
    duration = 5
    image_base_dir = "/Users/johan/Documents/alpescraft videos 2023/Logo/"
    image_filename = image_base_dir + "bandeau.jpg"
    logo_file_name = image_base_dir + "02-AlpesCraft_Couleurs-L.png"
    image_clip = ImageClip(image_filename).set_duration(duration)
    text_clip = TextClip(presentation_title, fontsize=70, color='white')

    logo_clip = ImageClip(logo_file_name).subclip(0, 5).resize(.4)
    logo_clip = logo_clip.set_duration(duration).set_position([round((image_clip.w - logo_clip.w) / 2), (image_clip.h - logo_clip.h) / 3.5])




    center_width = round((image_clip.w - text_clip.w) / 2)
    title_clip = (text_clip
                  .set_position([center_width, round((image_clip.h - text_clip.h) / 1.5)])
                  .set_duration(duration)
                  )
    result = CompositeVideoClip([image_clip, title_clip, logo_clip])  # Overlay text on video

    result.write_videofile("./test_intro.mpg", fps=25, codec='libx264')
