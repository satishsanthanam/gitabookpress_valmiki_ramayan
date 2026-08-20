# parse_all_md_to_json.py
import json
import re
import os

# Configuration for all 7 Kandas
KANDAS_CONFIG = [
    
    {"md_file": "yuddhakanda_mistral_ocr.md", "json_file": "data/Valmiki_Ramayan_Yuddhakanda.json", "kanda_name": "Yuddha Kanda", "folder": "yuddhakanda"}
]

def parse_markdown_file(file_path, kanda_name, folder_name):
    if not os.path.exists(file_path):
        print(f"⚠️ Warning: File '{file_path}' not found. Skipping...")
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    shlokas_data = []
    canto_blocks = re.split(r'(?:\n#{1,4}\s*|\n)(?:Canto|CANTO|Sarga|SARGA)\s+([IVXLCDM\d]+)', text)

    current_sarga = 1
    for i in range(1, len(canto_blocks), 2):
        sarga_num = current_sarga
        block_content = canto_blocks[i+1] if i+1 < len(canto_blocks) else ""

        # 1. Extract Sarga Summary (shloka: 0)
        first_shloka_match = re.search(r'[\u0900-\u097F]', block_content)
        if first_shloka_match:
            summary_raw = block_content[:first_shloka_match.start()]
            summary_clean = re.sub(r'[\u0900-\u097F]+', '', summary_raw)
            summary_clean = re.sub(r'[\r\n]+', ' ', summary_clean)
            summary_clean = " ".join(summary_clean.split()).strip()

            if summary_clean:
                shlokas_data.append({
                    "kanda": kanda_name,
                    "sarga": sarga_num,
                    "shloka": 0,
                    "shloka_text": "",
                    "transliteration": "",
                    "translation": "",
                    "explanation": summary_clean,
                    "comments": None,
                    "audio_file": f"ramayana/{folder_name}/{sarga_num}_0.mp3"
                })

        # 2. Extract Verse Blocks
        pattern = r'([\u0900-\u097F\s\।॥0-9\.:\-\—]+[॥\|]\s*[\d१-९]+\s*[॥\|])\s*\n+([^\u0900-\u097F]+?\(\d+(?:[—\-]\d+)?\))'
        matches = re.findall(pattern, block_content, re.MULTILINE)

        for v_num, (sanskrit_text, raw_english) in enumerate(matches, 1):
            match_num = re.search(r'\((\d+)(?:[—\-]\d+)?\)', raw_english)
            shloka_no = int(match_num.group(1)) if match_num else v_num

            # Clean Sanskrit
            sanskrit_cleaned = re.sub(r'^\s*[\.\*•]\s*', '', sanskrit_text)
            sanskrit_cleaned = re.sub(r'^\s*\d{1,4}\s*$', '', sanskrit_cleaned, flags=re.MULTILINE)
            sanskrit_cleaned = re.sub(r'[\r\n]+', '\n', sanskrit_cleaned).strip()

            # Clean English Explanation
            exp_cleaned = re.sub(r'[\r\n]+', ' ', raw_english)
            exp_cleaned = " ".join(exp_cleaned.split()).strip()

            shlokas_data.append({
                "kanda": kanda_name,
                "sarga": sarga_num,
                "shloka": shloka_no,
                "shloka_text": sanskrit_cleaned,
                "transliteration": "",
                "translation": "",
                "explanation": exp_cleaned,
                "comments": None,
                "audio_file": f"ramayana/{folder_name}/{sarga_num}_{shloka_no}.mp3"
            })
            
        current_sarga += 1

    # 3. CRITICAL: Group by Sarga & Sort Slokas Numerically (Fixes Out-of-Order sequence)
    sarga_groups = {}
    for item in shlokas_data:
        s = item["sarga"]
        if s not in sarga_groups:
            sarga_groups[s] = []
        sarga_groups[s].append(item)

    final_sorted_data = []
    for s_num in sorted(sarga_groups.keys()):
        sorted_sarga = sorted(sarga_groups[s_num], key=lambda x: x["shloka"])
        final_sorted_data.extend(sorted_sarga)

    return final_sorted_data

def process_all_kandas():
    os.makedirs("data", exist_ok=True)
    
    for cfg in KANDAS_CONFIG:
        print(f"Processing '{cfg['kanda_name']}' from {cfg['md_file']}...")
        parsed_data = parse_markdown_file(cfg['md_file'], cfg['kanda_name'], cfg['folder'])
        
        if parsed_data:
            with open(cfg['json_file'], "w", encoding="utf-8") as f:
                json.dump(parsed_data, f, ensure_ascii=False, indent=2)
            print(f"  ✓ Saved {len(parsed_data)} entries to '{cfg['json_file']}'\n")

if __name__ == "__main__":
    process_all_kandas()