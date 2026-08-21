from PIL import Image

# Quick preview script
tif_path = "rawMasters_Corrected/page34Master_ART.tif"
angle = 5.5  # Adjust this number until it looks right

with Image.open(tif_path) as img:
    straightened = img.rotate(angle, resample=Image.BICUBIC, expand=True, fillcolor=(255, 255, 255))
    straightened.show()  # Opens an interactive preview window immediately
    # Uncomment the line below once the angle looks perfect:
    # straightened.save(tif_path, format="TIFF")