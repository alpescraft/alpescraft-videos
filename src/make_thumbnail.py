from PIL import Image, ImageDraw, ImageFont
import yaml
import requests
from io import BytesIO

# Load the background image
background = Image.open("template/ht/background.png").convert("RGBA")

# Create a semi-transparent overlay
overlay = Image.new('RGBA', background.size, (101, 41, 86, 230))

# Paste the overlay on the background
background = Image.alpha_composite(background, overlay)

# Load the logo image and resize it
logo = Image.open("template/ht/logo-no-bg.png").convert("RGBA").resize((160, int(160 * Image.open("template/ht/logo.webp").size[1] / Image.open("template/ht/logo.webp").size[0])))

# Paste the logo on the background
background.paste(logo, (24, 24), logo)

# Load the talk configuration
with open("template/ht/talk1/config.yml", 'r') as stream:
    config = yaml.safe_load(stream)

# Load the speaker image and resize it
speaker_image = Image.open("template/ht/talk1/speaker.webp").resize((64, 64))

# Create a font for the title and speaker name
title_font = ImageFont.truetype("DejaVuSansMono.ttf", 16)
speaker_name_font = ImageFont.truetype("DejaVuSansMono.ttf", 12)

# Draw the title on the background
draw = ImageDraw.Draw(background)
title_text = config['title']
title_left, title_top, title_right, title_bottom = draw.textbbox((0, 0), title_text, font=title_font)
title_width = title_right - title_left
title_height = title_bottom - title_top
draw.text((24, 24 + logo.height), title_text, font=title_font, fill=(255, 255, 255))

# Draw the speaker name on the background
speaker_name_text = config['speaker_name']
speaker_name_left, speaker_name_top, speaker_name_right, speaker_name_bottom = draw.textbbox((0, 0), speaker_name_text, font=speaker_name_font)
speaker_name_width = speaker_name_right - speaker_name_left
speaker_name_height = speaker_name_bottom - speaker_name_top
speaker_name_y = 24 + logo.height + title_height + 24
speaker_name_x = background.width - speaker_image.width - speaker_name_width - 24
draw.text((speaker_name_x, speaker_name_y), speaker_name_text, font=speaker_name_font, fill=(255, 255, 255))

# Paste the speaker image on the background
speaker_image_y = speaker_name_y + (speaker_name_height - speaker_image.height) // 2
background.paste(speaker_image, (background.width - speaker_image.width - 24, speaker_image_y))

# Convert the image to RGB mode before saving
background = background.convert("RGB")

# Save the final image
background.save("template/ht/talk1/thumbnail.jpg")
