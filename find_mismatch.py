import json

with open("balakanda_parallel_master.json", "r", encoding="utf-8") as f:
  data = json.load(f)

missing = [
    item["verse_id"] for item in data if not item.get("english", "").strip()
]

print(f"Total Missing English: {len(missing)}")
print("First 20 missing IDs:")
for v_id in missing[:20]:
  print(f"  - {v_id}")

empty_sanskrit = [item["verse_id"] for item in data if not item.get("sanskrit")]
empty_english = [item["verse_id"] for item in data if not item.get("english")]

print(f"Total Verse Records: {len(data)}")
print(f"Missing Sanskrit: {len(empty_sanskrit)}")
print(f"Missing English: {len(empty_english)}")