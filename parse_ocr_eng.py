import json
import logging
import os
import re

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s'
)


def roman_to_int(roman):
  """Converts Roman numerals (e.g., Canto XIV) to integer Sarga numbers."""
  roman_map = {
      'I': 1,
      'V': 5,
      'X': 10,
      'L': 50,
      'C': 100,
      'D': 500,
      'M': 1000,
      'IV': 4,
      'IX': 9,
      'XL': 40,
      'XC': 90,
      'CD': 400,
      'CM': 900,
  }
  i = 0
  num = 0
  roman = roman.upper().strip()
  while i < len(roman):
    if i + 1 < len(roman) and roman[i : i + 2] in roman_map:
      num += roman_map[roman[i : i + 2]]
      i += 2
    else:
      num += roman_map.get(roman[i], 0)
      i += 1
  return num


def parse_english_ocr(file_path):
  logging.info(f'Processing English OCR text from: {file_path}')

  if not os.path.exists(file_path):
    logging.error(f'File {file_path} not found!')
    return []

  with open(file_path, 'r', encoding='utf-8') as f:
    raw_text = f.read()

  # Split document into Cantos/Sargas
  canto_blocks = re.split(r'\n(?=Canto\s+[IVXLCDM\d]+)', raw_text)
  english_data = []

  for block in canto_blocks:
    canto_match = re.search(r'Canto\s+([IVXLCDM\d]+)', block)
    if not canto_match:
      continue

    canto_raw = canto_match.group(1)
    sarga_num = (
        int(canto_raw) if canto_raw.isdigit() else roman_to_int(canto_raw)
    )

    # Match English paragraphs ending with verse indicators like (1), (1-2), (19—22)
    verse_matches = re.findall(
        r'([A-Z“"][^॥\u0900-\u097F\u0600-\u06FF\u0F00-\u0FFF]+?\((?:\d+|[\d\s\u2013\u2014\-]+)\))',
        block,
        re.DOTALL,
    )

    for vm in verse_matches:
      clean_text = re.sub(r'\s+', ' ', vm).strip()

      # Extract verse range/num in parentheses at the end
      num_match = re.search(r'\(([\d\s\u2013\u2014\-]+)\)$', clean_text)
      if num_match:
        verse_ref = (
            num_match.group(1).replace('—', '-').replace('–', '-').strip()
        )

        english_data.append({
            'kanda': 1,
            'sarga': sarga_num,
            'verse_ref': verse_ref,
            'english': clean_text,
        })

  logging.info(f'Extracted {len(english_data)} English translation blocks.')
  return english_data


# Save English JSON
english_json = parse_english_ocr('B01_ocred.txt')
if english_json:
  with open('balakanda_english.json', 'w', encoding='utf-8') as f:
    json.dump(english_json, f, ensure_ascii=False, indent=2)
  logging.info('🎉 Saved balakanda_english.json successfully!')
