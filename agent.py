from dataclasses import dataclass, field
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM


@dataclass
class LangChainOllamaChain:
    dado: str
    model_name: str = "llama3.1"
    template: str = "Question: {question}"
    prompt: ChatPromptTemplate = field(init=False)
    model: OllamaLLM = field(init=False)
    chain: any = field(init=False)
    
    def __post_init__(self):
        contexto = f"Contexto:\n{self.dado}\n\n{self.template}"
        self.prompt = ChatPromptTemplate.from_template(contexto)
        self.model = OllamaLLM(model=self.model_name)
        self.chain = self.prompt | self.model

    def ask(self, question: str) -> str:
        return self.chain.invoke({"question": question})

# Exemplo de uso
if __name__ == "__main__":
    chain_instance = LangChainOllamaChain(dado="a casa do senhor sergio é veremelha")
    resposta = chain_instance.ask("qual é a cor da casa do senhor sergio?")
    print(resposta)
