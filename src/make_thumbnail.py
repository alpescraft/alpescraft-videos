import os
from PIL import Image, ImageDraw, ImageFont
import yaml
import textwrap
import typer

# Define the supported image extensions
IMAGE_EXTENSIONS = ["png", "jpg", "jpeg", "webp"]

def find_file_with_extension(base_path):
    directory = os.path.dirname(base_path)
    filename = os.path.basename(base_path)
    for ext in IMAGE_EXTENSIONS:
        full_path = os.path.join(directory, f"{filename}.{ext}")
        if os.path.exists(full_path):
            return full_path
    raise FileNotFoundError(f"No file found with base name: {base_path}")

def load_config(config_path):
    with open(config_path, 'r') as stream:
        return yaml.safe_load(stream)

def create_background(background_path):
    background_file = find_file_with_extension(background_path)
    background = Image.open(background_file).convert("RGBA")
    overlay = Image.new('RGBA', background.size, (101, 41, 86, 230))
    return Image.alpha_composite(background, overlay)

def add_logo(background, logo_path, logo_x, logo_y, logo_width):
    logo_file = find_file_with_extension(logo_path)
    logo = Image.open(logo_file).convert("RGBA")
    logo_height = int(logo_width * logo.size[1] / logo.size[0])
    logo = logo.resize((logo_width, logo_height))
    background.paste(logo, (logo_x, logo_y), logo)
    return background, logo

def multiline_text(draw, text, font, max_width, max_height, x, y, fill, align="center"):
    lines = textwrap.wrap(text, width=int(max_width / draw.textbbox((0, 0), "A", font=font)[2]))
    y_text = y
    for line in lines:
        width, height = draw.textbbox((0, 0), line, font=font)[2:4]
        if align == "left":
            draw.text((x, y_text), line, font=font, fill=fill)
        elif align == "center":
            draw.text(((x + max_width - width) / 2, y_text), line, font=font, fill=fill)
        elif align == "right":
            draw.text((x + max_width - width, y_text), line, font=font, fill=fill)
        y_text += height

def add_title(background, config, font_path, title_x, title_y, title_max_width, title_max_height, title_font_size):
    draw = ImageDraw.Draw(background)
    title_font = ImageFont.truetype(font_path, title_font_size)
    title_text = config['title']
    multiline_text(draw, title_text, title_font, title_max_width, title_max_height, title_x, title_y, (255, 255, 255), "left")
    return background

def create_circular_avatar(image_path, size, border_size):
    avatar_file = find_file_with_extension(image_path)
    avatar = Image.open(avatar_file).resize((size, size))
    mask = Image.new("L", avatar.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)

    output = Image.new("RGBA", (size + border_size * 2, size + border_size * 2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(output)
    draw.ellipse((0, 0, size + border_size * 2, size + border_size * 2), fill=(255, 255, 255, 255))
    output.paste(avatar, (border_size, border_size), mask)

    return output

def add_speaker_info(background, config, avatar, font_path, avatar_x, avatar_y, avatar_size, name_y, name_font_size):
    draw = ImageDraw.Draw(background)
    speaker_name_font = ImageFont.truetype(font_path, name_font_size)
    speaker_name_text = config['speaker_name']

     # Add the avatar to the background
    background.paste(avatar, (avatar_x, avatar_y), avatar)

    # Calculate the center x-coordinate for the avatar
    avatar_center_x = avatar_x + avatar_size // 2

    # Measure the width of the speaker name text using textbbox
    text_bbox = draw.textbbox((0, 0), speaker_name_text, font=speaker_name_font)
    name_width = text_bbox[2] - text_bbox[0]

    # Calculate the x-coordinate for the speaker name to be centered under the avatar
    name_x = avatar_center_x - name_width // 2

    # Draw the speaker name on the background
    draw.text((name_x, name_y), speaker_name_text, font=speaker_name_font, fill=(255, 255, 255))

    return background

app = typer.Typer()

@app.command()
def generate_thumbnail(template: str, config: str):
    """
    Generate thumbnail for a talk.

    :param template: Template name (e.g., 'ht')
    :param config: Path to the config file
    """
    try:
        template_dir = os.path.join("template", template)
        config_dir = os.path.dirname(config)

        # Define the file paths
        BACKGROUND_PATH = os.path.join(template_dir, "background")
        LOGO_PATH = os.path.join(template_dir, "logo-no-bg")
        FONT_PATH = os.path.join(template_dir, "Franklin Gothic Demi Cond Regular.ttf")
        SPEAKER_IMAGE_PATH = os.path.join(config_dir, "speaker")
        THUMBNAIL_PATH = os.path.join(config_dir, "thumbnail.jpg")

        config_data = load_config(config)
        background = create_background(BACKGROUND_PATH)

        # Logo parameters
        logo_x, logo_y = 65, 65
        logo_width = 895

        # Title parameters
        title_x, title_y = 110, 500
        title_max_width, title_max_height = 1600, 400
        title_font_size = 86  # You may want to adjust this based on the new dimensions

        # Avatar parameters
        avatar_size = 300
        avatar_border_size = 8
        avatar_x, avatar_y = 1450, 420

        # Speaker name parameters
        name_font_size = 64  # You may want to adjust this based on the new layout
        name_y = avatar_y + avatar_size + 24

        background, logo = add_logo(background, LOGO_PATH, logo_x, logo_y, logo_width)
        background = add_title(background, config_data, FONT_PATH, title_x, title_y, title_max_width, title_max_height, title_font_size)

        # Create the avatar
        avatar = create_circular_avatar(SPEAKER_IMAGE_PATH, avatar_size, avatar_border_size)

        # Add speaker info (including the avatar and speaker name)
        background = add_speaker_info(background, config_data, avatar, FONT_PATH, avatar_x, avatar_y, avatar_size, name_y, name_font_size)

        # Convert the background to RGB and save it
        background = background.convert("RGB")
        background.save(THUMBNAIL_PATH)

        typer.echo(f"Thumbnail generated successfully: {THUMBNAIL_PATH}")
    except FileNotFoundError as e:
        typer.echo(f"Error: {e}")
    except Exception as e:
        typer.echo(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    app()
