dadosCOntaAgua = {
    "data_de_vencimento": (
        str, "Data de vencimento da fatura"),
    "valor_total_da_fatura": (
        float, "Valor total da fatura"),
    "valor_de_encargos_multas": (
        float, "Valor de encargos/multas (caso haja atraso)"),
    "mes_de_referencia": (
        str, "Mês de referência"),
    "consumo": (
        float, "Consumo registrado em m3"),
    "endereco": (
        str, "endereço do cliente")
}




from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import Field, create_model


load_dotenv()
KEY_API = os.getenv("GOOGLE_API_KEY")

campos = {
    dado: (tipo, Field(description=descricao))  
    for dado, (tipo, descricao) in dadosCOntaAgua.items()
}

DinamicModel = create_model(
    "ContaAgua",
    **campos  
)

    
class ContaAgua:
    def __init__(self, texto, model="gemini-1.5-flash", api_key=KEY_API):
        self.texto = texto
        self.llm = GoogleGenerativeAI(model=model, api_key=api_key)

    def extrair_conta_agua(self):
        parser = PydanticOutputParser(pydantic_object=DinamicModel)
        
        format_instructions = parser.get_format_instructions()
        
        prompt = PromptTemplate.from_template(
            """Extraia os seguintes dados da conta de agua abaixo:
            
            {format_instructions}
            
            Analise cuidadosamente o texto da conta de agua e extraia os campos solicitados.
            Se algum campo não estiver explícito, infira quando possível ou deixe em branco.
            
            conta de agua:
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
    


    