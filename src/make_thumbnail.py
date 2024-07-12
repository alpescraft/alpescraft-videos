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

# Load the logo image
logo = Image.open("template/ht/logo.webp").convert("RGBA")

# Paste the logo on the background
background.paste(logo, (0, 0), logo)

# Load the talk configuration
with open("template/ht/talk1/config.yml", 'r') as stream:
    config = yaml.safe_load(stream)

# Load the speaker image
speaker_image = Image.open("template/ht/talk1/speaker.webp")

# Create a font for the text
font = ImageFont.load_default()

# Draw the title and speaker name on the background
draw = ImageDraw.Draw(background)
draw.text((logo.width, 0), config['title'], font=font, fill=(255, 255, 255))
draw.text((background.width - speaker_image.width, logo.height), config['speaker_name'], font=font, fill=(255, 255, 255))
speaker_name_size = draw.textbbox((0, 0), config['speaker_name'], font=font)

# Paste the speaker image on the background
background.paste(speaker_image, (background.width - speaker_image.width, logo.height + speaker_name_size[3]))

# Convert the image to RGB mode before saving
background = background.convert("RGB")

# Save the final image
background.save("template/ht/talk1/thumbnail.jpg")
