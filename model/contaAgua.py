from langchain.prompts import PromptTemplate
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import Field, create_model
import sqlite3
import json
from model.LLm import LLm

class ContaAgua:
    def __init__(self):
        
        self.llm = LLm().llm_instance("gemini")

    def extrair_conta_agua(self, texto):
        with open('view/agua.json') as f:
            dadosCOntaAgua = json.load(f)

        # Definir atributos fixos
        atributos_fixos = {
            "Mes_de_referencia": (str, Field(description="mes de referÊcia da conta, retorne no formato YYYY-MM-01")),
            "valor_total": (float, Field(description="Valor total da conta")),
            "Consumo_faturado": (float, Field(description="Extraia exatamente o número do consumo faturado sem alterar seu formato"))
        }

        atributos_dinamicos = {
            dado["description"]: (str, Field(description=dado["description"]))
            for dado in dadosCOntaAgua
        }

        campos = {**atributos_fixos, **atributos_dinamicos}

        DinamicModel = create_model("ContaAgua", **campos)

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
            texto=texto
        )
        
        resposta_llm = self.llm.invoke(formatted_prompt)
        
        try:
            json_text = resposta_llm.content.split("```json")[1].split("```")[0].strip()
            dados_json = json.loads(json_text)
            return dados_json
        except Exception as e:
            print(f"Erro ao fazer parsing da resposta: {e}")
            print(f"Resposta original do LLM: {resposta_llm}")
            return None
    
    def salvar_conta_agua(self, dados):
        conector = sqlite3.connect("BD/database.db")
        cursor = conector.cursor()
        
        cursor.execute("""
        INSERT INTO ContaAgua (Mes_de_Referencia, valor_total, Consumo_Faturado) 
        VALUES (?, ?, ?) RETURNING id
    """, (dados['Mes_de_referencia'], dados['valor_total'], dados['Consumo_faturado']))


        id_contaagua = cursor.fetchone()[0]
        
        if len(dados) > 3:
            chaves = list(dados.keys())
            valores = list(dados.values())

            for i in range(3, len(dados)):
                cursor.execute("INSERT INTO ContaAguaDinamico (ContaAgua_id, chave, valor) VALUES (?, ?, ?)",
                            (id_contaagua, chaves[i], valores[i]))
        conector.commit()
        return True

