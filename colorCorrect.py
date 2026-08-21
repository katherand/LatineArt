import os
from PIL import Image, ImageEnhance, ImageStat

rawMastersDir = "rawMasters"
outputDir = "rawMasters_Corrected"

os.makedirs(outputDir, exist_ok=True)

# Adjustment factors
SATURATION_FACTOR = 0.80  # Reduces saturation by 20%
CONTRAST_FACTOR = 0.95    # Softens harsh shadows slightly by 5%

def isColorPlate(img):
    """Checks if the image has meaningful color variation (not just sepia/monochrome)."""
    if img.mode != "RGB":
        return False
    
    # Split RGB channels and compare variance between Red, Green, and Blue
    stat = ImageStat.Stat(img)
    r_mean, g_mean, b_mean = stat.mean[:3]
    
    # If RGB channel averages diverge significantly, it's a true color plate
    color_diff = abs(r_mean - g_mean) + abs(g_mean - b_mean) + abs(r_mean - b_mean)
    return color_diff > 15

def processTiffFile(fileName):
    inputPath = os.path.join(rawMastersDir, fileName)
    outputPath = os.path.join(outputDir, fileName)
    
    try:
        with Image.open(inputPath) as img:
            processedImg = img.copy()
            
            if isColorPlate(processedImg):
                # 1. Pull back oversaturated colors
                satEnhancer = ImageEnhance.Color(processedImg)
                processedImg = satEnhancer.enhance(SATURATION_FACTOR)
                
                # 2. Gently ease harsh contrast
                conEnhancer = ImageEnhance.Contrast(processedImg)
                processedImg = conEnhancer.enhance(CONTRAST_FACTOR)
                
                print(f"🎨 Corrected color plate: {fileName}")
            else:
                # For monochrome or near-monochrome sepia plates, apply gentle contrast fix only
                conEnhancer = ImageEnhance.Contrast(processedImg)
                processedImg = conEnhancer.enhance(0.98)
                print(f"⬛ Gentle contrast pass on monochrome/sepia plate: {fileName}")
            
            # Save uncompressed master TIFF
            processedImg.save(outputPath, format="TIFF", compression="raw")
            
    except Exception as err:
        print(f"❌ Error processing {fileName}: {err}")

def main():
    if not os.path.exists(rawMastersDir):
        print(f"⚠️ Directory '{rawMastersDir}' not found.")
        return
        
    tiffFiles = [f for f in os.listdir(rawMastersDir) if f.lower().endswith(('.tif', '.tiff'))]
    
    if not tiffFiles:
        print("No TIFF files found in rawMasters.")
        return
        
    print(f"--- Processing {len(tiffFiles)} TIFF files in batch ---\n")
    
    for fileName in sorted(tiffFiles):
        processTiffFile(fileName)
        
    print(f"\n✅ All done! Corrected masters saved to: '{outputDir}'")

if __name__ == "__main__":
    main()