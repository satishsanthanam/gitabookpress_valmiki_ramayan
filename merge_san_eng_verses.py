import json
import logging
import os
import re

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)


def roman_to_int(roman):
  roman_map = {
      "I": 1,
      "V": 5,
      "X": 10,
      "L": 50,
      "C": 100,
      "D": 500,
      "M": 1000,
      "IV": 4,
      "IX": 9,
      "XL": 40,
      "XC": 90,
      "CD": 400,
      "CM": 900,
  }
  i, num, roman = 0, 0, roman.upper().strip()
  while i < len(roman):
    if i + 1 < len(roman) and roman[i : i + 2] in roman_map:
      num += roman_map[roman[i : i + 2]]
      i += 2
    else:
      num += roman_map.get(roman[i], 0)
      i += 1
  return num


def clean_header_noise(text):
  text = re.sub(
      r"\*\s*(VÁLMÍKI-RÁMÁYANA|BÁLAKÁNDA|BÄLAKÄNDA|VĀLMĪKI-RĀMĀYANA|BĀLAKĀNDA)\s*\*",
      "",
      text,
      flags=re.IGNORECASE,
  )
  return text.strip()


def build_master_from_ocr_only(
    ocr_path="B01_ocred_clean.txt",
    output_json_path="balakanda_parallel_master.json",
):
  if not os.path.exists(ocr_path):
    logging.error(f"❌ File not found: {ocr_path}")
    return

  logging.info(f"📖 Parsing single-source file: {ocr_path}")
  with open(ocr_path, "r", encoding="utf-8") as f:
    raw_text = f.read()

  canto_blocks = re.split(r"\n(?=Canto\s+[IVXLCDM\d]+)", raw_text)
  master_data = []

  for block in canto_blocks:
    canto_match = re.search(r"Canto\s+([IVXLCDM\d]+)", block)
    if not canto_match:
      continue

    canto_raw = canto_match.group(1)
    sarga_num = (
        int(canto_raw) if canto_raw.isdigit() else roman_to_int(canto_raw)
    )

    logging.info(f"⚡ Processing Sarga {sarga_num}...")

    # Split canto into blocks separated by blank lines
    chunks = re.split(r"\n\s*\n", block)

    sans_buffer = []

    for chunk in chunks:
      chunk_clean = clean_header_noise(chunk.strip())
      if not chunk_clean:
        continue

      # Check if chunk contains Devanagari Sanskrit text
      if re.search(r"[\u0900-\u097F]", chunk_clean):
        sans_buffer.append(chunk_clean)
        continue

      # Check if chunk is an English translation ending with verse tag (e.g. (1) or (19-22))
      eng_tag_match = re.search(
          r"\(\s*([\d\s\u2013\u2014\-]+)\s*\)\s*$", chunk_clean
      )

      if eng_tag_match and sans_buffer:
        v_ref = (
            eng_tag_match.group(1)
            .replace("—", "-")
            .replace("–", "-")
            .replace(" ", "")
            .strip("-")
        )

        combined_sanskrit = "\n\n".join(sans_buffer)
        clean_eng = re.sub(r"\s+", " ", chunk_clean).strip()

        master_data.append({
            "kanda": 1,
            "sarga": sarga_num,
            "verse": v_ref,
            "verse_id": f"1.{sarga_num}.{v_ref}",
            "sanskrit": combined_sanskrit,
            "english": clean_eng,
        })

        # Clear buffer for next verse unit
        sans_buffer = []

  with open(output_json_path, "w", encoding="utf-8") as f:
    json.dump(master_data, f, ensure_ascii=False, indent=2)

  logging.info(
      f"🎉 SUCCESS! Extracted {len(master_data)} entries into {output_json_path}"
  )


if __name__ == "__main__":
  build_master_from_ocr_only()