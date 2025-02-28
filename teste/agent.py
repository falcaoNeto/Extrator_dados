from langchain_google_genai import GoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain_ollama.llms import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from dotenv import load_dotenv  
import os
load_dotenv()
KEY_API = os.getenv("GOOGLE_API_KEY")


class LangChainOllamaChain:
    def __init__(self, context: str):
        """Inicializa o chatbot com uma chave da OpenAI e um mini texto base."""
        self.context = context  # Texto base para respostas
        self.llm = GoogleGenerativeAI(model="gemini-1.5-flash", api_key=KEY_API)  # Modelo da OpenAI
        self.memory = ConversationBufferMemory()  # Memória para lembrar contexto

        # Template do prompt incluindo context e histórico de conversa
        self.prompt_template = PromptTemplate(
            input_variables=["history", "input"],
            template=(
                "Base de conhecimento:\n{context}\n\n"
                "Histórico da conversa:\n{history}\n\n"
                "Usuário: {input}\n"
                "Assistente:"
            ),
        )

        
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            prompt=self.prompt_template.partial(context=self.context),
        )

    def perguntar(self, pergunta: str) -> str:
        """Recebe uma pergunta e retorna a resposta com base no context e memória."""
        return self.conversation.predict(input=pergunta)

 
if __name__ == "__main__":
    
    context = "a casa do seu joao tem 100m2 de area e tem a cor verde no portão."

    chatbot = LangChainOllamaChain(context)

    while True:
        pergunta = input("Você: ")
        if pergunta.lower() in ["sair", "exit", "fim"]:
            print("Encerrando conversa.")
            break
        resposta = chatbot.perguntar(pergunta)
        print("Assistente:", resposta)
