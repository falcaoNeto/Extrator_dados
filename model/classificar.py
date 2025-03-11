from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from model.LLm import LLm
class Texto(BaseModel):
    result: str = Field(description="Classificar o texto entre(NotaFiscal, ContaAgua, NenhumOutro)")


class Classificar:
    def __init__(self, texto):
        self.texto = texto
        self.llm = LLm().llm_instance("gemini")
        
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
        
        response = self.llm.invoke(format_prompt)
        
        if hasattr(response, 'content'):
            result_text = response.content  
        else:
            result_text = str(response)     
        
        result2 = parser.parse(result_text)
        return result2.result
    

if __name__ == "__main__":
    texto = "conta de agua, valor 120 reais e consumo de 45 m3"
    classificar = Classificar(texto)
    print(classificar.classificar_texto())