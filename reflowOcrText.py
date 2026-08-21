import os
import re

inputFile = "FULL_CATALOG_OCR_MASTER.txt"
outputFile = "FULL_CATALOG_OCR_REFLOWED.txt"

def reflowText(rawText):
    # Split text into distinct blocks separated by blank lines
    blocks = rawText.split("\n\n")
    reflowedBlocks = []

    for block in blocks:
        # Preserve page headers (e.g., ================= PAGE 01 =================)
        if "====" in block:
            reflowedBlocks.append("\n" + block.strip() + "\n")
            continue

        # Clean internal line breaks within a paragraph block
        # Replaces single newlines with spaces, collapsing multiple spaces
        cleanedBlock = re.sub(r'(?<!\n)\n(?!\n)', ' ', block.strip())
        cleanedBlock = re.sub(r' +', ' ', cleanedBlock)

        if cleanedBlock:
            reflowedBlocks.append(cleanedBlock)

    # Rejoin blocks with clear double line breaks
    return "\n\n".join(reflowedBlocks)

def main():
    if not os.path.exists(inputFile):
        print(f"⚠️ Input file '{inputFile}' not found.")
        return

    with open(inputFile, "r", encoding="utf-8") as f:
        rawText = f.read()

    reflowedText = reflowText(rawText)

    with open(outputFile, "w", encoding="utf-8") as f:
        f.write(reflowedText)

    print(f"✅ Reflowed text saved to: '{outputFile}'")
    print("Narrow column line wraps have been merged into readable paragraph blocks!")

if __name__ == "__main__":
    main()