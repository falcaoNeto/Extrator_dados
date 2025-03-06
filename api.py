from fastapi import FastAPI, File, UploadFile, Request
import os
import tempfile
from classificar import Classificar
from notaFiscal import NotaFiscal
from contaAgua import ContaAgua
from teste.teste2 import LangChainOllamaChain
from docling.document_converter import DocumentConverter
import json 
import io
from extrairFoto import extrair_texto_da_foto
from typing import List


app = FastAPI()




@app.post("/uploadPhoto")
async def upload_photo(file: UploadFile = File(...)):
    print(file)
    image_bytes = await file.read()

    
    textoresult = extrair_texto_da_foto(image_bytes)


    result_classificar = Classificar(textoresult).classificar_texto()
    
    if result_classificar == "NotaFiscal":
        result_extrair = NotaFiscal(textoresult).extrair_nota_fiscal()
        if os.path.exists("BD/NotaFiscalBD.json") and os.path.getsize("BD/NotaFiscalBD.json") > 0:
            with(open("BD/NotaFiscalBD.json", "r+")) as f:
                    dados = json.load(f)
                    dados.append(result_extrair)
                    f.seek(0)
                    json.dump(dados, f, ensure_ascii=False, indent=2)
            
        else:
            with open("BD/NotaFiscalBD.json", "w", encoding="utf-8") as f:
                json.dump([result_extrair], f, ensure_ascii=False, indent=2)
        return result_extrair
        
    elif result_classificar == "ContaAgua":
        result_extrair = ContaAgua(textoresult).extrair_conta_agua()
        if os.path.exists("BD/ContaAguaBD.json") and os.path.getsize("BD/ContaAguaBD.json") > 0:
            with(open("BD/ContaAguaBD.json", "r+")) as f:
                    dados = json.load(f)
                    dados.append(result_extrair)
                    f.seek(0)
                    json.dump(dados, f, ensure_ascii=False, indent=2)
            
        else:
            with open("BD/ContaAguaBD.json", "w", encoding="utf-8") as f:
                json.dump([result_extrair], f, ensure_ascii=False, indent=2)
        return result_extrair
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
        textoImagem = NotaFiscal(textoImagem).extrair_nota_fiscal()
        if os.path.exists("BD/NotaFiscalBD.json") and os.path.getsize("BD/NotaFiscalBD.json") > 0:
            with(open("BD/NotaFiscalBD.json", "r+")) as f:
                    dados = json.load(f)
                    dados.append(textoImagem)
                    f.seek(0)
                    json.dump(dados, f, ensure_ascii=False, indent=2)
        else:
            with open("BD/NotaFiscalBD.json", "w", encoding="utf-8") as f:
                json.dump([textoImagem], f, ensure_ascii=False, indent=2)
        
        return textoImagem
        
    elif result_classificar == "ContaAgua":
        textoImagem = ContaAgua(textoImagem).extrair_conta_agua()
        if os.path.exists("BD/ContaAguaBD.json") and os.path.getsize("BD/ContaAguaBD.json") > 0:
            with(open("BD/ContaAguaBD.json", "r+")) as f:
                    dados = json.load(f)
                    dados.append(textoImagem)
                    f.seek(0)
                    json.dump(dados, f, ensure_ascii=False, indent=2)
        else:
            with open("BD/ContaAguaBD.json", "w", encoding="utf-8") as f:
                json.dump([textoImagem], f, ensure_ascii=False, indent=2)
        
        return textoImagem
    else:
        textoImagem = "NenhumOutro"



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
        result_extrair = NotaFiscal(textoresult).extrair_nota_fiscal()
        if os.path.exists("BD/NotaFiscalBD.json") and os.path.getsize("BD/NotaFiscalBD.json") > 0:
            with(open("BD/NotaFiscalBD.json", "r+")) as f:
                    dados = json.load(f)
                    dados.append(result_extrair)
                    f.seek(0)
                    json.dump(dados, f, ensure_ascii=False, indent=2)
        else:
            with open("BD/NotaFiscalBD.json", "w", encoding="utf-8") as f:
                json.dump([result_extrair], f, ensure_ascii=False, indent=2)
        
        return result_extrair
        
    elif result_classificar == "ContaAgua":
        result_extrair = ContaAgua(textoresult).extrair_conta_agua()
        if os.path.exists("BD/ContaAguaBD.json") and os.path.getsize("BD/ContaAguaBD.json") > 0:
            with(open("BD/ContaAguaBD.json", "r+")) as f:
                    dados = json.load(f)
                    dados.append(result_extrair)
                    f.seek(0)
                    json.dump(dados, f, ensure_ascii=False, indent=2)
        else:
            with open("BD/ContaAguaBD.json", "w", encoding="utf-8") as f:
                json.dump([result_extrair], f, ensure_ascii=False, indent=2)
        
        return result_extrair
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




import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)