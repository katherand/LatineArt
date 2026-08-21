import os
import time
import urllib.request
import fitz  # PyMuPDF
from PIL import Image

printerIp = "192.168.1.92"
outputDir = "rawMasters"

os.makedirs(outputDir, exist_ok=True)

def convertPdfToUncompressedTiff(pdfPath, tiffPath):
    """Extracts raw high-resolution raster from scanner PDF and saves as uncompressed TIFF."""
    try:
        doc = fitz.open(pdfPath)
        page = doc[0]
        # Render page at high scale (300 DPI base * 4 = 1200 DPI equivalent)
        zoom = 4
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img.save(tiffPath, format="TIFF", compression="raw")
        print(f"🖼️ Converted PDF stream -> Uncompressed Master TIFF: {tiffPath}")
        
        if os.path.exists(pdfPath):
            os.remove(pdfPath)
            
    except Exception as err:
        print(f"⚠️ PDF to TIFF Conversion Error: {err}")

def triggerScanAndDownload(actualPageNum, scanType="txt"):
    isArtPlate = scanType.lower() == "art"
    
    colorMode = "RGB24" if isArtPlate else "Grayscale8"
    dpiResolution = 1200 if isArtPlate else 600
    docFormat = "application/pdf" if isArtPlate else "image/jpeg"
    
    if isArtPlate:
        tempPdfPath = os.path.join(outputDir, f"temp_page{actualPageNum:02d}.pdf")
        finalTiffPath = os.path.join(outputDir, f"page{actualPageNum:02d}Master_ART.tif")
        targetDownloadPath = tempPdfPath
    else:
        finalJpgPath = os.path.join(outputDir, f"page{actualPageNum:02d}Master_TXT.jpg")
        targetDownloadPath = finalJpgPath

    xmlPayload = f"""<?xml version="1.0" encoding="UTF-8"?>
    <scan:ScanSettings xmlns:scan="http://schemas.hp.com/imaging/escl/2011/05/03">
        <pwg:Version xmlns:pwg="http://www.pwg.org/schemas/2010/12/sm">2.0</pwg:Version>
        <scan:Intent>Document</scan:Intent>
        <scan:DocumentFormat>{docFormat}</scan:DocumentFormat>
        <scan:XResolution>{dpiResolution}</scan:XResolution>
        <scan:YResolution>{dpiResolution}</scan:YResolution>
        <scan:ColorMode>{colorMode}</scan:ColorMode>
        <scan:InputSource>Platen</scan:InputSource>
    </scan:ScanSettings>""".encode('utf-8')
    
    print(f"\nTriggering {colorMode} ({docFormat}) at {dpiResolution} DPI...")
    
    req = urllib.request.Request(
        f"http://{printerIp}:80/eSCL/ScanJobs",
        data=xmlPayload,
        headers={"Content-Type": "text/xml"}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            jobLocation = response.headers.get("Location")
            print(f"Scan initiated. Job URI: {jobLocation}")
            
        waitTime = 8 if isArtPlate else 3
        time.sleep(waitTime)
        
        documentUrl = f"{jobLocation}/NextDocument"
        print("Downloading stream...")
        urllib.request.urlretrieve(documentUrl, targetDownloadPath)
        
        if isArtPlate:
            convertPdfToUncompressedTiff(tempPdfPath, finalTiffPath)
            print(f"✅ Master TIFF saved: {finalTiffPath}")
        else:
            print(f"✅ Text JPG saved: {finalJpgPath}")
            
    except Exception as error:
        print(f"❌ Direct eSCL HTTP Error: {error}")

def main():
    print("--- Catalog Digitization (Direct Sequential 1-48) ---")
    
    while True:
        pageInput = input("\nEnter Page Number (1-48) or 'q' to quit: ").strip()
        if pageInput.lower() == 'q':
            break
            
        scanType = input("Enter Scan Type ('txt' for Grayscale JPG / 'art' for Lossless TIFF, default 'txt'): ").strip().lower() or "txt"
        
        try:
            actualPage = int(pageInput)
            if 1 <= actualPage <= 48:
                input(f"Place Page {actualPage:02d} on flatbed glass and press ENTER to start scanning...")
                triggerScanAndDownload(actualPage, scanType)
            else:
                print("⚠️ Please enter a page number between 1 and 48.")
        except ValueError:
            print("⚠️ Please enter a valid number.")

if __name__ == "__main__":
    main()