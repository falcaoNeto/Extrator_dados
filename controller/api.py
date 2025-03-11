from fastapi import FastAPI, File, UploadFile, Request
import tempfile
from model.classificar import Classificar
from model.notaFiscal import NotaFiscal
from model.contaAgua import ContaAgua
from docling.document_converter import DocumentConverter
from model.extrairFoto import extrair_texto_da_foto
from typing import List
from model.agentsql import Agent

app = FastAPI()

@app.post("/uploadPhoto")
async def upload_photo(file: UploadFile = File(...)):
    print(file)
    image_bytes = await file.read()

    
    textoresult = extrair_texto_da_foto(image_bytes)


    result_classificar = Classificar(textoresult).classificar_texto()
    
    if result_classificar == "NotaFiscal":
        extrair = NotaFiscal()
        result_extrair = extrair.extrair_nota_fiscal(textoresult)
        confirm = extrair.salvar_nota_fiscal(result_extrair)
        if confirm:
            return result_extrair
        else:
            return "Falha ao salvar"    
        
    elif result_classificar == "ContaAgua":
        conta_agua = ContaAgua()
        dados = conta_agua.extrair_conta_agua(textoresult)
        confimar = conta_agua.salvar_conta_agua(dados)

        if confimar:
            return result_extrair
        else:
           return "Falha ao salvar"    
    else:
        result_extrair = "NenhumOutro"

    
@app.post("/uploadPhotos")
async def upload_photos(files: List[UploadFile] = File(...)):
    textoImagem = ""
    for file in files:
        bytes_img = await file.read()
        textoresult = extrair_texto_da_foto(bytes_img)

        if len(textoImagem) == 0:
            textoImagem = textoresult
        else:
            textoImagem += "\n" + textoresult  # Agora está acumulando corretamente os textos

    print(textoImagem)
    result_classificar = Classificar(textoImagem).classificar_texto()
    
    if result_classificar == "NotaFiscal":
        extrair = NotaFiscal()
        result_extrair = extrair.extrair_nota_fiscal(textoImagem)
        confirm = extrair.salvar_nota_fiscal(result_extrair)
        if confirm:
            return result_extrair
        else:
            return "Falha ao salvar"    
        
    elif result_classificar == "ContaAgua":
        conta_agua = ContaAgua()
        result_extrair = conta_agua.extrair_conta_agua(textoImagem)
        confimar = conta_agua.salvar_conta_agua(result_extrair)

        if confimar:
            return result_extrair
        else:
           return "Falha ao salvar"    
    else:
        result_extrair = "NenhumOutro"


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(await file.read())  
        temp_pdf_path = temp_pdf.name

    converter = DocumentConverter()
    result = converter.convert(temp_pdf_path)
    textoresult = result.document.export_to_dict()
    
    result_classificar = Classificar(textoresult).classificar_texto()
    
    if result_classificar == "NotaFiscal":
        extrair = NotaFiscal()
        result_extrair = extrair.extrair_nota_fiscal(textoresult)
        confirm = extrair.salvar_nota_fiscal(result_extrair)
        if confirm:
            return result_extrair
        else:
            return "Falha ao salvar"    
        
    elif result_classificar == "ContaAgua":
        conta_agua = ContaAgua()
        result_extrair = conta_agua.extrair_conta_agua(textoresult)
        confimar = conta_agua.salvar_conta_agua(result_extrair)

        if confimar:
            return result_extrair
        else:
           return "Falha ao salvar"    
    else:
        result_extrair = "NenhumOutro"


@app.post("/response")
async def response(request: Request):
    data = await request.json() 
    message = data.get("message")
    agent = Agent()
    response = agent.agent_response(message)
    print(response)
    return {"response": response}



import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)