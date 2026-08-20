# Script: concat_sargas.py
# Purpose: Merge 1_0.mp3, 1_1.mp3, 1_2.mp3... into 1.mp3 for full Sarga streaming

import os
import json
import re
from pydub import AudioSegment

CONFIGS = [
    ("Valmiki_Ramayan_Balakanda.json", "./audio/ramayana/balakanda/")
]

def concat_sargas():
    for json_file, target_dir in CONFIGS:
        if not os.path.exists(json_file):
            print(f"⚠️ Dataset {json_file} not found. Skipping...")
            continue

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Group items by Sarga
        sarga_map = {}
        for item in data:
            sarga = item.get("sarga", 1)
            if sarga not in sarga_map:
                sarga_map[sarga] = []
            sarga_map[sarga].append(item)

        print(f"\n--- Processing Sarga Concatenation for {json_file} ---")

        for sarga_num, items in sarga_map.items():
            merged_filename = f"{sarga_num}.mp3"
            merged_filepath = os.path.join(target_dir, merged_filename)

            if os.path.exists(merged_filepath):
                print(f"  ⏩ Skipping Sarga {sarga_num}: '{merged_filename}' already exists.")
                continue

            combined_audio = AudioSegment.empty()
            # Sort so shloka 0 (Summary) comes first, followed by 1, 2, 3...
            sorted_items = sorted(items, key=lambda x: x.get("shloka", 0))

            for item in sorted_items:
                shloka = item.get("shloka", 0)
                verse_file = os.path.join(target_dir, f"{sarga_num}_{shloka}.mp3")

                if os.path.exists(verse_file):
                    verse_audio = AudioSegment.from_mp3(verse_file)
                    combined_audio += verse_audio
                    # Add a 400ms pause between verses
                    combined_audio += AudioSegment.silent(duration=400)
                else:
                    print(f"  ⚠️ Warning: Missing audio file {verse_file}")

            if len(combined_audio) > 0:
                combined_audio.export(merged_filepath, format="mp3", bitrate="128k")
                print(f"  ✓ Concatenated Sarga {sarga_num} -> {merged_filepath}")

if __name__ == "__main__":
    concat_sargas()