import os
import pytesseract
from PIL import Image

inputDir = "rawMasters"
outputDir = "ocrTexts"

os.makedirs(outputDir, exist_ok=True)

def preprocessForOcr(img):
    """Converts image to clean high-contrast grayscale for maximum OCR accuracy."""
    # Convert to pure grayscale
    gray = img.convert("L")
    return gray

def ocrSingleFile(fileName):
    inputPath = os.path.join(inputDir, fileName)
    baseName = os.path.splitext(fileName)[0]
    txtOutputPath = os.path.join(outputDir, f"{baseName}_OCR.txt")
    
    try:
        with Image.open(inputPath) as img:
            processed = preprocessForOcr(img)
            
            # Run Tesseract OCR (supports Spanish and English text extraction)
            # --psm 3 = Automatic page segmentation (detects multi-column text layouts)
            extractedText = pytesseract.image_to_string(processed, lang="eng+spa", config="--psm 3")
            
            # Save raw text to file
            with open(txtOutputPath, "w", encoding="utf-8") as txtFile:
                txtFile.write(extractedText)
                
            print(f"📄 Successfully extracted text -> {txtOutputPath}")
            
    except Exception as err:
        print(f"❌ OCR failed for {fileName}: {err}")

def main():
    if not os.path.exists(inputDir):
        print(f"⚠️ Directory '{inputDir}' not found.")
        return

    # Process all JPG text pages and TIF art plates in rawMasters
    imageFiles = [
        f for f in os.listdir(inputDir) 
        if f.lower().endswith(('.jpg', '.jpeg', '.tif', '.tiff')) and not f.startswith('.')
    ]
    
    if not imageFiles:
        print(f"No image files found in {inputDir}.")
        return

    print(f"--- Running Tesseract OCR on {len(imageFiles)} pages ---\n")
    
    for fileName in sorted(imageFiles):
        ocrSingleFile(fileName)
        
    print(f"\n✅ OCR Processing complete! Text files stored in: '{outputDir}'")

if __name__ == "__main__":
    main()