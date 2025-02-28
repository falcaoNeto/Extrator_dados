from dotenv import load_dotenv
import os
load_dotenv()

token = os.getenv("TOKEN")

import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from telegram.ext._contexttypes import ContextTypes
import json



FASTAPI_URL = "http://127.0.0.1:8000/upload"  # Endpoint do FastAPI

FASTAPI_URL_RESPONSE = "http://127.0.0.1:8000/response"

app = Application.builder().token(token).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Olá! Envie um PDF para processarmos. Clique em /DadosExtrair para verificar os dados a serem extraidos.")



async def DadosExtrair(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with open("contaAgua.json", "r") as f:
        result = json.loads(f)

    await update.message.reply_text(result)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.text:
        await update.message.reply_text("Envie um PDF para processarmos.")

    file = await update.message.document.get_file()
    file_path = file.file_path
    file_name = update.message.document.file_name

    
    file_data = requests.get(file_path).content
    
    
    files = {"file": (file_name, file_data)}
    response = requests.post(FASTAPI_URL, files=files)

    await update.message.reply_text(f"Documento enviado ao servidor! Resposta: {response.text}")

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Recebe áudios e repassa para o FastAPI"""
    file = await update.message.voice.get_file()
    file_path = file.file_path

    # Baixa o arquivo temporariamente
    file_data = requests.get(file_path).content

    # Envia para o FastAPI
    files = {"file": ("audio.mp3", file_data)}
    response = requests.post(FASTAPI_URL, files=files)

    await update.message.reply_text(f"Áudio enviado ao servidor! Resposta: {response.text}")



async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text
    response = requests.post(FASTAPI_URL_RESPONSE, json={"message": message})

    await update.message.reply_text(response.text)


# Adiciona os handlers ao bot
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.Document.PDF, handle_document))
app.add_handler(MessageHandler(filters.VOICE, handle_audio))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

app.run_polling()
