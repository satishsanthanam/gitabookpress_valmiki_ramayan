# Version 4.2 - Valmiki Ramayana MP3 Generator (Book/Kanda Subfolder Edition)
# Updates in v4.2:
# - OUTPUT_AUDIO_DIR dynamically creates book subfolders (e.g., "./audio/ramayana/balakanda/")
# - Prevents 1_1.mp3 collisions across different Kandas/Books
# - Normalizes IAST diacritics for smooth TTS pronunciation
# - Cleans verse tags, quotes, footnotes, and page numbers

import os
import json
import asyncio
import re
import unicodedata
import edge_tts

# Inputs
JSON_PATH = "Valmiki_Ramayan_Balakanda.json"
BASE_AUDIO_DIR = "./audio/ramayana/"

# Voice Selection ("en-IN-PrabhatNeural" for Indian Male, "en-IN-NeerjaNeural" for Female)
VOICE = "en-IN-PrabhatNeural"

def convert_iast_to_plain_ascii(text):
    """
    Normalizes IAST diacritics into plain ASCII text for TTS pronunciation.
    e.g., "Vālmīki" -> "Valmiki", "Nārada" -> "Narada", "Śrī Rāma" -> "Sri Rama"
    """
    if not text:
        return ""
    normalized = unicodedata.normalize('NFD', text)
    plain_text = "".join(c for c in normalized if unicodedata.category(c) != 'Mn')
    return plain_text

def clean_text_for_speech(text):
    """
    Strips IAST diacritics, trailing verse numbers, quotes, and footnotes.
    """
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

async def main():
    if not os.path.exists(JSON_PATH):
        print(f"Error: Could not find dataset at {JSON_PATH}")
        return

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        shlokas = json.load(f)

    print(f"--- [Version 4.2 MP3 Generator] Loaded {len(shlokas)} shlokas ---")

    for index, item in enumerate(shlokas, 1):
        # Determine book/kanda subfolder (e.g. "Bala Kanda" -> "balakanda")
        raw_kanda = item.get("kanda", "balakanda")
        kanda_folder = re.sub(r'[^a-zA-Z0-9]', '', raw_kanda).lower()
        
        # Target output directory: ./audio/ramayana/balakanda/
        target_dir = os.path.join(BASE_AUDIO_DIR, kanda_folder)
        os.makedirs(target_dir, exist_ok=True)

        sarga = item.get("sarga", 1)
        shloka = item.get("shloka", 1)
        raw_text = item.get("explanation") or item.get("translation")
        
        text_for_tts = clean_text_for_speech(raw_text)

        if not text_for_tts:
            continue

        filename = f"{sarga}_{shloka}.mp3"
        filepath = os.path.join(target_dir, filename)

        if os.path.exists(filepath):
            print(f"[{index}/{len(shlokas)}] Skipped (already exists): {filepath}")
            continue

        try:
            await generate_shloka_audio(text_for_tts, filepath)
            print(f"[{index}/{len(shlokas)}] Generated: {filepath}")
        except Exception as e:
            print(f"Error generating {filepath}: {e}")

if __name__ == "__main__":
    asyncio.run(main())