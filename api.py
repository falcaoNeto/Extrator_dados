from fastapi import FastAPI, File, UploadFile, Request
from docling.document_converter import DocumentConverter
import os
import tempfile
import json
from agent import LangChainOllamaChain


app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(await file.read())  # Salvar conteúdo no arquivo temporário
        temp_pdf_path = temp_pdf.name

    converter = DocumentConverter()
    result = converter.convert(temp_pdf_path)
    final = result.document.export_to_markdown()
    print(type(final))

    with open(os.path.join(UPLOAD_DIR, "arquivo.txt"), "w") as f:
        f.write(final)

    os.remove(temp_pdf_path)

@app.post("/response")
async def response(request: Request):
    # data = json.loads(json_question)
    json_body = await request.json()
    
    # Acessa o valor de 'message'
    message_content = json_body.get("message")

    with open(os.path.join("uploads", "arquivo.txt"), "r") as f:
        content = f.read()
    
    print(11)
    chain = LangChainOllamaChain(dado=content)
    result = chain.ask(message_content)
    print(result)
    
    return result
