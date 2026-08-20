import re


def devanagari_to_arabic(dev_str):
  dev_map = {
      '०': '0',
      '१': '1',
      '२': '2',
      '३': '3',
      '४': '4',
      '५': '5',
      '६': '6',
      '७': '7',
      '८': '8',
      '९': '9',
  }
  return ''.join(dev_map.get(char, char) for char in str(dev_str))


def clean_english_tags(match):
  inside = match.group(1)
  clean_inside = re.sub(r'[\s\u2013\u2014\-]+', '-', inside).strip('-')
  return f'({clean_inside})'


def cleanup_ocr_file(
    input_path='B01_ocred.txt', output_path='B01_ocred_clean.txt'
):
  print(f'🧹 Cleaning up OCR file: {input_path}...')

  with open(input_path, 'r', encoding='utf-8') as f:
    ocr_text = f.read()

  # 1. Clean Devanagari verse numbers inside dandas: ॥ ८० ॥ -> ॥ 80 ॥
  def replace_sanskrit_nums(match):
    prefix = match.group(1)
    num_part = match.group(2)
    suffix = match.group(3)
    converted_num = devanagari_to_arabic(num_part)
    return f'{prefix} {converted_num} {suffix}'

  text_clean = re.sub(
      r'([॥।])\s*([\u0966-\u096F\d\s\-\—]+)\s*([॥।])',
      replace_sanskrit_nums,
      ocr_text,
  )

  # 2. Clean English verse tags: ( 19 — 22 ) -> (19-22)
  text_clean = re.sub(
      r'\(\s*([\d\s\u2013\u2014\-]+)\s*\)', clean_english_tags, text_clean
  )

  # 3. Strip page header banners breaking sentences
  text_clean = re.sub(
      r'\*\s*(VÁLMÍKI-RÁMÁYANA|BÁLAKÁNDA|BÄLAKÄNDA|VĀLMĪKI-RĀMĀYANA|BĀLAKĀNDA)\s*\*',
      '',
      text_clean,
      flags=re.IGNORECASE,
  )

  with open(output_path, 'w', encoding='utf-8') as f:
    f.write(text_clean)

  print(f'🎉 Saved sanitized OCR text to: {output_path}')


if __name__ == '__main__':
  cleanup_ocr_file()