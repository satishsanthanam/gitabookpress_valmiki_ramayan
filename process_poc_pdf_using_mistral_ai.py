import base64
import os
import json
from mistralai.client import Mistral

api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)

def encode_file(file_path):
    with open(file_path, "rb") as pdf_file:
        return base64.b64encode(pdf_file.read()).decode('utf-8')

file_path = "./input.pdf"
base64_file = encode_file(file_path)

ocr_response = client.ocr.process(
    document={
        "type": "document_url",
        "document_url": f"data:application/pdf;base64,{base64_file}"
    },
    model="mistral-ocr-latest",
    include_image_base64=True,
    include_blocks=True
)

# Extract markdown from each page and combine into a single string
markdown_content = ""
for page in ocr_response.pages:
    if hasattr(page, 'markdown') and page.markdown:
        markdown_content += page.markdown + "\n\n"

# Save to a markdown file
with open("output.md", "w", encoding="utf-8") as f:
    f.write(markdown_content.strip())  # Remove trailing whitespace

print(f"OCR results saved to output.md. Total pages processed: {len(ocr_response.pages)}")
