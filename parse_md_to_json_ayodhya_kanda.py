# Version 3.3 - Valmiki Ramayana Markdown to JSON Converter (Sarga Summary Included)
# Updates in v3.3:
# - Extracts Canto English summaries and creates a 'shloka: 0' entry per Sarga.
# - Assigns 'audio_file': 'ramayana/ayodhyakanda/{sarga}_0.mp3' for Sarga summaries.
# - Cleans stray OCR artifacts, page headers, page numbers, and footnote asterisks.

import json
import re

INPUT_MD_FILE = "ayodhyakanda_mistral_ocr.md"
OUTPUT_JSON_FILE = "data/Valmiki_Ramayan_Ayodhyakanda.json"
KANDA_NAME = "Ayodhya Kanda"
KANDA_FOLDER = "ayodhyakanda"

# =====================================================================
# STEP 1: PARSE MARKDOWN TO RAW STRUCTURE (WITH SARGA SUMMARY)
# =====================================================================
def parse_mistral_markdown(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    shlokas_data = []
    
    # Split text by Canto headers (e.g., "Canto I", "## Canto II", etc.)
    canto_blocks = re.split(r'(?:\n#{1,4}\s*|\n)(?:Canto|CANTO)\s+([IVXLCDM\d]+)', text)

    current_sarga = 1
    # Index 0 is metadata/preamble, cantos start at index 1 in pairs (canto_num, content)
    for i in range(1, len(canto_blocks), 2):
        sarga_num = current_sarga
        block_content = canto_blocks[i+1] if i+1 < len(canto_blocks) else ""

        # --- EXTRACT SARGA SUMMARY (SHLOKA 0) ---
        # Find the text between "Canto N" and the first Sanskrit shloka line
        first_shloka_match = re.search(r'[\u0900-\u097F]', block_content)
        if first_shloka_match:
            summary_raw = block_content[:first_shloka_match.start()]
            # Clean up summary text (remove Devanagari Sarga titles if any matched before the first verse)
            summary_clean = re.sub(r'[\u0900-\u097F]+', '', summary_raw)
            summary_clean = re.sub(r'[\r\n]+', ' ', summary_clean)
            summary_clean = " ".join(summary_clean.split()).strip()

            if summary_clean:
                shlokas_data.append({
                    "kanda": KANDA_NAME,
                    "sarga": sarga_num,
                    "shloka": 0,
                    "shloka_text": "",
                    "transliteration": "",
                    "translation": "",
                    "explanation": summary_clean,
                    "comments": None
                })

        # --- EXTRACT SHLOKAS ---
        pattern = r'([\u0900-\u097F\s\।॥0-9\.:\-\—]+[॥\|]\s*[\d१-९]+\s*[॥\|])\s*\n+([^\u0900-\u097F]+?\(\d+(?:[—\-]\d+)?\))'
        matches = re.findall(pattern, block_content, re.MULTILINE)

        for v_num, (sanskrit_text, raw_english) in enumerate(matches, 1):
            match_num = re.search(r'\((\d+)(?:[—\-]\d+)?\)', raw_english)
            shloka_no = int(match_num.group(1)) if match_num else v_num

            shlokas_data.append({
                "kanda": KANDA_NAME,
                "sarga": sarga_num,
                "shloka": shloka_no,
                "shloka_text": sanskrit_text.strip(),
                "transliteration": "",
                "translation": "",
                "explanation": raw_english.strip(),
                "comments": None
            })
            
        current_sarga += 1

    return shlokas_data


# =====================================================================
# STEP 2: CLEAN OCR ARTIFACTS & ATTACH MP3 LINKS
# =====================================================================
def clean_and_normalize_dataset(raw_dataset):
    cleaned_dataset = []

    for item in raw_dataset:
        sarga = item["sarga"]
        shloka = item["shloka"]
        raw_exp = item.get("explanation", "")
        raw_sanskrit = item.get("shloka_text", "")

        # 1. Clean Devanagari Shloka Text
        sanskrit_cleaned = re.sub(r'^\s*[\.\*•]\s*', '', raw_sanskrit)
        sanskrit_cleaned = re.sub(r'^\s*\d{1,4}\s*$', '', sanskrit_cleaned, flags=re.MULTILINE)
        sanskrit_cleaned = re.sub(r'[\r\n]+', '\n', sanskrit_cleaned).strip()

        # 2. Clean English Explanation
        exp_cleaned = re.sub(r'\*\s*VĀLMĪKI-RĀMĀYAṆA\s*\*|\*\s*AYODHYĀKĀṆḌA\s*\*|\*\s*AYODHYĀKĀNḌA\s*\*|\*\s*Ayodhyākāṇḍa\s\*', '', raw_exp)
        exp_cleaned = re.sub(r'^\s*\d{1,4}\s*$', '', exp_cleaned, flags=re.MULTILINE)
        exp_cleaned = re.sub(r'^\s*\*.*$', '', exp_cleaned, flags=re.MULTILINE) # Remove footnotes
        exp_cleaned = re.sub(r'[\r\n]+', ' ', exp_cleaned)
        exp_cleaned = " ".join(exp_cleaned.split()).strip()

        # 3. For actual shlokas (shloka > 0), ensure proper trailing verse tag (N)
        if shloka > 0:
            exp_cleaned = re.sub(r'\(\s*[\-—]?\s*\)', f'({shloka})', exp_cleaned)
            if exp_cleaned and not re.search(r'\(\d+(?:[—\-]\d+)?\)$', exp_cleaned):
                exp_cleaned = f"{exp_cleaned} ({shloka})"

        cleaned_item = {
            "kanda": item["kanda"],
            "sarga": sarga,
            "shloka": shloka,
            "shloka_text": sanskrit_cleaned,
            "transliteration": item.get("transliteration", ""),
            "translation": item.get("translation", ""),
            "explanation": exp_cleaned,
            "comments": item.get("comments", None),
            "audio_file": f"ramayana/{KANDA_FOLDER}/{sarga}_{shloka}.mp3"
        }

        cleaned_dataset.append(cleaned_item)

    return cleaned_dataset


# =====================================================================
# MAIN PIPELINE EXECUTION (v3.3)
# =====================================================================
if __name__ == "__main__":
    print("--- [Version 3.3] Valmiki Ramayana Converter (With Sarga Summaries) ---")
    raw_data = parse_mistral_markdown(INPUT_MD_FILE)
    print(f"-> Extracted {len(raw_data)} raw shloka/summary blocks.")

    final_data = clean_and_normalize_dataset(raw_data)

    with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)

    print(f"✓ [Version 3.3] Pipeline complete! Saved {len(final_data)} entries to {OUTPUT_JSON_FILE}")