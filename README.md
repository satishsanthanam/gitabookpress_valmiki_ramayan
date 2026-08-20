# Vālmīki Rāmāyaṇa Digital Dataset

A structured, production-ready digital compilation of the **Vālmīki Rāmāyaṇa** epic, standardized into structured JSON and CSV formats. Designed for developer integration, machine translation pipelines, search indexing, and audio-text synchronization.

---

## 📌 Project Overview

This repository contains the complete text of the Vālmīki Rāmāyaṇa split across its 7 Kāṇḍas (books). Each entry captures the exact Sanskrit Shloka alongside its corresponding prose gloss/commentary, structured into clean machine-readable schemas.

### Key Features
* **Complete Coverage:** Includes all 7 Kāṇḍas of the Vālmīki Rāmāyaṇa.
* **Standardized Schema:** Every record contains exact Kāṇḍa titles, Shloka/Verse indexing, original Sanskrit text, and commentary.
* **Dual Format Support:** Maintained in both `.json` and `.csv` formats for seamless use in database seeds, web/mobile APIs, and data science workflows.
* **Translation-Ready:** Cleaned of OCR noise, running page headers, and stray artifacts, making it optimized for LLM batch translations (Claude, Gemini, OpenAI).

---

## 🗂️ Dataset Structure

```text
valmiki-ramayana/
├── json/
│   ├── 01_balakanda.json
│   ├── 02_ayodhyakanda.json
│   ├── 03_aranyakanda.json
│   ├── 04_kishkindhakanda.json
│   ├── 05_sundarakanda.json
│   ├── 06_lankakanda.json
│   └── 07_uttarakanda.json
├── csv/
│   ├── 01_balakanda.csv
│   ├── 02_ayodhyakanda.csv
│   ├── 03_aranyakanda.csv
│   ├── 04_kishkindhakanda.csv
│   ├── 05_sundarakanda.csv
│   ├── 06_lankakanda.csv
│   └── 07_uttarakanda.csv
├── scripts/
│   └── pipeline_helpers.py
└── README.md

```

---

## 📄 Data Schema

### JSON Format

Each Kāṇḍa is structured as an array of verse objects:

```json
[
  {
    "kanda": "Bala Kanda",
    "sarga": "1",
    "verse_index": "1",
    "sanskrit_shloka": "तपःस्वाध्यायनिरतं तपस्वी वाग्विदां वरम् ।\nनारदं परिपप्रच्छ वाल्मीकिर्मुनिपुंगवम् ॥ १ ॥",
    "meaning": "Ascetic Valmiki asked Narada, the preeminent among the eloquent, who was ever engaged in austerity and self-study..."
  }
]

```

### CSV Fields

| Field Name | Type | Description |
| --- | --- | --- |
| `kanda` | String | Name of the Kāṇḍa (e.g., *Bala Kanda*, *Sundara Kanda*) |
| `sarga` | String/Int | Sarga (Chapter) number |
| `verse_index` | String/Int | Shloka / Verse number within the Sarga |
| `sanskrit_shloka` | String | Original Sanskrit verse text in Devanagari script |
| `meaning` | String | Corresponding prose meaning or commentary |

---

## 🚀 Usage & Integration

### Python Example: Loading Data

```python
import json
import pandas as pd

# Load JSON
with open("json/05_sundarakanda.json", "r", encoding="utf-8") as f:
    sundara_kanda = json.load(f)

print(f"Loaded {len(sundara_kanda)} verses from Sundara Kanda.")

# Load CSV via Pandas
df = pd.read_csv("csv/01_balakanda.csv")
print(df.head())

```

---

## 🗺️ Roadmap & Future Phases

* [x] OCR extraction and initial markdown generation.
* [x] Structural dataset parsing and schema normalization.
* [ ] English translation pipeline integration.
* [ ] Multi-language commentary alignment (Hindi, Tamil, Telugu).
* [ ] Audio pairing and MP3 timing alignment for verse playback.
* [ ] Outstanding issues documented in errors_to_fix.xlsx
---

## 📜 License & Credits

* **Text Source:** Derived from classical Vālmīki Rāmāyaṇa texts.
* **OCR & Digitization:** Initial document processing, text extraction, and Markdown OCR generation powered by **Mistral AI** OCR services.  ref (process_pdf_via_batch_mistral_api.py)
* **License:** Distributed under the [MIT License](https://www.google.com/search?q=LICENSE) for open-source educational, devotional, and developer use.

```

```