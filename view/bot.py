from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes, ConversationHandler
from telegram import Update
from collections import defaultdict
import json
import requests
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
token = os.getenv("TOKEN")

FASTAPI_URL = "http://127.0.0.1:8000/upload"
FASTAPI_URL_PHOTO = "http://127.0.0.1:8000/uploadPhoto"
FASTAPI_URL_PHOTOS = "http://127.0.0.1:8000/uploadPhotos"
FASTAPI_URL_RESPONSE = "http://127.0.0.1:8000/response"
SELECT_DOC_TYPE, ADD_ATRIBUTO, REMOVE_ATRIBUTO, SELECT_SECTION = range(4)

app = Application.builder().token(token).build()
media_groups = {}

# Funções auxiliares
def get_doc_filename(doc_type):
    return {
        'agua': 'view/agua.json',
        'nota': 'view/notaFiscal.json'
    }.get(doc_type, 'view/agua.json')

async def handle_album(update: Update, context):
    message = update.message
    
    # Verifica se a mensagem faz parte de um grupo de mídia
    if message.media_group_id:
        group_id = message.media_group_id
        if group_id not in media_groups:
            media_groups[group_id] = []
            # Agenda o processamento do grupo após 1 segundo para acumular todas as mensagens
            asyncio.create_task(process_media_group_after_delay(group_id, delay=1.0))
        media_groups[group_id].append(message)
    else:
        # Se não for parte de um grupo, processa individualmente
        await process_individual_message(message)

async def process_media_group_after_delay(group_id, delay=1.0):
    # Aguarda um curto período para garantir que todas as mensagens do grupo sejam recebidas
    await asyncio.sleep(delay)
    # Remove o grupo do dicionário e processa as mensagens acumuladas
    messages = media_groups.pop(group_id, [])
    await process_media_group(messages)

async def process_media_group(messages):
    files = []
    for msg in messages:
        file = await msg.photo[-1].get_file()
        file_data = requests.get(file.file_path).content
        files.append(("files", (file.file_path, file_data)))  # Envia vários arquivos com a mesma chave "files"

    response = requests.post(FASTAPI_URL_PHOTOS, files=files)

    if response.status_code == 200:
            await messages[0].reply_text("✅ Documento processado com sucesso!\n\n")
            dict_response = json.loads(response.text)
            
            if dict_response.get("produtos"):
                resposta = "📋 Atributos Nota Fiscal:\n"
                for key, value in dict_response.items():
                    if key == "produtos":
                        resposta += "\n\n📋 Atributos de Produtos:\n"
                        for dict in dict_response["produtos"]:
                            for key, value in dict.items():
                                if value == None:
                                    value = "..."
                                resposta += f"🔹 {key} - *{value.replace('_', ' ').title()}*\n"
                                break
                    if value == None:
                        value = "..."
                    resposta += f"🔹 {key} - *{value.replace('_', ' ').title()}*\n"

                await messages[0].reply_text(resposta, parse_mode='Markdown')
                return

            resposta = "📋 Atributos Conta Agua:\n\n"
            for key, value in dict_response.items():
                if value == None:
                    value = "..."
                resposta += f"🔹 {key} - *{value.replace('_', ' ').title()}*\n"

            await messages[0].reply_text(resposta, parse_mode='Markdown')
            
    else:
        await messages[0].reply_text(f"❌ Erro no processamento: {response.text}")



async def process_individual_message(message) -> None:
    file = await message.photo[-1].get_file()
    file_data = requests.get(file.file_path).content
    
    files = {"file": (file.file_path, file_data)}
    response = requests.post(FASTAPI_URL_PHOTO, files=files)+

    if response.status_code == 200:
            await message[0].reply_text("✅ Documento processado com sucesso!\n\n")
            dict_response = json.loads(response.text)
            
            if dict_response.get("produtos"):
                resposta = "📋 Atributos Nota Fiscal:\n"
                for key, value in dict_response.items():
                    if key == "produtos":
                        resposta += "\n\n📋 Atributos de Produtos:\n"
                        for dict in dict_response["produtos"]:
                            for key, value in dict.items():
                                if value == None:
                                    value = "..."
                                resposta += f"🔹 {key} - *{value.replace('_', ' ').title()}*\n"
                                break
                    if value == None:
                        value = "..."
                    resposta += f"🔹 {key} - *{value.replace('_', ' ').title()}*\n"

                await message[0].reply_text(resposta, parse_mode='Markdown')
                return

            resposta = "📋 Atributos Conta Agua:\n\n"
            for key, value in dict_response.items():
                if value == None:
                    value = "..."
                resposta += f"🔹 {key} - *{value.replace('_', ' ').title()}*\n"

            await message[0].reply_text(resposta, parse_mode='Markdown')
            
    else:
        await message[0].reply_text(f"❌ Erro no processamento: {response.text}")




async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        file = await update.message.document.get_file()
        file_data = requests.get(file.file_path).content
        
        files = {"file": (update.message.document.file_name, file_data)}
        response = requests.post(FASTAPI_URL, files=files)
        
        if response.status_code == 200:
            await update.message.reply_text("✅ Documento processado com sucesso!\n\n")
            dict_response = json.loads(response.text)
            
            if dict_response.get("produtos"):
                resposta = "📋 Atributos Nota Fiscal:\n"
                for key, value in dict_response.items():
                    if key == "produtos":
                        resposta += "\n\n📋 Atributos de Produtos:\n"
                        for dict in dict_response["produtos"]:
                            for key, value in dict.items():
                                if value == None:
                                    value = "..."
                                resposta += f"🔹 {key} - *{value.replace('_', ' ').title()}*\n"
                                break
                    if value == None:
                        value = "..."
                    resposta += f"🔹 {key} - *{value.replace('_', ' ').title()}*\n"

                await update.message.reply_text(resposta, parse_mode='Markdown')
                return

            resposta = "📋 Atributos Conta Agua:\n\n"
            for key, value in dict_response.items():
                if value == None:
                    value = "..."
                resposta += f"🔹 {key} - *{value.replace('_', ' ').title()}*\n"

            await update.message.reply_text(resposta, parse_mode='Markdown')
            
        else:
            await update.message.reply_text(f"❌ Erro no processamento: {response.text}")

    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao processar documento: {str(e)}")




async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    mensagem = (
        "🚀 Bem-vindo ao Bot de Extração de Dados! 🚀\n\n"
        "📌 Comandos disponíveis:\n"
        "/start - Mostra esta mensagem\n"
        "/ExibirContaAgua - Listar atributos da Conta de Água\n"
        "/ExibirNotaFiscal - Listar atributos da Nota Fiscal\n"
        "Envie um PDF para processar ou use os comandos acima."
    )
    await update.message.reply_text(mensagem)

async def ExibirContaAgua(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['current_doc'] = 'agua'
    try:
        with open("view/agua.json", "r") as f:
            dados = json.load(f)
            
        resposta = "📋 Atributos da Conta de Água:\n\n"
        for dado in dados:
            resposta += f"🔹 {dado['index']} - *{dado['description'].replace('_', ' ').title()}*\n"
            
        await update.message.reply_text(resposta, parse_mode='Markdown')
        await update.message.reply_text("/adicionarAtributo - Adicionar atributo\n/removerAtributo - Remover atributo")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")

async def ExibirNotaFiscal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['current_doc'] = 'nota'
    try:
        with open("view/notaFiscal.json", "r") as f:
            dados = json.load(f)
            
        # Exibir atributos gerais (primeira seção)
        resposta = "📋 Atributos Gerais da Nota Fiscal:\n\n"
        for dado in dados[0]:
            resposta += f"🔹 {dado['index']} - *{dado['description'].replace('_', ' ').title()}*\n"
        
        await update.message.reply_text(resposta, parse_mode='Markdown')
        
        # Exibir atributos de produtos (segunda seção)
        resposta = "📋 Atributos de Produtos da Nota Fiscal:\n\n"
        for dado in dados[1]:
            resposta += f"🔹 {dado['index']} - *{dado['description'].replace('_', ' ').title()}*\n"
            
        await update.message.reply_text(resposta, parse_mode='Markdown')
        await update.message.reply_text("/adicionarAtributo - Adicionar atributo\n/removerAtributo - Remover atributo")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")

# Handlers de Atributos
async def adicionar_atributo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if 'current_doc' not in context.user_data:
        await update.message.reply_text("📄 Selecione o documento:\n/agua - Conta de Água\n/nota - Nota Fiscal")
        return SELECT_DOC_TYPE
    
    if context.user_data['current_doc'] == 'nota':
        await update.message.reply_text("📝 Selecione a seção:\n1 - Atributos Gerais\n2 - Atributos de Produtos")
        return SELECT_SECTION
    else:
        await update.message.reply_text("📝 Informe o novo atributo:")
        return ADD_ATRIBUTO

async def select_doc_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    doc_type = update.message.text.strip().lower()
    if doc_type not in ['agua', 'nota']:
        await update.message.reply_text("❌ Documento inválido! Use /agua ou /nota")
        return SELECT_DOC_TYPE
    
    context.user_data['current_doc'] = doc_type
    
    if doc_type == 'nota':
        await update.message.reply_text("📝 Selecione a seção:\n1 - Atributos Gerais\n2 - Atributos de Produtos")
        return SELECT_SECTION
    else:
        await update.message.reply_text("📝 Informe o novo atributo:")
        return ADD_ATRIBUTO

async def select_section(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        section = int(update.message.text.strip())
        if section not in [1, 2]:
            await update.message.reply_text("❌ Seção inválida! Digite 1 para Atributos Gerais ou 2 para Atributos de Produtos")
            return SELECT_SECTION
        
        # Armazenar a seção escolhida (ajustando para índice 0-based)
        context.user_data['section'] = section - 1
        await update.message.reply_text("📝 Informe o novo atributo:")
        return ADD_ATRIBUTO
        
    except ValueError:
        await update.message.reply_text("❌ Valor inválido! Digite 1 para Atributos Gerais ou 2 para Atributos de Produtos")
        return SELECT_SECTION

async def add_atributo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    atributo = update.message.text.strip().lower()
    doc_type = context.user_data['current_doc']
    arquivo = get_doc_filename(doc_type)
    
    try:
        with open(arquivo, "r+") as f:
            dados = json.load(f)
            
            if doc_type == 'nota':
                section = context.user_data['section']
                novo_index = len(dados[section])
                dados[section].append({
                    "index": novo_index,
                    "type": "string" if section == 0 or atributo.startswith("nome") else "number",
                    "description": atributo
                })
            else:
                novo_index = len(dados)
                dados.append({
                    "index": novo_index,
                    "type": "string",
                    "description": atributo
                })
            
            f.seek(0)
            json.dump(dados, f, indent=4, ensure_ascii=False)
            f.truncate()
            
        secao_texto = f" na seção {'Atributos Gerais' if context.user_data.get('section') == 0 else 'Atributos de Produtos'}" if doc_type == 'nota' else ""
        await update.message.reply_text(f"✅ Atributo '{atributo}' adicionado com sucesso{secao_texto}!")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")
    
    return ConversationHandler.END

async def remover_atributo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if 'current_doc' not in context.user_data:
        await update.message.reply_text("📄 Selecione o documento:\n/agua - Conta de Água\n/nota - Nota Fiscal")
        return SELECT_DOC_TYPE
    
    if context.user_data['current_doc'] == 'nota':
        await update.message.reply_text("📝 Selecione a seção:\n1 - Atributos Gerais\n2 - Atributos de Produtos")
        return SELECT_SECTION
    else:
        await update.message.reply_text("🔢 Informe o ID do atributo a ser removido:")
        return REMOVE_ATRIBUTO

async def remove_atributo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        index = int(update.message.text.strip())
    except:
        await update.message.reply_text("❌ ID inválido! Informe apenas números")
        return ConversationHandler.END
    
    doc_type = context.user_data['current_doc']
    arquivo = get_doc_filename(doc_type)
    
    try:
        with open(arquivo, "r+") as f:
            dados = json.load(f)
            
            if doc_type == 'nota':
                section = context.user_data['section']
                atributo = None
                for i, item in enumerate(dados[section]):
                    if item['index'] == index:
                        atributo = item['description']
                        dados[section].pop(i)
                        break
                
                # Reindexar a seção atual
                for i, item in enumerate(dados[section]):
                    item['index'] = i
            else:
                atributo = None
                for i, item in enumerate(dados):
                    if item['index'] == index:
                        atributo = item['description']
                        dados.pop(i)
                        break
                
                # Reindexar
                for i, item in enumerate(dados):
                    item['index'] = i
                
            f.seek(0)
            json.dump(dados, f, indent=4, ensure_ascii=False)
            f.truncate()
        
        if atributo:
            secao_texto = f" na seção {'Atributos Gerais' if context.user_data.get('section') == 0 else 'Atributos de Produtos'}" if doc_type == 'nota' else ""
            await update.message.reply_text(f"✅ Atributo '{atributo}' removido com sucesso{secao_texto}!")
        else:
            await update.message.reply_text("❌ ID não encontrado!")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")
    
    return ConversationHandler.END

async def cancel(update: Update, context) -> int:
    await update.message.reply_text("❌ Operação cancelada")
    return ConversationHandler.END

# Configuração dos Handlers
conv_handler_add = ConversationHandler(
    entry_points=[CommandHandler('adicionarAtributo', adicionar_atributo)],
    states={
        SELECT_DOC_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_doc_type)],
        SELECT_SECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_section)],
        ADD_ATRIBUTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_atributo)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

conv_handler_remove = ConversationHandler(
    entry_points=[CommandHandler('removerAtributo', remover_atributo)],
    states={
        SELECT_DOC_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_doc_type)],
        SELECT_SECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_section)],
        REMOVE_ATRIBUTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, remove_atributo)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)





app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ExibirContaAgua", ExibirContaAgua))
app.add_handler(CommandHandler("ExibirNotaFiscal", ExibirNotaFiscal))
app.add_handler(MessageHandler(filters.Document.PDF, handle_document))
app.add_handler(MessageHandler(filters.PHOTO, handle_album))
app.add_handler(conv_handler_add)
app.add_handler(conv_handler_remove)

# Inicia o Bot
if __name__ == "__main__":
    print("🤖 Bot em execução...")
    app.run_polling()