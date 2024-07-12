from PIL import Image, ImageDraw, ImageFont
import yaml
import requests
from io import BytesIO
import textwrap

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
background = Image.open("template/ht/background.png").convert("RGBA")

# Create a semi-transparent overlay
overlay = Image.new('RGBA', background.size, (101, 41, 86, 230))

# Paste the overlay on the background
background = Image.alpha_composite(background, overlay)

# Load the logo image and resize it
logo = Image.open("template/ht/logo-no-bg.png").convert("RGBA").resize((895, int(895 * Image.open("template/ht/logo-no-bg.png").size[1] / Image.open("template/ht/logo-no-bg.png").size[0])))

# Paste the logo on the background
background.paste(logo, (64, 64), logo)

# Load the talk configuration
with open("template/ht/talk1/config.yml", 'r') as stream:
    config = yaml.safe_load(stream)
# Load the speaker image and resize it
speaker_image = Image.open("template/ht/talk1/speaker.webp").resize((250, 250))

# Create a circular mask for the speaker image
speaker_mask = Image.new("L", speaker_image.size, 0)
draw = ImageDraw.Draw(speaker_mask)
mask_radius = min(speaker_image.size) // 2
mask_center = (speaker_image.size[0] // 2, speaker_image.size[1] // 2)
draw.ellipse((mask_center[0] - mask_radius, mask_center[1] - mask_radius, mask_center[0] + mask_radius, mask_center[1] + mask_radius), fill=255)

# Draw a white circle of 15px larger than the mask
# circle_radius = mask_radius + 15
# border = Image.new("L", speaker_image.size, 0)
# draw_border = ImageDraw.Draw(speaker_mask)
# draw.ellipse((mask_center[0] - circle_radius, mask_center[1] - circle_radius, mask_center[0] + circle_radius, mask_center[1] + circle_radius), fill=255)

# Create a new image with the same size as the speaker image
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
multiline_text(draw, title_text, title_font, 1400, 1000, 64, 192 + logo.height, fill=(255, 255, 255), align="left")

# Draw the speaker name on the background
# Draw the speaker name on the background
speaker_name_text = config['speaker_name']
speaker_image_x = 1400 + 113
speaker_image_y = 192 + logo.height
speaker_name_width = draw.textbbox((0, 0), speaker_name_text, font=speaker_name_font)[2] - draw.textbbox((0, 0), speaker_name_text, font=speaker_name_font)[0]
speaker_name_height = draw.textbbox((0, 0), speaker_name_text, font=speaker_name_font)[3] - draw.textbbox((0, 0), speaker_name_text, font=speaker_name_font)[1]
speaker_name_x = background.width - speaker_name_width - 48
speaker_name_y = speaker_image_y + speaker_image.height
multiline_text(draw, speaker_name_text, speaker_name_font, 476, speaker_name_height, speaker_name_x, speaker_name_y, fill=(255, 255, 255), align="center")


# Paste the speaker image on the background
# speaker_image_y = 64 + logo.height + 1000 + 64

# Paste the white circle onto the background
background.paste(circle, (speaker_image_x, speaker_image_y), circle)
background.paste(speaker_image, (speaker_image_x + 15, speaker_image_y + 15), speaker_image)

# Convert the image to RGB mode before saving
background = background.convert("RGB")

# Save the final image
background.save("template/ht/talk1/thumbnail.jpg")
