from PIL import Image, ImageDraw

def create_circular_mask(height, width):
    # Create a new image with white background
    mask = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    # Create a circular mask
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, width, height), fill=(255, 255, 255, 255))

    # Save the mask to a file
    mask.save(f"circular-mask-{width}x{height}.png")

if __name__ == '__main__':
    create_circular_mask(200, 200)
