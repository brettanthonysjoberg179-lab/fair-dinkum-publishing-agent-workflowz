
from PIL import Image, ImageDraw, ImageFont
import textwrap

def generate_thumbnail(title, output_path, background_color="#1a1a1a", text_color="#ffffff"):
    # Canvas setup
    width, height = 1200, 1200
    img = Image.new('RGB', (width, height), color=background_color)
    draw = ImageDraw.Draw(img)

    # Font setup - using a default font
    # In production, load a specific font file
    try:
        font = ImageFont.truetype("arial.ttf", 80)
    except IOError:
        font = ImageFont.load_default()

    # Text rendering
    lines = textwrap.wrap(title, width=20)
    y_text = 400
    for line in lines:
        # Simple centering
        bbox = draw.textbbox((0, 0), line, font=font)
        text_w = bbox[2] - bbox[0]
        x_text = (width - text_w) / 2
        draw.text((x_text, y_text), line, font=font, fill=text_color)
        y_text += 100

    img.save(output_path)
    return output_path

if __name__ == "__main__":
    # Test generation
    generate_thumbnail("Example Product Title", "test_thumb.png")
    print("Thumbnail generated.")
