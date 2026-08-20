import base64
from mistralai.client import Mistral
import os
import glob
import shutil
from pypdf import PdfReader, PdfWriter

api_key = os.environ.get("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)


def split_pdf(input_pdf_path, batch_size=50, output_dir="batches"):
    """Split a PDF into zero-padded batch PDFs (e.g., batch_01.pdf, batch_02.pdf)."""
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than zero")

    reader = PdfReader(input_pdf_path)
    if not reader.pages:
        return 0

    os.makedirs(output_dir, exist_ok=True)
    
    # Clear any old batch files in the output directory
    for existing_file in glob.glob(os.path.join(output_dir, "batch_*.*")):
        os.remove(existing_file)

    total_pages = len(reader.pages)
    total_batches = (total_pages + batch_size - 1) // batch_size

    batch_idx = 1
    for start in range(0, total_pages, batch_size):
        writer = PdfWriter()
        for page in reader.pages[start:start + batch_size]:
            writer.add_page(page)

        # Zero-padded filename generation (e.g. batch_01.pdf, batch_02.pdf)
        batch_filename = f"batch_{batch_idx:02d}.pdf"
        batch_path = os.path.join(output_dir, batch_filename)
        
        with open(batch_path, "wb") as batch_file:
            writer.write(batch_file)

        batch_idx += 1

    return total_batches


def encode_file(file_path):
    with open(file_path, "rb") as pdf_file:
        return base64.b64encode(pdf_file.read()).decode('utf-8')


def process_batch(batch_path, batch_md_out):
    """Process a single PDF batch and save to its OWN individual zero-padded .md file."""
    base64_file = encode_file(batch_path)

    ocr_response = client.ocr.process(
        document={
            "type": "document_url",
            "document_url": f"data:application/pdf;base64,{base64_file}"
        },
        model="mistral-ocr-latest",
        include_image_base64=True,
        include_blocks=True
    )

    # Save to dedicated batch markdown file (e.g., batches/batch_01.md)
    with open(batch_md_out, "w", encoding="utf-8") as f:
        for page in ocr_response.pages:
            if hasattr(page, 'markdown') and page.markdown:
                f.write(page.markdown + "\n\n")

    return len(ocr_response.pages)


def process_all_batches(input_pdf_path, batch_size=50, output_file="06_yuddhakanda.md"):
    """
    Splits the input PDF, processes each batch individually into batch_XX.md,
    and merges all markdown outputs in exact integer order.
    """
    # Step 1: Split PDF into zero-padded batch PDFs
    total_batches = split_pdf(input_pdf_path, batch_size=batch_size)
    print(f"📄 Created {total_batches} PDF batches in 'batches/' directory.")

    # Step 2: Grab and sort PDF batches numerically by integer
    batch_files = sorted(
        glob.glob("batches/batch_*.pdf"),
        key=lambda x: int(os.path.basename(x).split('_')[1].split('.')[0])
    )
    processed_pages = 0

    # Step 3: Run OCR for each batch file
    for i, batch_file in enumerate(batch_files, start=1):
        # Generate target zero-padded markdown path (batches/batch_01.md, batch_02.md, etc.)
        batch_md_out = os.path.join("batches", f"batch_{i:02d}.md")

        # CACHE CHECK: If markdown file exists, skip calling Mistral API
        if os.path.exists(batch_md_out):
            print(f"  ⏭️ Batch {i:02d}/{total_batches:02d} already processed ({batch_md_out}). Skipping API call...")
            continue

        print(f"⚡ Processing batch {i:02d}/{total_batches:02d} ({batch_file})...")
        try:
            pages_processed = process_batch(batch_file, batch_md_out)
            processed_pages += pages_processed
            print(f"  → Saved {batch_md_out} ({pages_processed} pages).")
        except Exception as e:
            print(f"  ❌ Error processing batch {i:02d}: {e}")
            continue

    # Step 4: Merge all batch markdown files in strict numerical order
    print("\n🔗 Merging all batch MD files in exact sequential order...")
    all_md_files = sorted(
        glob.glob("batches/batch_*.md"),
        key=lambda x: int(os.path.basename(x).split('_')[1].split('.')[0])
    )

    with open(output_file, "w", encoding="utf-8") as outfile:
        for md_file in all_md_files:
            print(f"  Appending {md_file}...")
            with open(md_file, "r", encoding="utf-8") as infile:
                outfile.write(infile.read() + "\n\n")

    print(f"✅ Finished! Output written to {output_file}")


def cleanup_batches():
    """Optional utility to delete temporary batch folder."""
    if os.path.exists("batches"):
        shutil.rmtree("batches")
        print("✅ Temporary batch files deleted.")


# --- RUN PIPELINE FOR YUDDHAKANDA ---
# This will keep all intermediate batch_XX.md files in the `batches` folder without cleaning up!
process_all_batches("input.pdf", batch_size=50, output_file="06_yuddhakanda.md")