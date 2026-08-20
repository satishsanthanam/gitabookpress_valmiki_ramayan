# smart_audit.py
import json
import os
import re

JSON_FILES = [
    "data/Valmiki_Ramayan_Balakanda.json",
    "data/Valmiki_Ramayan_Ayodhyakanda.json",
    "data/Valmiki_Ramayan_Aranyakanda.json",
    "data/Valmiki_Ramayan_Kishkindhakanda.json",
    "data/Valmiki_Ramayan_Sundarakanda.json",
    "data/Valmiki_Ramayan_Yuddhakanda.json",
    "data/Valmiki_Ramayan_Uttarakanda.json"
]

def smart_audit(filepath):
    if not os.path.exists(filepath):
        return

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    sargas = {}
    for item in data:
        s = item.get("sarga", 1)
        if s not in sargas:
            sargas[s] = []
        sargas[s].append(item)

    print(f"\n==========================================")
    print(f" SMART AUDIT REPORT: {filepath}")
    print(f"==========================================")

    for s_num in sorted(sargas.keys()):
        items = sargas[s_num]
        shloka_nums = [x.get("shloka", 0) for x in items]
        
        # Check ordering
        is_sorted = shloka_nums == sorted(shloka_nums)
        
        # Account for multi-verse spans in explanation e.g. "(5—8)"
        covered_verses = set()
        for item in items:
            sh = item.get("shloka", 0)
            exp = item.get("explanation", "")
            match = re.search(r'\((\d+)\s*[—\-]\s*(\d+)\)', exp)
            if match:
                start_v, end_v = int(match.group(1)), int(match.group(2))
                covered_verses.update(range(start_v, end_v + 1))
            elif sh > 0:
                covered_verses.add(sh)

        actual_max = max(covered_verses) if covered_verses else 0
        missing = [v for v in range(1, actual_max + 1) if v not in covered_verses]

        if not is_sorted or missing:
            print(f"📌 Sarga {s_num}:")
            if not is_sorted:
                print(f"   ⚠️ Out of order! Found order: {shloka_nums[:8]}...")
            if missing:
                print(f"   ❌ Genuine Missing Verses: {missing}")

if __name__ == "__main__":
    for j_file in JSON_FILES:
        smart_audit(j_file)