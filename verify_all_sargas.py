import os
import re

# Official Sarga/Canto counts for Valmiki Ramayan
KANDA_EXPECTED_COUNTS = {
    "balakanda_mistral_ocr.md": {"name": "Bala Kanda", "expected": 77},
    "ayodhyakanda_mistral_ocr.md": {"name": "Ayodhya Kanda", "expected": 119},
    "aranyakanda_mistral_ocr.md": {"name": "Aranya Kanda", "expected": 75},
    "kishkindhakanda_mistral_ocr.md": {"name": "Kishkindha Kanda", "expected": 67},
    "sundarakanda_mistral_ocr.md": {"name": "Sundara Kanda", "expected": 68},
    "yuddhakanda_mistral_ocr.md": {"name": "Yuddha Kanda", "expected": 128},
    "uttarakanda_mistral_ocr.md": {"name": "Uttara Kanda", "expected": 111},
}

def roman_to_int(s):
    """Convert Roman numerals to integers, handling minor OCR typos."""
    s = s.upper().strip()
    s = s.replace('L', 'I').replace('1', 'I') if s == 'CL' else s  # Fix OCR Cl -> CI
    if s.isdigit():
        return int(s)
    
    roman_map = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    result = 0
    for i in range(len(s)):
        if i > 0 and roman_map.get(s[i], 0) > roman_map.get(s[i - 1], 0):
            result += roman_map[s[i]] - 2 * roman_map[s[i - 1]]
        else:
            result += roman_map.get(s[i], 0)
    return result

def verify_file(filename, info):
    if not os.path.exists(filename):
        print(f"❌ File not found: {filename}")
        return

    with open(filename, "r", encoding="utf-8") as f:
        text = f.read()

    # Pre-clean known OCR typos (e.g. Canto Cl -> Canto CI)
    text = re.sub(r'Canto\s+Cl\b', 'Canto CI', text, flags=re.IGNORECASE)
    text = re.sub(r'Canto\s+C\s+I\b', 'Canto CI', text, flags=re.IGNORECASE)

    # 1. Match English Canto headers: "Canto XVIII", "Canto 18", "Canto CI"
    english_cantos = re.findall(r'Canto\s*([IVXLCDM\d]+)', text, re.IGNORECASE)
    
    # 2. Match Devanagari Sarga end-markers: "सर्गः ॥ १८ ॥" or "सर्गः ॥ १ ॥"
    sanskrit_cantos = re.findall(r'सर्गः\s*॥\s*(\d+)\s*॥', text)

    # Combine all found canto numbers
    found_nums = set()
    for c in english_cantos:
        val = roman_to_int(c)
        if 1 <= val <= info["expected"]:
            found_nums.add(val)

    for c in sanskrit_cantos:
        val = int(c)
        if 1 <= val <= info["expected"]:
            found_nums.add(val)

    expected_set = set(range(1, info["expected"] + 1))
    missing = expected_set - found_nums

    print(f"📖 {info['name']} ({filename})")
    print(f"   Detected: {len(found_nums)} / {info['expected']} Cantos")
    
    if not missing:
        print(f"   ✅ PERFECT MATCH! All {info['expected']} Cantos are verified.")
    else:
        print(f"   ⚠️ MISSING CANTOS: {sorted(list(missing))}")
    print("-" * 60)

# Run verification across all 7 Kanda files
print("=" * 60)
print("VALMIKI RAMAYAN - FULL DATASET VERIFICATION")
print("=" * 60)

for file_name, meta in KANDA_EXPECTED_COUNTS.items():
    verify_file(file_name, meta)