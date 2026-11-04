import os
from PIL import Image, ImageDraw, ImageFont

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]


def load_font(size):
    for path in FONT_PATHS:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def create_carousel_slides():
    os.makedirs("slides", exist_ok=True)
    
    # 2x supersampling for ultra-sharp luxury output (1080x1350 portrait)
    width, height = 2160, 2700
    
    slides_data = [
        ("THE INDIAN RUPEES", "MASTERING YOUR MONEY", "01 / 04"),
        ("COMPOUNDING", "The 8th Wonder of the World", "02 / 04"),
        ("ASSET ALLOCATION", "Protect & Grow Your Capital", "03 / 04"),
        ("FINANCIAL FREEDOM", "Build Wealth. Live Free.", "04 / 04")
    ]
    
    slide_filenames = []
    for i, (title, subtitle, page) in enumerate(slides_data, start=1):
        img = Image.new("RGB", (width, height), color="#0B132B") # Deep navy luxury background
        draw = ImageDraw.Draw(img)
        
        # Draw luxury border frame
        draw.rectangle([80, 80, width - 80, height - 80], outline="#D4AF37", width=6)
        
        # Text positioning (sizes are for the 2x canvas; without a font size
        # Pillow draws a tiny ~10px bitmap font)
        draw.text((160, 400), title, fill="#D4AF37", font=load_font(150))
        draw.text((160, 650), subtitle, fill="#FFFFFF", font=load_font(90))
        draw.text((160, 2400), page, fill="#8D99AE", font=load_font(70))
        
        filename = f"slides/slide_{i}.png"
        img_final = img.resize((1080, 1350), Image.Resampling.LANCZOS)
        img_final.save(filename, "PNG")
        slide_filenames.append(filename)
        
    print("Generated 4 luxury carousel slides successfully.")
    return slide_filenames

if __name__ == "__main__":
    create_carousel_slides()