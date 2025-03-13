from fastapi import FastAPI, File, UploadFile, Request
import tempfile
from model.classificar import Classificar
from model.notaFiscal import NotaFiscal
from model.contaAgua import ContaAgua
from docling.document_converter import DocumentConverter
from model.extrairFoto import extrair_texto_da_foto
from typing import List
from model.agentsql import Agent
from model.atrDinamicos import JsonDocumentManager

app = FastAPI()
json_manager = JsonDocumentManager(base_path="model")

# Rota que recebe Uma foto
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

# Rota que recebe 2 ou mais fotos
@app.post("/uploadPhotos")
async def upload_photos(files: List[UploadFile] = File(...)):
    textoImagem = ""
    for file in files:
        bytes_img = await file.read()
        textoresult = extrair_texto_da_foto(bytes_img)

        if len(textoImagem) == 0:
            textoImagem = textoresult
        else:
            textoImagem += "\n" + textoresult  

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

# Rota que recebe um PDF
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

# Rota para responder as perguntas usando um AgentSQL
@app.post("/response")
async def response(request: Request):
    data = await request.json() 
    message = data.get("message")
    agent = Agent()
    response = agent.agent_response(message)
    print(response)
    return {"response": response}


# Rotas para CRUD dos dados dinamicos de ContaAgua e NotaFiscal
@app.get("/GetAtrAgua")
async def get_atributos_agua():
    """Retorna todos os atributos da conta de água"""
    try:
        return json_manager.load_data('agua')
    except Exception as e:
        return {"error": str(e)}, 500

@app.post("/AddAtrAgua")
async def add_atributo_agua(request: Request):
    """Adiciona um novo atributo à conta de água"""
    data = await request.json()
    try:
        new_attr = json_manager.add_attribute('agua', data.get("description"))
        return new_attr
    except Exception as e:
        return {"error": str(e)}, 400

@app.post("/RemoveAtrAgua")
async def remove_atributo_agua(request: Request):
    """Remove um atributo da conta de água pelo index"""
    data = await request.json()
    try:
        removed = json_manager.remove_attribute('agua', data.get("index"))
        return removed if removed else {"error": "Atributo não encontrado"}, 404
    except Exception as e:
        return {"error": str(e)}, 400


@app.get("/GetAtrNotaFiscalGeral")
async def get_atributos_nota_geral():
    """Retorna os atributos gerais da nota fiscal"""
    try:
        data = json_manager.load_data('nota')
        return data[0]  
    except Exception as e:
        return {"error": str(e)}, 500

@app.post("/AddAtrNotaFiscalGeral")
async def add_atributo_nota_geral(request: Request):
    """Adiciona um novo atributo à seção geral da nota fiscal"""
    data = await request.json()
    try:
        new_attr = json_manager.add_attribute('nota', data.get("description"), section=0)
        return new_attr
    except Exception as e:
        return {"error": str(e)}, 400

@app.post("/RemoveAtrNotaFiscalGeral")
async def remove_atributo_nota_geral(request: Request):
    """Remove um atributo da seção geral da nota fiscal"""
    data = await request.json()
    try:
        removed = json_manager.remove_attribute('nota', data.get("index"), section=0)
        return removed if removed else {"error": "Atributo não encontrado"}, 404
    except Exception as e:
        return {"error": str(e)}, 400


@app.get("/GetAtrNotaFiscalProdutos")
async def get_atributos_nota_produtos():
    """Retorna os atributos de produtos da nota fiscal"""
    try:
        data = json_manager.load_data('nota')
        return data[1]  
    except Exception as e:
        return {"error": str(e)}, 500

@app.post("/AddAtrNotaFiscalProdutos")
async def add_atributo_nota_produtos(request: Request):
    """Adiciona um novo atributo à seção de produtos da nota fiscal"""
    data = await request.json()
    try:
        new_attr = json_manager.add_attribute('nota', data.get("description"), section=1)
        return new_attr
    except Exception as e:
        return {"error": str(e)}, 400

@app.post("/RemoveAtrNotaFiscalProdutos")
async def remove_atributo_nota_produtos(request: Request):
    """Remove um atributo da seção de produtos da nota fiscal"""
    data = await request.json()
    try:
        removed = json_manager.remove_attribute('nota', data.get("index"), section=1)
        return removed if removed else {"error": "Atributo não encontrado"}, 404
    except Exception as e:
        return {"error": str(e)}, 400



import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)