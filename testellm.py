from docling.document_converter import DocumentConverter
from contaAgua import ExtrairDados


converter = DocumentConverter()
result = converter.convert("deso.pdf")
result2 = result.document.export_to_markdown()


Extrai = ExtrairDados(result2)
result3 = Extrai.extrair_conta_agua()
print(type(result3))
print("---------------------------------------------------------------------")
print(result3)

