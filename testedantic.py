import json
from pydantic import BaseModel, Field, create_model  
from typing import List, Dict, Any

with open('view/notaFiscal.json') as f:
    dadosNotaFiscal = json.load(f)
camposProdutos = {
    dado["description"]: (str, Field(description=dado["description"]))  
    for dado in dadosNotaFiscal[1]
}
DinamicModelProdutos = create_model(    
    "Produtos",
    **camposProdutos
)
camposNotaFiscal = {
    dado["description"]: (str, Field(description=dado["description"]))  
    for dado in dadosNotaFiscal[0]
}
camposNotaFiscal["produtos"] = (List[DinamicModelProdutos], Field(description="Lista de produtos na nota fiscal"))
DinamicModelNotaFiscal = create_model(
    "NotaFiscal",  
    **camposNotaFiscal
)

print(DinamicModelNotaFiscal.__fields__)
print("---------------------------------------------------------------------")
print(DinamicModelProdutos.__fields__)