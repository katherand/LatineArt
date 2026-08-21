import os
import re

ocrDir = "ocrTexts"
outputFile = "FULL_CATALOG_OCR_MASTER.txt"

def extractPageNumber(filename):
    """Extracts the digits from filenames like 'page08Master_ART_OCR.txt' for proper sorting."""
    match = re.search(r'page(\d+)', filename, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 0

def compileOcrFiles():
    if not os.path.exists(ocrDir):
        print(f"⚠️ Directory '{ocrDir}' not found.")
        return

    # Find all OCR txt files
    txtFiles = [
        f for f in os.listdir(ocrDir) 
        if f.lower().endswith('.txt') and not f.startswith('.')
    ]

    if not txtFiles:
        print(f"No text files found in '{ocrDir}'.")
        return

    # Sort files numerically by page number instead of standard alphabetical string sorting
    txtFiles.sort(key=extractPageNumber)

    print(f"Found {len(txtFiles)} page transcriptions. Compiling into {outputFile}...\n")

    compiledContent = []
    
    for fileName in txtFiles:
        pageNum = extractPageNumber(fileName)
        filePath = os.path.join(ocrDir, fileName)
        
        with open(filePath, "r", encoding="utf-8") as f:
            content = f.read().strip()

        # Add clear visual page header for easy physical auditing
        pageHeader = f"\n=========================================\n" \
                     f"  PAGE {pageNum:02d}  [{fileName}]\n" \
                     f"=========================================\n\n"
        
        compiledContent.append(pageHeader + content + "\n")

    # Write master document
    with open(outputFile, "w", encoding="utf-8") as outFile:
        outFile.writelines(compiledContent)

    print(f"✅ Master catalog compiled successfully -> {outputFile}")

if __name__ == "__main__":
    compileOcrFiles()