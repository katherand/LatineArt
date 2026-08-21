import os
from PIL import Image

source_dir = "rawMasters_Corrected"
web_dir = "rawMasters_Web"

os.makedirs(web_dir, exist_ok=True)

converted_count = 0

for filename in os.listdir(source_dir):
    if filename.lower().endswith(('.tif', '.tiff')):
        tif_path = os.path.join(source_dir, filename)
        base_name = os.path.splitext(filename)[0]
        png_path = os.path.join(web_dir, f"{base_name}.png")

        # Skip conversion if the target PNG already exists and is newer
        with Image.open(tif_path) as img:
            rgb_img = img.convert("RGB")
            rgb_img.save(png_path, "PNG", optimize=True)
            print(f"✅ Converted: {filename} -> {base_name}.png")
            converted_count += 1

print(f"\n🎉 Batch complete! Added {converted_count} web-ready PNG assets into 'rawMasters_Web/'.")