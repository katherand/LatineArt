import os
import re
import json
from difflib import SequenceMatcher

inputFile = "FULL_CATALOG_OCR_REFLOWED.txt"
outputFile = "latine_catalog_data.json"

ARTISTS_LIST = [
    "Julio Antonio", "Maria Brito", "Alicia Candiani", "Tony Capellán",
    "Elizabeth Cerejido", "Esperanza Cortés", "Karina Chechik", "Teresa & Allen Diehl",
    "Edouard Duval-Carrié", "Felipe Ehrenberg", "Eugenio Espinosa", "Eduardo Daniel Fiorda",
    "Florencio Gelabert", "Maria Gnecco", "Luz Maria Gordillo", "Nicolás Leiva",
    "Antonio Migliori", "Rebeca Mendoza", "Liora Mondlak", "Gabriel Orenstein",
    "Jorge Pantoja", "Renata Pedrosa", "Jorge Pineda", "Gloria Rodriguez",
    "Lydia Rubio", "Raimundo Rubio", "Juan Sánchez", "Carolina Sardi",
    "Juan-Si", "Paul Sierra", "Betina Sor", "Pablo Soria",
    "Raphael Soriano", "Sebastian Spreng", "Miguel Trelles", "Jorge Vera"
]

def clean_for_comparison(text):
    """Strips special characters and normalizes case for fuzzy checks."""
    return re.sub(r'[^a-zA-Z\s]', '', text).lower().strip()

def similarity(a, b):
    return SequenceMatcher(None, clean_for_comparison(a), clean_for_comparison(b)).ratio()

def extractAllPlates(text):
    plates = []
    rawMatches = re.findall(r'\[(.*?)\]', text, re.DOTALL)
    
    for match in rawMatches:
        if "_OCR.txt" in match or "TXT_OCR" in match or "Page skipped" in match:
            continue
            
        cleanedContent = re.sub(r'\s+', ' ', match.strip())
        
        if '|' in cleanedContent:
            parts = [p.strip() for p in cleanedContent.split('|')]
            if len(parts) >= 3:
                plates.append({"artist": parts[0], "title": parts[1], "imagePath": parts[2]})
            elif len(parts) == 2:
                plates.append({"artist": parts[0], "title": parts[0], "imagePath": parts[1]})
                
        elif "rawMasters_Corrected/" in cleanedContent:
            pathMatch = re.search(r'(rawMasters_Corrected/\S+)', cleanedContent)
            if pathMatch:
                imagePath = pathMatch.group(1)
                textBeforePath = cleanedContent.replace(imagePath, '').strip()
                plates.append({"artist": textBeforePath, "title": textBeforePath, "imagePath": imagePath})

    return plates

def main():
    if not os.path.exists(inputFile):
        print(f"⚠️ File '{inputFile}' not found.")
        return

    with open(inputFile, "r", encoding="utf-8") as f:
        rawText = f.read()

    # Step 1: Extract plates globally
    allPlates = extractAllPlates(rawText)

    # Step 2: Slice between "forward" and "afterword"
    bioText = rawText
    forwardMatch = re.search(r'\n\s*forwa?rd\b', rawText, re.IGNORECASE)
    if forwardMatch:
        bioText = rawText[forwardMatch.end():]
        
    afterwordMatch = re.search(r'\n\s*afterword\b', bioText, re.IGNORECASE)
    if afterwordMatch:
        bioText = bioText[:afterwordMatch.start()]

    # Step 3: CRITICAL CLEANING - Strip page headers AND bracketed tags BEFORE line parsing
    cleanBioText = re.sub(r'=========================================\s*PAGE \d+\s*\[.*?\]\s*=========================================', '', bioText)
    cleanBioText = re.sub(r'\[.*?\]', '', cleanBioText)

    # Split into non-empty lines
    lines = [line.strip() for line in cleanBioText.split('\n') if line.strip()]

    headerLocations = [] # List of matched headers: {"line_idx", "artist", "raw_line"}

    # Step 4: Line-by-line Fuzzy Header Matching
    for idx, line in enumerate(lines):
        for artist in ARTISTS_LIST:
            # Match directly if exact, or use fuzzy matching for spellos/accents
            exact_match = clean_for_comparison(line) == clean_for_comparison(artist)
            score = similarity(line, artist)

            if exact_match or score >= 0.80:
                headerLocations.append({
                    "line_idx": idx,
                    "artist": artist,
                    "raw_line": line,
                    "score": score
                })
                break # Move to next line once matched

    # Sort headers by order of appearance
    headerLocations.sort(key=lambda x: x["line_idx"])

    # Build bios dictionary
    artistBios = {artist: "" for artist in ARTISTS_LIST}

    for i in range(len(headerLocations)):
        current = headerLocations[i]
        start_line = current["line_idx"] + 1
        
        if i + 1 < len(headerLocations):
            end_line = headerLocations[i+1]["line_idx"]
        else:
            end_line = len(lines)

        bio_content = " ".join(lines[start_line:end_line])
        artistBios[current["artist"]] = bio_content

    # Step 5: Assemble JSON
    parsedCatalog = {
        "metadata": {
            "title": "Latin American Artists Traveling Exhibition Catalog",
            "imageDirectory": "rawMasters_Corrected",
            "totalArtists": len(ARTISTS_LIST),
            "totalPlates": len(allPlates)
        },
        "artists": []
    }

    missing_count = 0
    for artist in ARTISTS_LIST:
        bio = artistBios.get(artist, "")
        if not bio:
            print(f"❌ Missing Bio Warning: '{artist}'")
            missing_count += 1

        artistNorm = clean_for_comparison(artist)
        artistPlates = [
            p for p in allPlates 
            if artistNorm in clean_for_comparison(p["artist"]) or artistNorm in clean_for_comparison(p["title"])
        ]

        parsedCatalog["artists"].append({
            "name": artist,
            "bio": bio,
            "artworks": artistPlates
        })

    with open(outputFile, "w", encoding="utf-8") as f:
        json.dump(parsedCatalog, f, ensure_ascii=False, indent=2)

    print("\n" + "="*50)
    print(f"✅ Ingestion Complete!")
    print(f"   Indexed {parsedCatalog['metadata']['totalArtists']} Artists")
    print(f"   Extracted {parsedCatalog['metadata']['totalPlates']} Total Artwork Plates")
    if missing_count > 0:
        print(f"   ⚠️ {missing_count} Artists are missing bios. Check warnings above!")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()