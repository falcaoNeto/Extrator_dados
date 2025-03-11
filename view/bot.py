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
import json

class DocumentExtractionBot:
    SELECT_DOC_TYPE, ADD_ATRIBUTO, REMOVE_ATRIBUTO, SELECT_SECTION = range(4)
    

    FASTAPI_URL = "http://api:8000/upload"
    FASTAPI_URL_PHOTO = "http://api:8000/uploadPhoto"
    FASTAPI_URL_PHOTOS = "http://api:8000/uploadPhotos"
    FASTAPI_URL_RESPONSE = "http://api:8000/response"
    
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
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.ConsultorDados))
        
        self.app.add_handler(self._create_add_attribute_handler())
        self.app.add_handler(self._create_remove_attribute_handler())
    
    def _create_add_attribute_handler(self):
        """Create conversation handler for adding attributes"""
        return ConversationHandler(
            entry_points=[CommandHandler('adicionarAtributo', self.adicionar_atributo)],
            states={
                self.SELECT_DOC_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.select_doc_type)],
                self.SELECT_SECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.select_section)],
                self.ADD_ATRIBUTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.add_atributo)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)]
        )
    
    def _create_remove_attribute_handler(self):
        """Create conversation handler for removing attributes"""
        return ConversationHandler(
            entry_points=[CommandHandler('removerAtributo', self.remover_atributo)],
            states={
                self.SELECT_DOC_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.select_doc_type)],
                self.SELECT_SECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.select_section)],
                self.REMOVE_ATRIBUTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.remove_atributo)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)]
        )
    
    def get_doc_filename(self, doc_type):
        """Return the appropriate JSON file path based on document type"""
        return {
            'agua': 'view/agua.json',
            'nota': 'view/notaFiscal.json'
        }.get(doc_type, 'view/agua.json')
    
    async def handle_album(self, update: Update, context):
        """Handle photo album messages (media groups)"""
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
        """Process media group after a delay to ensure all photos are collected"""
        await asyncio.sleep(delay)
        messages = self.media_groups.pop(group_id, [])
        await self.process_media_group(messages)
    
    async def process_media_group(self, messages):
        """Process a group of photos and send to API"""
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
        """Process a single photo message"""
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
    
    async def _format_nota_fiscal_response(self, message, dict_response):
        """Formatar e enviar resposta da nota fiscal no bot do Telegram"""
        resposta = "\U0001F4CB *Nota Fiscal:*\n"
        
        for key, value in dict_response.items():
            if key == "produtos":
                continue 
            
            if value is None:
                value = "..."
            
            resposta += f"\n\U0001F4D6 *{key.replace('_', ' ').title()}*: {value}"
        
        resposta += "\n\n\U0001F4CB *Produtos:*\n"
        for produto in dict_response.get("produtos", []):
            resposta += "\n\U0001F539 *Produto:*\n"
            for p_key, p_value in produto.items():
                if p_value is None:
                    p_value = "..."
                resposta += f"\U0001F4DD {p_key.replace('_', ' ').title()}: {p_value}\n"
        
        await message.reply_text(resposta, parse_mode="Markdown")
    
    async def _format_agua_response(self, message, dict_response):
        """Formatar e enviar resposta da conta de água no bot do Telegram"""
        resposta = "\U0001F4CB *Conta de Água:*\n\n"
        
        for key, value in dict_response.items():
            if value is None:
                value = "..."
            resposta += f"\U0001F4A7 *{key.replace('_', ' ').title()}*: {value}\n"
        
        await message.reply_text(resposta, parse_mode='Markdown')

    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle PDF document uploads"""
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
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
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


    async def ConsultorDados(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message.text
        print(message)
        response = requests.post(self.FASTAPI_URL_RESPONSE, json={"message": message})
        print(response)
        dic_resp = response.json()
        resp = dic_resp.get("response")
        await update.message.reply_text(resp)
        


    
    async def ExibirContaAgua(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ExibirContaAgua command"""
        context.user_data['current_doc'] = 'agua'
        try:
            with open("view/agua.json", "r") as f:
                dados = json.load(f)
                
            resposta = "📋 Atributos da Conta de Água:\n\n"
            resposta += "- Data de Emissao\n- Valor Total\n- Consumo Faturado\n\n"
            for dado in dados:
                resposta += f"🔹 {dado['index']} - *{dado['description'].replace('_', ' ').title()}*\n"
                
            await update.message.reply_text(resposta, parse_mode='Markdown')
            await update.message.reply_text("/adicionarAtributo - Adicionar atributo\n/removerAtributo - Remover atributo")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Erro: {str(e)}")
    
    async def ExibirNotaFiscal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ExibirNotaFiscal command"""
        context.user_data['current_doc'] = 'nota'
        try:
            with open("view/notaFiscal.json", "r") as f:
                dados = json.load(f)
                
            resposta = "📋 Atributos Gerais da Nota Fiscal:\n\n"
            for dado in dados[0]:
                resposta += f"🔹 {dado['index']} - *{dado['description'].replace('_', ' ').title()}*\n"
            
            await update.message.reply_text(resposta, parse_mode='Markdown')
            
           
            resposta = "📋 Atributos de Produtos da Nota Fiscal:\n\n"
            for dado in dados[1]:
                resposta += f"🔹 {dado['index']} - *{dado['description'].replace('_', ' ').title()}*\n"
                
            await update.message.reply_text(resposta, parse_mode='Markdown')
            await update.message.reply_text("/adicionarAtributo - Adicionar atributo\n/removerAtributo - Remover atributo")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Erro: {str(e)}")
    
    async def adicionar_atributo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start conversation to add a new attribute"""
        if 'current_doc' not in context.user_data:
            await update.message.reply_text("📄 Selecione o documento:\n/agua - Conta de Água\n/nota - Nota Fiscal")
            return self.SELECT_DOC_TYPE
        
        if context.user_data['current_doc'] == 'nota':
            await update.message.reply_text("📝 Selecione a seção:\n1 - Atributos Gerais\n2 - Atributos de Produtos")
            return self.SELECT_SECTION
        else:
            await update.message.reply_text("📝 Informe o novo atributo:")
            return self.ADD_ATRIBUTO
    
    async def select_doc_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process document type selection"""
        doc_type = update.message.text.strip().lower()
        if doc_type not in ['agua', 'nota']:
            await update.message.reply_text("❌ Documento inválido! Use /agua ou /nota")
            return self.SELECT_DOC_TYPE
        
        context.user_data['current_doc'] = doc_type
        
        if doc_type == 'nota':
            await update.message.reply_text("📝 Selecione a seção:\n1 - Atributos Gerais\n2 - Atributos de Produtos")
            return self.SELECT_SECTION
        else:
            await update.message.reply_text("📝 Informe o novo atributo:")
            return self.ADD_ATRIBUTO
    
    async def select_section(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process section selection for nota fiscal"""
        try:
            section = int(update.message.text.strip())
            if section not in [1, 2]:
                await update.message.reply_text("❌ Seção inválida! Digite 1 para Atributos Gerais ou 2 para Atributos de Produtos")
                return self.SELECT_SECTION
            
            # Store chosen section (adjust to 0-based index)
            context.user_data['section'] = section - 1
            await update.message.reply_text("📝 Informe o novo atributo:")
            return self.ADD_ATRIBUTO
            
        except ValueError:
            await update.message.reply_text("❌ Valor inválido! Digite 1 para Atributos Gerais ou 2 para Atributos de Produtos")
            return self.SELECT_SECTION
    
    async def add_atributo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add a new attribute to the selected document/section"""
        atributo = update.message.text.strip().lower()
        doc_type = context.user_data['current_doc']
        arquivo = self.get_doc_filename(doc_type)
        
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
    
    async def remover_atributo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if 'current_doc' not in context.user_data:
            await update.message.reply_text("📄 Selecione o documento:\n/agua - Conta de Água\n/nota - Nota Fiscal")
            return self.SELECT_DOC_TYPE
        
        if context.user_data['current_doc'] == 'nota':
            await update.message.reply_text("📝 Selecione a seção:\n1 - Atributos Gerais\n2 - Atributos de Produtos")
            return self.SELECT_SECTION
        else:
            await update.message.reply_text("🔢 Informe o ID do atributo a ser removido:")
            return self.REMOVE_ATRIBUTO
    
    async def remove_atributo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            index = int(update.message.text.strip())
        except:
            await update.message.reply_text("❌ ID inválido! Informe apenas números")
            return ConversationHandler.END
        
        doc_type = context.user_data['current_doc']
        arquivo = self.get_doc_filename(doc_type)
        
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
                    
                    for i, item in enumerate(dados[section]):
                        item['index'] = i
                else:
                    atributo = None
                    for i, item in enumerate(dados):
                        if item['index'] == index:
                            atributo = item['description']
                            dados.pop(i)
                            break
                    
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
    
    async def cancel(self, update: Update, context):
        """Cancel the current operation"""
        await update.message.reply_text("❌ Operação cancelada")
        return ConversationHandler.END
    
    def run(self):
        """Start the bot"""
        print("🤖 Bot em execução...")
        self.app.run_polling()


if __name__ == "__main__":
    bot = DocumentExtractionBot()
    bot.run()