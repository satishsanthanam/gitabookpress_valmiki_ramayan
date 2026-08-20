import glob
import os
import re

# 1. Collect all batch markdown files
all_mds = glob.glob("batches/yuddakanda/batch_*.md")

# 2. Sort by INTEGER value (1, 2, 3 ... 10, 11, 12)
sorted_mds = sorted(
    all_mds,
    key=lambda x: int(re.search(r'batch_(\d+)', x).group(1))
)

print("Merging in this exact order:")
for f in sorted_mds:
    print(f" - {f}")

# 3. Write out the sequentially correct Yuddhakanda file
with open("06_yuddhakanda_fixed.md", "w", encoding="utf-8") as outfile:
    for md_file in sorted_mds:
        with open(md_file, "r", encoding="utf-8") as infile:
            outfile.write(infile.read() + "\n\n")

print("✅ Re-merged into 06_yuddhakanda_fixed.md successfully!")