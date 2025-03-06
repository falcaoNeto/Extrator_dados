from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser

class Texto(BaseModel):
    result: str = Field(description="Classificar o texto entre(NotaFiscal, ContaAgua, NenhumOutro)")

load_dotenv()
KEY_API = os.getenv("GOOGLE_API_KEY")

class Classificar:
    def __init__(self, texto, model="gemini-1.5-flash", api_key=KEY_API):
        self.texto = texto
        self.llm = GoogleGenerativeAI(model=model, api_key=api_key)
        
    def classificar_texto(self):
        parser = PydanticOutputParser(pydantic_object=Texto)
        
        format_instructions = parser.get_format_instructions()
        
        prompt = PromptTemplate.from_template(
            """
            Deve classificar o texto usando as instrucoes abaixo:
            
            {format_instructions}

            Texto:
            {texto}
            """
            )
        format_prompt = prompt.format(texto=self.texto, format_instructions=format_instructions)
        result = self.llm.invoke(format_prompt)
        result = parser.parse(result)
        return result.result
    

if __name__ == "__main__":
    # with open("arquivo.txt", "r") as f:
    #     result2 = f.read()
    texto = "conta de agua, valor 120 reais e consumo de 45 m3"
    classificar = Classificar(texto)
    print(classificar.classificar_texto())