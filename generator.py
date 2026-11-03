import os
from PIL import Image, ImageDraw, ImageFont

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
        
        # Text positioning
        draw.text((160, 400), title, fill="#D4AF37")
        draw.text((160, 600), subtitle, fill="#FFFFFF")
        draw.text((160, 2400), page, fill="#8D99AE")
        
        filename = f"slides/slide_{i}.png"
        img_final = img.resize((1080, 1350), Image.Resampling.LANCZOS)
        img_final.save(filename, "PNG")
        slide_filenames.append(filename)
        
    print("Generated 4 luxury carousel slides successfully.")
    return slide_filenames

if __name__ == "__main__":
    create_carousel_slides()