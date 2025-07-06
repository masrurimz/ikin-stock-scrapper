#!/usr/bin/env python3
import fitz  # PyMuPDF

# Read the PDF file
pdf_path = "/Users/masrurimz/Projects/ikin-stock-scrapper/docs/share-buy-back/Public Ownership_Result.pdf"
doc = fitz.open(pdf_path)

# Extract text from all pages
text_content = ""
for page_num in range(len(doc)):
    page = doc.load_page(page_num)
    text_content += page.get_text()

total_pages = len(doc)
doc.close()

print("PDF Content:")
print("="*50)
print(text_content)
print("="*50)
print(f"Total pages: {total_pages}")