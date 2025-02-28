
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Union

load_dotenv()
KEY_API = os.getenv("GOOGLE_API_KEY")

class Produto(BaseModel):
    nome_do_produto: str = Field(description="Nome do produto na nota fiscal")
    quantidade: Union[int, float] = Field(description="Quantidade do produto")
    valor_unitario: float = Field(description="Valor unitário do produto em reais")
    model_config = ConfigDict(extra="allow")

class NotaFiscal(BaseModel):
    nome_da_empresa: str = Field(description="Nome da empresa emissora da nota fiscal")
    data_de_compra: str = Field(description="Data da compra no formato DD/MM/AAAA")
    produtos: List[Produto] = Field(description="Lista de produtos comprados")
    model_config = ConfigDict(extra="allow")




class NotaFiscal:
    def __init__(self, texto, model="gemini-1.5-flash", api_key=KEY_API):
        self.texto = texto
        self.llm = GoogleGenerativeAI(model=model, api_key=api_key)
        

    def extrair_nota_fiscal(self, campo_extra=None):

        parser = PydanticOutputParser(pydantic_object=NotaFiscal)
        
    
        format_instructions = parser.get_format_instructions()
        
        # Criar um template de prompt que inclui as instruções de formatação
        prompt = PromptTemplate.from_template(
            """Extraia os seguintes dados da nota fiscal abaixo:
            
            {format_instructions}
            
            Analise cuidadosamente o texto da nota fiscal e extraia os campos solicitados.
            Se algum campo não estiver explícito, infira quando possível ou deixe em branco.
            
            Nota Fiscal:
            {texto}
            """
        )
        
        formatted_prompt = prompt.format(
            format_instructions=format_instructions,
            texto=self.texto
        )
        
        resposta_llm = self.llm.invoke(formatted_prompt)
        
        try:
            nota_fiscal_estruturada = parser.parse(resposta_llm)
            return nota_fiscal_estruturada
        except Exception as e:
            print(f"Erro ao fazer parsing da resposta: {e}")
            print(f"Resposta original do LLM: {resposta_llm}")
            return None
            