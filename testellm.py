from docling.document_converter import DocumentConverter
from contaAgua import ContaAgua
from classificar import Classificar
import json


converter = DocumentConverter()
result = converter.convert("AGUA FEV.pdf")
result2 = result.document.export_to_dict()

with open("arquivooo.json", "w", encoding="utf-8") as f:
    json.dump(result2, f, ensure_ascii=False, indent=2)
print(result2)
# result = Classificar(result2)
# result2 = result.classificar_texto()
# Extrai = ContaAgua(result2)
# result3 = Extrai.extrair_conta_agua()
# print(type(result3))
# print("---------------------------------------------------------------------")
# print(result3)

