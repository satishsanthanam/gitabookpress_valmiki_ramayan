from pypdf import PdfReader, PdfWriter
import os

def split_pdf(input_pdf_path, output_dir="batches", batch_size=50):
    """Split a PDF into smaller batches of `batch_size` pages."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    reader = PdfReader(input_pdf_path)
    total_pages = len(reader.pages)
    batch_num = 1

    for start_page in range(0, total_pages, batch_size):
        end_page = min(start_page + batch_size, total_pages)
        writer = PdfWriter()

        for page_num in range(start_page, end_page):
            writer.add_page(reader.pages[page_num])

        batch_filename = f"{output_dir}/batch_{batch_num}.pdf"
        with open(batch_filename, "wb") as batch_file:
            writer.write(batch_file)

        print(f"Created batch {batch_num}: pages {start_page + 1}-{end_page}")
        batch_num += 1

    return batch_num - 1  # Total number of batches

# Example usage:
# split_pdf("input.pdf", batch_size=25)
