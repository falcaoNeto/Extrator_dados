from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama.llms import OllamaLLM
import os
from dotenv import load_dotenv
load_dotenv()
KEY_API = os.getenv("GOOGLE_API_KEY")


class LLm:
    def __init__(self):
        self.gemini = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=KEY_API)
        self.ollama = OllamaLLM(model="llama3.1:latest", endpoint="http://localhost:11434")



    def llm_instance(self, llm):
        if llm == "gemini":
            return self.gemini
        elif llm == "ollama":
            return self.ollama
        else:
            raise ValueError("Modelo de LLM inválido. Escolha 'gemini' ou 'ollama'.")

    

if __name__ == "__main__":
    llm = LLm()
    print(llm.llm_instance("gemini"))