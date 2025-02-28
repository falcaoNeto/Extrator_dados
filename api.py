from fastapi import FastAPI, File, UploadFile, Request
import os
import tempfile
from classificar import Classificar
from notaFiscal import NotaFiscal
from contaAgua import ContaAgua
from teste.teste2 import LangChainOllamaChain



app = FastAPI()



@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(await file.read())  
        temp_pdf_path = temp_pdf.name

    result_classificar = Classificar.classificar_texto(temp_pdf_path)
    if result_classificar == "NotaFiscal":
        result_extrair = NotaFiscal.extrair_nota_fiscal(temp_pdf_path)
    elif result_classificar == "ContaAgua":
        result_extrair = ContaAgua.extrair_conta_agua(temp_pdf_path)
    else:
        result_extrair = "NenhumOutro"
    

    
    

@app.post("/response")
async def response(request: Request):
    # data = json.loads(json_question)
    json_body = await request.json()        
    
    
    message_content = json_body.get("message")

    with open(os.path.join("uploads", "arquivo.txt"), "r") as f:
        content = f.read()
    
    print(11)
    chain = LangChainOllamaChain(mini_texto=content)
    result = chain.perguntar(message_content)
    print(result)
    
    return result
