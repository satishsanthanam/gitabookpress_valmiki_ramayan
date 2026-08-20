import re

def normalize_and_verify(md_file_path):
    with open(md_file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Normalize non-standard OCR Roman numerals to standard ones
    # Fixes LXXXXVII / Lxxxxvii -> XCVII, LXXXX -> XC, etc.
    replacements = {
        r'LXXXXVII': 'XCVII',
        r'LXXXXVI': 'XCVI',
        r'LXXXXV': 'XCV',
        r'LXXXXIV': 'XCIV',
        r'LXXXXIII': 'XCIII',
        r'LXXXXII': 'XCII',
        r'LXXXXI': 'XCI',
        r'LXXXX': 'XC',
        r'XXXX': 'XL',
        r'VIIII': 'IX',
        r'IIII': 'IV',
    }

    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # Save cleaned text back to the file
    with open(md_file_path, "w", encoding="utf-8") as f:
        f.write(text)

    print("✅ Normalized non-standard Roman numerals in file!")

# Clean Uttara Kanda file
normalize_and_verify("uttarakanda_mistral_ocr.md")