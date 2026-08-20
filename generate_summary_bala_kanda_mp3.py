# Script: generate_summary_mp3s.py
# Purpose: Generate MP3 audio ONLY for shloka: 0 (Sarga Summaries)

import os
import json
import asyncio
import re
import unicodedata
import edge_tts

# Configuration
JSON_FILES = [
    ("Valmiki_Ramayan_Balakanda.json", "./audio/ramayana/balakanda/")
]

VOICE = "en-IN-PrabhatNeural"

def convert_iast_to_plain_ascii(text):
    if not text:
        return ""
    normalized = unicodedata.normalize('NFD', text)
    return "".join(c for c in normalized if unicodedata.category(c) != 'Mn')

def clean_text_for_speech(text):
    if not text:
        return ""
    cleaned = convert_iast_to_plain_ascii(text)
    cleaned = re.sub(r'["\'”“*#]', '', cleaned)
    cleaned = re.sub(r'[\r\n]+', ' ', cleaned)
    return " ".join(cleaned.split()).strip()

async def generate_audio(text, output_filepath):
    communicate = edge_tts.Communicate(text, VOICE, rate="-5%")
    await communicate.save(output_filepath)

async def process_summaries():
    for json_file, target_dir in JSON_FILES:
        if not os.path.exists(json_file):
            print(f"⚠️ Dataset {json_file} not found. Skipping...")
            continue

        os.makedirs(target_dir, exist_ok=True)
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Filter strictly for shloka 0 (Summaries)
        summaries = [item for item in data if item.get("shloka") == 0]
        print(f"\n--- Found {len(summaries)} Sarga Summaries in {json_file} ---")

        for index, item in enumerate(summaries, 1):
            sarga = item.get("sarga", 1)
            raw_text = item.get("explanation") or item.get("translation")
            text_for_tts = clean_text_for_speech(raw_text)

            if not text_for_tts:
                continue

            filename = f"{sarga}_0.mp3"
            filepath = os.path.join(target_dir, filename)

            if os.path.exists(filepath):
                print(f"  [{index}/{len(summaries)}] Skipped (already exists): {filename}")
                continue

            try:
                await generate_audio(text_for_tts, filepath)
                print(f"  [{index}/{len(summaries)}] ✓ Generated: {filename}")
            except Exception as e:
                print(f"  ❌ Error generating {filename}: {e}")

if __name__ == "__main__":
    asyncio.run(process_summaries())