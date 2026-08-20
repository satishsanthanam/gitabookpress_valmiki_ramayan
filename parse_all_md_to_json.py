# parse_all_md_to_json.py
import json
import re
import os

# Configuration for all 7 Kandas
KANDAS_CONFIG = [
    {"md_file": "balakanda_mistral_ocr.md", "json_file": "data/Valmiki_Ramayan_Balakanda.json", "kanda_name": "Bala Kanda", "folder": "balakanda"},
    {"md_file": "ayodhyakanda_mistral_ocr.md", "json_file": "data/Valmiki_Ramayan_Ayodhyakanda.json", "kanda_name": "Ayodhya Kanda", "folder": "ayodhyakanda"},
    {"md_file": "aranyakanda_mistral_ocr.md", "json_file": "data/Valmiki_Ramayan_Aranyakanda.json", "kanda_name": "Aranya Kanda", "folder": "aranyakanda"},
    {"md_file": "kishkindhakanda_mistral_ocr.md", "json_file": "data/Valmiki_Ramayan_Kishkindhakanda.json", "kanda_name": "Kishkindha Kanda", "folder": "kishkindhakanda"},
    {"md_file": "sundarakanda_mistral_ocr.md", "json_file": "data/Valmiki_Ramayan_Sundarakanda.json", "kanda_name": "Sundara Kanda", "folder": "sundarakanda"},
    {"md_file": "yuddhakanda_mistral_ocr.md", "json_file": "data/Valmiki_Ramayan_Yuddhakanda.json", "kanda_name": "Yuddha Kanda", "folder": "yuddhakanda"},
    {"md_file": "uttarakanda_mistral_ocr.md", "json_file": "data/Valmiki_Ramayan_Uttarakanda.json", "kanda_name": "Uttara Kanda", "folder": "uttarakanda"},
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
                    "shloka_start": 0,
                    "shloka_end": 0,
                    "shloka_text": "",
                    "explanation": summary_clean,
                    "comments": None,
                    "audio_file": f"ramayana/{folder_name}/{sarga_num}_0.mp3"
                })

        # 2. Extract Verse Blocks
        pattern = r'([\u0900-\u097F\s\।॥0-9\.:\-\—]+[॥\|]\s*[\d१-९]+\s*[॥\|])\s*\n+([^\u0900-\u097F]+?\(\d+(?:[—\-]\d+)?\))'
        matches = re.findall(pattern, block_content, re.MULTILINE)

        for v_num, (sanskrit_text, raw_english) in enumerate(matches, 1):
            # Check for single vs multi-shloka range e.g., (18) vs (19—22)
            match_range = re.search(r'\((\d+)(?:[—\-](\d+))?\)', raw_english)
            
            if match_range:
                shloka_start = int(match_range.group(1))
                shloka_end = int(match_range.group(2)) if match_range.group(2) else shloka_start
            else:
                shloka_start = v_num
                shloka_end = v_num

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
                "shloka_start": shloka_start,
                "shloka_end": shloka_end,
                "shloka_text": sanskrit_cleaned,
                "explanation": exp_cleaned,
                "comments": None,
                "audio_file": f"ramayana/{folder_name}/{sarga_num}_{shloka_start}.mp3"
            })
            
        current_sarga += 1

    # 3. Group by Sarga & Sort Shlokas Numerically by shloka_start
    sarga_groups = {}
    for item in shlokas_data:
        s = item["sarga"]
        if s not in sarga_groups:
            sarga_groups[s] = []
        sarga_groups[s].append(item)

    final_sorted_data = []
    for s_num in sorted(sarga_groups.keys()):
        sorted_sarga = sorted(sarga_groups[s_num], key=lambda x: x["shloka_start"])
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