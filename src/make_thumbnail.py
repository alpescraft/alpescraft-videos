import os
from PIL import Image, ImageDraw, ImageFont
import yaml
import requests
from io import BytesIO
import textwrap

# Define the file paths
BACKGROUND_PATH = "template/ht/background.png"
LOGO_PATH = "template/ht/logo-no-bg.png"
CONFIG_PATH = "template/ht/talk1/config.yml"
SPEAKER_IMAGE_PATH = "template/ht/talk1/speaker.webp"
THUMBNAIL_PATH = "template/ht/talk1/thumbnail.jpg"

# Define the supported image extensions
IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "webp"]

def multiline_text(draw, text, font, max_width, max_height, x, y, fill, align="center"):
    lines = textwrap.wrap(text, width=int(max_width / draw.textbbox((0, 0), "A", font=font)[2]))
    line_height = draw.textbbox((0, 0), "A", font=font)[3] - draw.textbbox((0, 0), "A", font=font)[1]
    y_text = y
    for line in lines:
        width = draw.textbbox((0, 0), line, font=font)[2] - draw.textbbox((0, 0), line, font=font)[0]
        height = draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1]
        if align == "left":
            draw.text((x, y_text), line, font=font, fill=fill)
        elif align == "center":
            draw.text(((x + max_width - width) / 2, y_text), line, font=font, fill=fill)
        elif align == "right":
            draw.text((x + max_width - width, y_text), line, font=font, fill=fill)
        y_text += height

# Load the background image
background = Image.open(BACKGROUND_PATH).convert("RGBA")

# Create a semi-transparent overlay
overlay = Image.new('RGBA', background.size, (101, 41, 86, 230))

# Paste the overlay on the background
background = Image.alpha_composite(background, overlay)

# Load the logo image and resize it
logo = Image.open(LOGO_PATH).convert("RGBA").resize((895, int(895 * Image.open(LOGO_PATH).size[1] / Image.open(LOGO_PATH).size[0])))

# Paste the logo on the background
background.paste(logo, (64, 64), logo)

# Load the talk configuration
with open(CONFIG_PATH, 'r') as stream:
    config = yaml.safe_load(stream)

# Load the speaker image and resize it
speaker_image_path = SPEAKER_IMAGE_PATH
if not os.path.splitext(speaker_image_path)[1][1:] in IMAGE_EXTENSIONS:
    raise ValueError(f"Unsupported image extension: {os.path.splitext(speaker_image_path)[1]}")
speaker_image = Image.open(speaker_image_path).resize((250, 250))

# Create a circular mask for the speaker image
speaker_mask = Image.new("L", speaker_image.size, 0)
draw = ImageDraw.Draw(speaker_mask)
mask_radius = min(speaker_image.size) // 2
mask_center = (speaker_image.size[0] // 2, speaker_image.size[1] // 2)
draw.ellipse((mask_center[0] - mask_radius, mask_center[1] - mask_radius, mask_center[0] + mask_radius, mask_center[1] + mask_radius), fill=255)

# Create a new image that is 15px larger than the speaker image size
circle_size = (speaker_image.size[0] + 30, speaker_image.size[1] + 30)
circle = Image.new("RGBA", circle_size, (0, 0, 0, 0))
draw_circle = ImageDraw.Draw(circle)

# Draw a white circle of 15px larger than the mask
circle_radius = min(circle_size) // 2
draw_circle.ellipse((circle_size[0] // 2 - circle_radius, circle_size[1] // 2 - circle_radius, circle_size[0] // 2 + circle_radius, circle_size[1] // 2 + circle_radius), fill=(255, 255, 255, 255))

# Apply the circular mask to the speaker image
speaker_image = Image.composite(speaker_image, Image.new("RGBA", speaker_image.size, (0, 0, 0, 0)), speaker_mask)

# Create a font for the title and speaker name
title_font = ImageFont.truetype("DejaVuSansMono.ttf", 64)
speaker_name_font = ImageFont.truetype("DejaVuSansMono.ttf", 36)

# Draw the title on the background
draw = ImageDraw.Draw(background)
title_text = config['title']
title_x = 64
title_y = 192 + logo.height
title_max_width = 1400
title_max_height = 1000
title_fill = (255, 255, 255)
title_align = "left"
multiline_text(draw, title_text, title_font, title_max_width, title_max_height, title_x, title_y, title_fill, title_align)

# Draw the speaker name on the background
speaker_name_text = config['speaker_name']
speaker_image_x = 1400 + 113
speaker_image_y = 192 + logo.height
speaker_name_width = draw.textbbox((0, 0), speaker_name_text, font=speaker_name_font)[2] - draw.textbbox((0, 0), speaker_name_text, font=speaker_name_font)[0]
speaker_name_height = draw.textbbox((0, 0), speaker_name_text, font=speaker_name_font)[3] - draw.textbbox((0, 0), speaker_name_text, font=speaker_name_font)[1]
speaker_name_max_width = 476
speaker_name_x = background.width - speaker_name_width - 48 - (speaker_name_max_width - speaker_name_width) // 2
speaker_name_y = speaker_image_y + 64 + speaker_image.height
speaker_name_fill = (255, 255, 255)
speaker_name_align = "center"
draw.text((speaker_name_x, speaker_name_y), speaker_name_text, font=speaker_name_font, fill=speaker_name_fill)

# Paste the white circle onto the background
background.paste(circle, (speaker_image_x, speaker_image_y), circle)

# Paste the speaker image onto the white circle
speaker_image_x_offset = 15
speaker_image_y_offset = 15
background.paste(speaker_image, (speaker_image_x + speaker_image_x_offset, speaker_image_y + speaker_image_y_offset), speaker_image)

# Convert the image to RGB mode before saving
background = background.convert("RGB")

# Save the final image
thumbnail_path = THUMBNAIL_PATH
if not os.path.splitext(thumbnail_path)[1][1:] in IMAGE_EXTENSIONS:
    raise ValueError(f"Unsupported image extension: {os.path.splitext(thumbnail_path)[1]}")
background.save(thumbnail_path)
