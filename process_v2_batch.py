import base64
from mistralai.client import Mistral
import os
import json
import shutil
import glob
from pypdf import PdfReader, PdfWriter

api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)

BATCHES_DIR = "batches"

def split_pdf(input_pdf_path, batch_size=50, output_dir=BATCHES_DIR):
    """Split a PDF into batches if they don't already exist."""
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than zero")

    reader = PdfReader(input_pdf_path)
    if not reader.pages:
        return 0

    os.makedirs(output_dir, exist_ok=True)
    
    # Check if batches already exist
    existing_pdfs = glob.glob(os.path.join(output_dir, "batch_*.pdf"))
    if existing_pdfs:
        print(f"ℹ️ Found {len(existing_pdfs)} existing PDF batches in '{output_dir}/'. Skipping split.")
        return len(existing_pdfs)

    total_batches = 0
    for start in range(0, len(reader.pages), batch_size):
        writer = PdfWriter()
        for page in reader.pages[start:start + batch_size]:
            writer.add_page(page)

        total_batches += 1
        batch_path = os.path.join(output_dir, f"batch_{total_batches}.pdf")
        with open(batch_path, "wb") as batch_file:
            writer.write(batch_file)

    print(f"✅ Split PDF into {total_batches} batch files.")
    return total_batches


def encode_file(file_path):
    with open(file_path, "rb") as pdf_file:
        return base64.b64encode(pdf_file.read()).decode('utf-8')


def process_batch(batch_pdf_path, batch_md_path):
    """Process a single PDF batch and save OCR output directly to its own .md file."""
    base64_file = encode_file(batch_pdf_path)

    ocr_response = client.ocr.process(
        document={
            "type": "document_url",
            "document_url": f"data:application/pdf;base64,{base64_file}"
        },
        model="mistral-ocr-latest",
        include_image_base64=True,
        include_blocks=True
    )

    with open(batch_md_path, "w", encoding="utf-8") as f:
        for page in ocr_response.pages:
            if hasattr(page, 'markdown') and page.markdown:
                f.write(page.markdown + "\n\n")

    return len(ocr_response.pages)


def concat_batches(batches_dir=BATCHES_DIR, final_output_file="output.md"):
    """Concatenate all individual batch_*.md files into a single output file."""
    md_files = sorted(
        glob.glob(os.path.join(batches_dir, "batch_*.md")),
        key=lambda x: int(re.search(r'batch_(\d+)\.md', x).group(1)) if re.search(r'batch_(\d+)\.md', x) else 0
    )

    if not md_files:
        print("⚠️ No batch .md files found to concatenate.")
        return

    print(f"\n🔗 Concatenating {len(md_files)} Markdown batch files into '{final_output_file}'...")
    with open(final_output_file, "w", encoding="utf-8") as outfile:
        for md_file in md_files:
            with open(md_file, "r", encoding="utf-8") as infile:
                outfile.write(infile.read() + "\n\n")
            print(f"  → Merged: {os.path.basename(md_file)}")

    print(f"✅ Concatenation complete! Final combined file: {final_output_file}")


def process_all_batches(input_pdf_path, batch_size=50, final_output_file="output.md"):
    """Process all batches into individual .md files and concatenate them upon completion."""
    # Step 1: Split PDF into batches
    total_batches = split_pdf(input_pdf_path, batch_size=batch_size)

    # Step 2: Process each PDF batch into its own batch_N.md file
    processed_pages = 0
    failed_batches = []

    for i in range(1, total_batches + 1):
        batch_pdf = os.path.join(BATCHES_DIR, f"batch_{i}.pdf")
        batch_md = os.path.join(BATCHES_DIR, f"batch_{i}.md")

        # Skip if batch_N.md already exists (e.g. from previous successful run)
        if os.path.exists(batch_md) and os.path.getsize(batch_md) > 0:
            print(f"Processing batch {i}/{total_batches}...")
            print(f"  ⏩ Skipping batch {i}: '{batch_md}' already exists.")
            continue

        print(f"Processing batch {i}/{total_batches}...")
        try:
            pages_processed = process_batch(batch_pdf, batch_md)
            processed_pages += pages_processed
            print(f"  → Saved: {batch_md} ({pages_processed} pages)")
        except Exception as e:
            print(f"  ❌ Error processing batch {i}: {e}")
            failed_batches.append(i)

    # Step 3: Automatically Concatenate all batch_N.md files
    concat_batches(batches_dir=BATCHES_DIR, final_output_file=final_output_file)

    if failed_batches:
        print(f"\n⚠️ Note: Batches {failed_batches} failed. Fix API errors and re-run this script to automatically retry only the failed batches.")
    else:
        print("\n🎉 All batches processed and combined successfully!")


def cleanup_batches(batches_dir=BATCHES_DIR):
    """Deletes temporary batches folder."""
    if os.path.exists(batches_dir):
        shutil.rmtree(batches_dir)
        print("✅ Temporary batch files deleted.")


# Example execution
if __name__ == "__main__":
    import re
    process_all_batches("input.pdf", batch_size=50, final_output_file="output.md")