import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

class TelegramPDFPhotoBot:
    def __init__(self, token):
        self.token = token
        self.application = Application.builder().token(self.token).build()
        # Dicionário para armazenar as mensagens de cada grupo de mídia
        self.media_groups = {}

    async def start(self, update: Update, context):
        await update.message.reply_text(
            "Olá! Envie várias fotos ou documentos PDF de uma vez que eu retornarei os IDs dos arquivos."
        )

    async def handle_album(self, update: Update, context):
        message = update.message

        # Verifica se a mensagem faz parte de um grupo de mídia
        if message.media_group_id:
            group_id = message.media_group_id
            if group_id not in self.media_groups:
                self.media_groups[group_id] = []
                # Agenda o processamento do grupo após 1 segundo para acumular todas as mensagens
                asyncio.create_task(self.process_media_group_after_delay(group_id, delay=1.0))
            self.media_groups[group_id].append(message)
        else:
            # Se não for parte de um grupo, processa individualmente
            await self.process_individual_message(message)

    async def process_media_group_after_delay(self, group_id, delay=1.0):
        # Aguarda um curto período para garantir que todas as mensagens do grupo sejam recebidas
        await asyncio.sleep(delay)
        # Remove o grupo do dicionário e processa as mensagens acumuladas
        messages = self.media_groups.pop(group_id, [])
        await self.process_media_group(messages)

    async def process_media_group(self, messages):
        # Extrai os file_ids das fotos (ou PDFs) do grupo
        file_ids = []
        for msg in messages:
            if msg.photo:
                # Seleciona a maior resolução (última da lista)
                file_ids.append(msg.photo[-1].file_id)
            elif msg.document:
                file_ids.append(msg.document.file_id)
        # Retorna os IDs das fotos respondendo na conversa (usando a primeira mensagem do grupo)
        await messages[0].reply_text(f"Fotos recebidas do grupo: {file_ids}")

    async def process_individual_message(self, message):
        file_ids = []
        if message.photo:
            file_ids.append(message.photo[-1].file_id)
        elif message.document:
            file_ids.append(message.document.file_id)
        # Retorna o ID da foto (ou PDF) individualmente
        await message.reply_text(f"Foto recebida: {file_ids}")

    def run(self):
        # Adiciona os manipuladores para o comando /start e para fotos/PDFs
        self.application.add_handler(CommandHandler('start', self.start))
        self.application.add_handler(
            MessageHandler(
                filters.PHOTO | filters.Document.PDF, 
                self.handle_album
            )
        )
        self.application.run_polling(drop_pending_updates=True)

# Exemplo de uso
bot = TelegramPDFPhotoBot(
    token='7545111242:AAGjSzBj-VK90LjNnkEEUxyCjE-wlSk6IFE'
)
bot.run()
