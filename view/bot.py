from telegram import Update
from telegram.ext import (
    Application, MessageHandler, filters, CommandHandler, 
    ContextTypes, ConversationHandler
)
import json
import requests
import asyncio
import os
from dotenv import load_dotenv

class DocumentExtractionBot:
    DOC_TYPE, SECTION, ADD_ATTRIBUTE, REMOVE_ATTRIBUTE = range(4)
    host = "api"
    # URLs para upload e resposta
    FASTAPI_URL = f"http://{host}:8000/upload"
    FASTAPI_URL_PHOTO = f"http://{host}:8000/uploadPhoto"
    FASTAPI_URL_PHOTOS = f"http://{host}:8000/uploadPhotos"
    FASTAPI_URL_RESPONSE = f"http://{host}:8000/response"

    # URLs para manipulação de atributos
    FASTAPI_URL_GET_AGUA = f"http://{host}:8000/GetAtrAgua"
    FASTAPI_URL_ADD_AGUA = f"http://{host}:8000/AddAtrAgua"
    FASTAPI_URL_REMOVE_AGUA = f"http://{host}:8000/RemoveAtrAgua"
    FASTAPI_URL_GET_NOTA_GERAL = f"http://{host}:8000/GetAtrNotaFiscalGeral"
    FASTAPI_URL_ADD_NOTA_GERAL = f"http://{host}:8000/AddAtrNotaFiscalGeral"
    FASTAPI_URL_REMOVE_NOTA_GERAL = f"http://{host}:8000/RemoveAtrNotaFiscalGeral"
    FASTAPI_URL_GET_NOTA_PRODUTOS = f"http://{host}:8000/GetAtrNotaFiscalProdutos"
    FASTAPI_URL_ADD_NOTA_PRODUTOS = f"http://{host}:8000/AddAtrNotaFiscalProdutos"
    FASTAPI_URL_REMOVE_NOTA_PRODUTOS = f"http://{host}:8000/RemoveAtrNotaFiscalProdutos"
    
    def __init__(self):
        load_dotenv()
        self.token = os.getenv("TOKEN")
        self.app = Application.builder().token(self.token).build()
        self.media_groups = {}
        
        self._register_handlers()
    
    def _register_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("ExibirContaAgua", self.ExibirContaAgua))
        self.app.add_handler(CommandHandler("ExibirNotaFiscal", self.ExibirNotaFiscal))
        self.app.add_handler(MessageHandler(filters.Document.PDF, self.handle_document))
        self.app.add_handler(MessageHandler(filters.PHOTO, self.handle_album))
        self.app.add_handler(self._create_add_attribute_handler())
        self.app.add_handler(self._create_remove_attribute_handler())
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.ConsultorDados))
    
    async def handle_album(self, update: Update, context):
        message = update.message
        if message.media_group_id:
            group_id = message.media_group_id
            if group_id not in self.media_groups:
                self.media_groups[group_id] = []
                asyncio.create_task(self.process_media_group_after_delay(group_id, delay=1.0))
            self.media_groups[group_id].append(message)
        else:
            await self.process_individual_message(message)
    
    async def process_media_group_after_delay(self, group_id, delay=1.0):
        await asyncio.sleep(delay)
        messages = self.media_groups.pop(group_id, [])
        await self.process_media_group(messages)
    
    async def process_media_group(self, messages):
        files = []
        for msg in messages:
            file = await msg.photo[-1].get_file()
            file_data = requests.get(file.file_path).content
            files.append(("files", (file.file_path, file_data)))
    
        response = requests.post(self.FASTAPI_URL_PHOTOS, files=files)
    
        if response.status_code == 200:
            await messages[0].reply_text("✅ Documento processado com sucesso!\n\n")
            dict_response = json.loads(response.text)
            if dict_response.get("produtos"):
                await self._format_nota_fiscal_response(messages[0], dict_response)
                return
            await self._format_agua_response(messages[0], dict_response)
        else:
            await messages[0].reply_text(f"❌ Erro no processamento: {response.text}")
    
    async def process_individual_message(self, message):
        file = await message.photo[-1].get_file()
        file_data = requests.get(file.file_path).content
        files = {"file": (file.file_path, file_data)}
        response = requests.post(self.FASTAPI_URL_PHOTO, files=files)
    
        if response.status_code == 200:
            await message.reply_text("✅ Documento processado com sucesso!\n\n")
            dict_response = json.loads(response.text)
            if dict_response.get("produtos"):
                await self._format_nota_fiscal_response(message, dict_response)
                return
            await self._format_agua_response(message, dict_response)
        else:
            await message.reply_text(f"❌ Erro no processamento: {response.text}")
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            file = await update.message.document.get_file()
            file_data = requests.get(file.file_path).content
            files = {"file": (update.message.document.file_name, file_data)}
            response = requests.post(self.FASTAPI_URL, files=files)
            
            if response.status_code == 200:
                await update.message.reply_text("✅ Documento processado com sucesso!\n\n")
                dict_response = json.loads(response.text)
                if dict_response.get("produtos"):
                    await self._format_nota_fiscal_response(update.message, dict_response)
                    return
                await self._format_agua_response(update.message, dict_response)
            else:
                await update.message.reply_text(f"❌ Erro no processamento: {response.text}")
        except Exception as e:
            await update.message.reply_text(f"❌ Erro ao processar documento: {str(e)}")
    
    async def _format_nota_fiscal_response(self, message, dict_response):
        resposta = "\U0001F4CB *Nota Fiscal:*\n"
        for key, value in dict_response.items():
            if key == "produtos":
                continue 
            resposta += f"\n\U0001F4D6 *{key.replace('_', ' ').title()}*: {value if value is not None else '...'}"
        resposta += "\n\n\U0001F4CB *Produtos:*\n"
        for produto in dict_response.get("produtos", []):
            resposta += "\n\U0001F539 *Produto:*\n"
            for p_key, p_value in produto.items():
                resposta += f"\U0001F4DD {p_key.replace('_', ' ').title()}: {p_value if p_value is not None else '...'}\n"
        await message.reply_text(resposta, parse_mode="Markdown")
    
    async def _format_agua_response(self, message, dict_response):
        resposta = "\U0001F4CB *Conta de Água:*\n\n"
        for key, value in dict_response.items():
            resposta += f"\U0001F4A7 *{key.replace('_', ' ').title()}*: {value if value is not None else '...'}\n"
        await message.reply_text(resposta, parse_mode='Markdown')
    
    async def ConsultorDados(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message.text
        response = requests.post(self.FASTAPI_URL_RESPONSE, json={"message": message})
        dic_resp = response.json()
        resp = dic_resp.get("response")
        await update.message.reply_text(resp)
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        mensagem = (
            "🚀 Bem-vindo ao Bot de Extração de Dados! 🚀\n\n"
            "📌 Comandos disponíveis:\n"
            "/start - Mostra esta mensagem\n"
            "/ExibirContaAgua - Listar atributos da Conta de Água\n"
            "/ExibirNotaFiscal - Listar atributos da Nota Fiscal\n"
            "Envie um PDF ou imagens para processar ou use os comandos acima\n"
            "Faça uma pergunta sobre os documentos enviados!"
        )
        await update.message.reply_text(mensagem)
    
    async def ExibirContaAgua(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['current_doc'] = 'agua'
        try:
            response = requests.get(self.FASTAPI_URL_GET_AGUA)
            if response.status_code != 200:
                await update.message.reply_text("❌ Erro ao obter atributos da conta de água.")
                return
            data = response.json()
            resposta = "📋 Atributos da Conta de Água:\n\n"
            resposta += "- Data de Emissao\n- Valor Total\n- Consumo Faturado\n\n"
            for item in data:
                resposta += f"🔹 {item['index']} - *{item['description'].replace('_', ' ').title()}*\n"
            await update.message.reply_text(resposta, parse_mode='Markdown')
            await update.message.reply_text("/adicionarAtributo - Adicionar atributo\n/removerAtributo - Remover atributo")
        except Exception as e:
            await update.message.reply_text(f"❌ Erro: {str(e)}")
    
    async def ExibirNotaFiscal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['current_doc'] = 'nota'
        try:
            # Atributos Gerais
            response_geral = requests.get(self.FASTAPI_URL_GET_NOTA_GERAL)
            if response_geral.status_code != 200:
                await update.message.reply_text("❌ Erro ao obter atributos gerais da nota fiscal.")
                return
            data_geral = response_geral.json()
            resposta = "📋 Atributos Gerais da Nota Fiscal:\n\n"
            resposta += "- Nome da Empresa\n- Data Compra\n- Valor Total\n\n"
            for item in data_geral:
                resposta += f"🔹 {item['index']} - *{item['description'].replace('_', ' ').title()}*\n"
            await update.message.reply_text(resposta, parse_mode='Markdown')
            
            # Atributos de Produtos
            response_produtos = requests.get(self.FASTAPI_URL_GET_NOTA_PRODUTOS)
            if response_produtos.status_code != 200:
                await update.message.reply_text("❌ Erro ao obter atributos de produtos da nota fiscal.")
                return
            data_produtos = response_produtos.json()
            resposta = "📋 Atributos de Produtos da Nota Fiscal:\n\n"
            resposta += "- Nome do Produto\n- Valor do Produto\n\n"
            for item in data_produtos:
                resposta += f"🔹 {item['index']} - *{item['description'].replace('_', ' ').title()}*\n"
            await update.message.reply_text(resposta, parse_mode='Markdown')
            await update.message.reply_text("/adicionarAtributo - Adicionar atributo\n/removerAtributo - Remover atributo")
        except Exception as e:
            await update.message.reply_text(f"❌ Erro: {str(e)}")
    
    def _create_add_attribute_handler(self):
        return ConversationHandler(
            entry_points=[CommandHandler('adicionarAtributo', self.adicionar_atributo)],
            states={
                self.DOC_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.select_doc_type_add)],
                self.SECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.select_section_add)],
                self.ADD_ATTRIBUTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.add_attribute)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
        )
    
    async def adicionar_atributo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if 'current_doc' not in context.user_data:
            await update.message.reply_text("📄 Selecione o documento (agua ou nota):")
            return self.DOC_TYPE
        else:
            doc_type = context.user_data['current_doc']
            if doc_type == 'nota':
                await update.message.reply_text("📝 Selecione a seção:\n1 - Atributos Gerais\n2 - Atributos de Produtos")
                return self.SECTION
            else:
                await update.message.reply_text("📝 Informe o novo atributo:")
                return self.ADD_ATTRIBUTE
    
    async def select_doc_type_add(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        doc_type = update.message.text.strip().lower()
        if doc_type not in ['agua', 'nota']:
            await update.message.reply_text("❌ Documento inválido! Use 'agua' ou 'nota'.")
            return self.DOC_TYPE
        context.user_data['current_doc'] = doc_type
        if doc_type == 'nota':
            await update.message.reply_text("📝 Selecione a seção:\n1 - Atributos Gerais\n2 - Atributos de Produtos")
            return self.SECTION
        else:
            await update.message.reply_text("📝 Informe o novo atributo:")
            return self.ADD_ATTRIBUTE
    
    async def select_section_add(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            section = int(update.message.text.strip())
            if section not in [1, 2]:
                await update.message.reply_text("❌ Seção inválida! Digite 1 ou 2.")
                return self.SECTION
            context.user_data['section'] = section - 1
            await update.message.reply_text("📝 Informe o novo atributo:")
            return self.ADD_ATTRIBUTE
        except ValueError:
            await update.message.reply_text("❌ Valor inválido! Digite 1 ou 2.")
            return self.SECTION
    
    async def add_attribute(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        attribute = update.message.text.strip()
        doc_type = context.user_data['current_doc']
        try:
            if doc_type == 'agua':
                url = self.FASTAPI_URL_ADD_AGUA
            elif doc_type == 'nota':
                section = context.user_data.get('section', 0)
                url = self.FASTAPI_URL_ADD_NOTA_GERAL if section == 0 else self.FASTAPI_URL_ADD_NOTA_PRODUTOS
            else:
                await update.message.reply_text("❌ Tipo de documento inválido.")
                return ConversationHandler.END
            
            response = requests.post(url, json={"description": attribute})
            if response.status_code == 200:
                secao_texto = ""
                if doc_type == 'nota':
                    secao_texto = " na seção " + ("Atributos Gerais" if context.user_data.get('section') == 0 else "Atributos de Produtos")
                await update.message.reply_text(f"✅ Atributo '{attribute}' adicionado com sucesso{secao_texto}!")
            else:
                await update.message.reply_text(f"❌ Erro ao adicionar atributo: {response.text}")
        except Exception as e:
            await update.message.reply_text(f"❌ Erro: {str(e)}")
        return ConversationHandler.END
    
    def _create_remove_attribute_handler(self):
        return ConversationHandler(
            entry_points=[CommandHandler('removerAtributo', self.remover_atributo)],
            states={
                self.DOC_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.select_doc_type_remove)],
                self.SECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.select_section_remove)],
                self.REMOVE_ATTRIBUTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.remove_attribute)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
        )
    
    async def remover_atributo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if 'current_doc' not in context.user_data:
            await update.message.reply_text("📄 Selecione o documento (agua ou nota):")
            return self.DOC_TYPE
        else:
            doc_type = context.user_data['current_doc']
            if doc_type == 'nota':
                await update.message.reply_text("📝 Selecione a seção:\n1 - Atributos Gerais\n2 - Atributos de Produtos")
                return self.SECTION
            else:
                await update.message.reply_text("🔢 Informe o ID do atributo a ser removido:")
                return self.REMOVE_ATTRIBUTE
    
    async def select_doc_type_remove(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        doc_type = update.message.text.strip().lower()
        if doc_type not in ['agua', 'nota']:
            await update.message.reply_text("❌ Documento inválido! Use 'agua' ou 'nota'.")
            return self.DOC_TYPE
        context.user_data['current_doc'] = doc_type
        if doc_type == 'nota':
            await update.message.reply_text("📝 Selecione a seção:\n1 - Atributos Gerais\n2 - Atributos de Produtos")
            return self.SECTION
        else:
            await update.message.reply_text("🔢 Informe o ID do atributo a ser removido:")
            return self.REMOVE_ATTRIBUTE
    
    async def select_section_remove(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            section = int(update.message.text.strip())
            if section not in [1, 2]:
                await update.message.reply_text("❌ Seção inválida! Digite 1 ou 2.")
                return self.SECTION
            context.user_data['section'] = section - 1
            await update.message.reply_text("🔢 Informe o ID do atributo a ser removido:")
            return self.REMOVE_ATTRIBUTE
        except ValueError:
            await update.message.reply_text("❌ Valor inválido! Digite 1 ou 2.")
            return self.SECTION
    
    async def remove_attribute(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            index = int(update.message.text.strip())
        except ValueError:
            await update.message.reply_text("❌ ID inválido! Informe apenas números.")
            return ConversationHandler.END
        
        doc_type = context.user_data['current_doc']
        try:
            if doc_type == 'agua':
                get_url = self.FASTAPI_URL_GET_AGUA
                remove_url = self.FASTAPI_URL_REMOVE_AGUA
            elif doc_type == 'nota':
                section = context.user_data.get('section', 0)
                if section == 0:
                    get_url = self.FASTAPI_URL_GET_NOTA_GERAL
                    remove_url = self.FASTAPI_URL_REMOVE_NOTA_GERAL
                else:
                    get_url = self.FASTAPI_URL_GET_NOTA_PRODUTOS
                    remove_url = self.FASTAPI_URL_REMOVE_NOTA_PRODUTOS
            else:
                await update.message.reply_text("❌ Tipo de documento inválido.")
                return ConversationHandler.END
            
            # Obter atributos para encontrar a descrição
            response_get = requests.get(get_url)
            if response_get.status_code != 200:
                await update.message.reply_text("❌ Erro ao obter atributos.")
                return ConversationHandler.END
            data = response_get.json()
            
            # Encontrar atributo pelo index
            removed_attr = next((item['description'] for item in data if item['index'] == index), None)
            if not removed_attr:
                await update.message.reply_text("❌ ID não encontrado!")
                return ConversationHandler.END
            
            # Remover atributo
            response_remove = requests.post(remove_url, json={"index": index})
            if response_remove.status_code != 200:
                await update.message.reply_text(f"❌ Erro ao remover atributo: {response_remove.text}")
                return ConversationHandler.END
            
            secao_texto = ""
            if doc_type == 'nota':
                secao_texto = " na seção " + ("Atributos Gerais" if context.user_data.get('section') == 0 else "Atributos de Produtos")
            await update.message.reply_text(f"✅ Atributo '{removed_attr}' removido com sucesso{secao_texto}!")
        except Exception as e:
            await update.message.reply_text(f"❌ Erro: {str(e)}")
        return ConversationHandler.END
    
    async def cancel(self, update: Update, context):
        await update.message.reply_text("❌ Operação cancelada")
        return ConversationHandler.END
    
    def run(self):
        print("🤖 Bot em execução...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = DocumentExtractionBot()
    bot.run()