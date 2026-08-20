# Version 4.3 - Valmiki Ramayana MP3 Generator & Sarga Concatenator
# Updates in v4.3:
# - Generates verse MP3s (1_0.mp3, 1_1.mp3...) in ./audio/ramayana/<kanda>/
# - Concatenates full Sarga audio into ./audio/ramayana/<kanda>/<sarga_num>.mp3 (e.g. 1.mp3)
# - Adds a subtle 400ms pause between verses during concatenation
# - Uses IAST normalization for natural TTS speech

import os
import json
import asyncio
import re
import unicodedata
import edge_tts
from pydub import AudioSegment

# Inputs
JSON_PATH = "data/Valmiki_Ramayan_Ayodhyakanda.json"
BASE_AUDIO_DIR = "./audio/ramayana/"

# Voice Selection
VOICE = "en-IN-PrabhatNeural"

def convert_iast_to_plain_ascii(text):
    """Normalizes IAST diacritics into plain ASCII text for TTS pronunciation."""
    if not text:
        return ""
    normalized = unicodedata.normalize('NFD', text)
    return "".join(c for c in normalized if unicodedata.category(c) != 'Mn')

def clean_text_for_speech(text):
    """Strips IAST diacritics, trailing verse numbers, quotes, and footnotes."""
    if not text:
        return ""
    cleaned = convert_iast_to_plain_ascii(text)
    cleaned = re.sub(r'\(\d+(?:[—\-]\d+)?\)$', '', cleaned)
    cleaned = re.sub(r'["\'”“*#]', '', cleaned)
    cleaned = re.sub(r'[\r\n]+', ' ', cleaned)
    return " ".join(cleaned.split()).strip()

async def generate_shloka_audio(text, output_filepath):
    communicate = edge_tts.Communicate(text, VOICE, rate="-5%")
    await communicate.save(output_filepath)

def concat_sarga_audio(target_dir, sarga_num, verse_items):
    """Merges all individual verse MP3s of a Sarga into a single <sarga_num>.mp3 file."""
    merged_filename = f"{sarga_num}.mp3"
    merged_filepath = os.path.join(target_dir, merged_filename)

    if os.path.exists(merged_filepath):
        print(f"  ⏩ Skipping Sarga merge: '{merged_filepath}' already exists.")
        return

    combined_audio = AudioSegment.empty()
    # Sort verses so 0 (summary) comes first, followed by 1, 2, 3...
    sorted_verses = sorted(verse_items, key=lambda x: x.get("shloka", 0))

    for item in sorted_verses:
        shloka = item.get("shloka", 0)
        verse_mp3_path = os.path.join(target_dir, f"{sarga_num}_{shloka}.mp3")

        if os.path.exists(verse_mp3_path):
            verse_audio = AudioSegment.from_mp3(verse_mp3_path)
            combined_audio += verse_audio
            # Add a 400ms pause between verses for a natural narration pace
            combined_audio += AudioSegment.silent(duration=400)

    if len(combined_audio) > 0:
        combined_audio.export(merged_filepath, format="mp3", bitrate="128k")
        print(f"  ✓ Concatenated full Sarga: {merged_filepath}")

async def main():
    if not os.path.exists(JSON_PATH):
        print(f"Error: Could not find dataset at {JSON_PATH}")
        return

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        shlokas = json.load(f)

    print(f"--- [Version 4.3 MP3 Generator] Loaded {len(shlokas)} entries ---")

    # Group entries by Sarga
    sarga_groups = {}
    for item in shlokas:
        sarga = item.get("sarga", 1)
        if sarga not in sarga_groups:
            sarga_groups[sarga] = []
        sarga_groups[sarga].append(item)

    START_SARGA = 87

    for sarga_num, verse_list in sarga_groups.items():

        # Fast-skip all Sargas prior to your starting point
        if sarga_num < START_SARGA:
            continue

        raw_kanda = verse_list[0].get("kanda", "ayodhyakanda")
        kanda_folder = re.sub(r'[^a-zA-Z0-9]', '', raw_kanda).lower()
        target_dir = os.path.join(BASE_AUDIO_DIR, kanda_folder)
        os.makedirs(target_dir, exist_ok=True)

        print(f"\nProcessing Sarga {sarga_num} ({len(verse_list)} items)...")

        # Step 1: Generate individual verse MP3s
        for item in verse_list:
            shloka = item.get("shloka", 0)
            raw_text = item.get("explanation") or item.get("translation")
            text_for_tts = clean_text_for_speech(raw_text)

            if not text_for_tts:
                continue

            filename = f"{sarga_num}_{shloka}.mp3"
            filepath = os.path.join(target_dir, filename)

            if os.path.exists(filepath):
                continue

            try:
                await generate_shloka_audio(text_for_tts, filepath)
                print(f"  → Generated verse: {filename}")
            except Exception as e:
                print(f"  ❌ Error generating {filename}: {e}")

        # Step 2: Concatenate all verses into sarga_num.mp3 (e.g. 1.mp3)
        concat_sarga_audio(target_dir, sarga_num, verse_list)

if __name__ == "__main__":
    asyncio.run(main())