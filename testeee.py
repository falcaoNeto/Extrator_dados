from docling.document_converter import DocumentConverter
import os

converter = DocumentConverter()
result = converter.convert("Trabalho ES2 (6)_merged_organized (2).pdf")
final = result.document.export_to_markdown()


with open(os.path.join("uploads", "arquivo.txt"), "w") as f:
        f.write(final)