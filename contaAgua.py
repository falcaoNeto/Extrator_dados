from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import Field, create_model

import json



load_dotenv()
KEY_API = os.getenv("GOOGLE_API_KEY")



    
class ContaAgua:
    def __init__(self, texto, model="gemini-1.5-flash", api_key=KEY_API):
        self.texto = texto
        self.llm = GoogleGenerativeAI(model=model, api_key=api_key)

    def extrair_conta_agua(self):
        with open('view/agua.json') as f:
            dadosCOntaAgua = json.load(f)

        campos = {
        dado["description"]: (str, Field(description=dado["description"]))  
        for dado in dadosCOntaAgua
        }

        DinamicModel = create_model(
            "ContaAgua",
            **campos  
        )

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
            json_text = resposta_llm.split("```json")[1].split("```")[0].strip()
            dados_json = json.loads(json_text)
            return dados_json
        except Exception as e:
            print(f"Erro ao fazer parsing da resposta: {e}")
            print(f"Resposta original do LLM: {resposta_llm}")
            return None
    


if __name__ == "__main__":
    texto = """<!-- image -->

13 d0 Julho

49020

VALOR A PAGAR

16/12/2024

12/2024

MÊS REFERENCIA

VENCIMENTO

CONSUMO FATURADO

R$ 196,50

<!-- image -->

<!-- image -->

16 m3

VALOR DE AGUA

VALOR DE ESGOTO

VALOR DO JUROS

VALOR DA MULTA

## SIMONI POSSARI

RUA MARIZE ALMEIDA SANTOS 521 - LUZIA - ARACAJU - -ARACAJU -

49045500

EDF S AP 101

<!-- image -->

MATRICULA

## 0005036852

2ª Via

| Leit. Anterior           | 2682       |
|--------------------------|------------|
| Leit. Atual              | 2698       |
| Media Consumo (m3)       | 16         |
| Ocorrência de leitura    | -          |
| Data de Leit. Anterior   | 04/11/2024 |
| Dias de consumo          | 32         |
| Média diária             | 0,50       |
| Previsão para Prox. Leit | 03/01/2025 |
| Previsão de Tributos(R$) |            |

Serviços

107,00

1,08

2,82

Informações complementares

## MENSAGEM

APONTE A CAMERA DO SEU CELULAR NO QR CODE ABAIXO

E PAGUE SUA FATURA COM PIX PELO APP DO SEU BANCO.

A07N537222

04/12/2024 DATA DE LEITURA

RES:1 COM:0 IND:0  PUB:0

NOV/2024 00021 AGO/2024 00016

OUT/2024 00013 JUL/2024 00015

SET/2024 00014 JUN/2024 00014

REF

(M³)

REF

(M³)

HIDRÔMETRO

HISTÓRICO DE CONSUMO

CLASSIFICAÇãO ECONOMIAS

125930373

ART. 50 INCISO

| Parametro                                                      |   Turbidez | Cor   | Cloro   |    | Coliforme   | Escherichia   |
|----------------------------------------------------------------|------------|-------|---------|----|-------------|---------------|
| Nº Mínimo de Amostras Exigidas                                 |        247 | 247   | 247     | 0  | 247         | 247           |
| Nº de Amostras Analisadas                                      |          0 |       |         |    | 0           | 0             |
| Nº Mínimo de Amostras em Conformidade  com Portaria 2.914/2011 |          0 | 0     | 0       | 0  |             |               |

IDENTIFICADOR PARA DEBITO AUTOMATICO : 0005036852

<!-- image -->

Comprovante da DESO

0005036852 Matricula

16/12/2024

12/2024

R$ 196,50

Vencimento

Total a pagar RS

PAGUE COM PIX

<!-- image -->

82650000001-1   96500041012-0   59303730000-5   50368520012-6

<!-- image -->

125.930.373

2ª Via"""
    with open("arquivooo.json", "r", encoding="utf-8") as f:
        dados = json.load(f)
    
    
    classificar = ContaAgua(dados)
    result = classificar.extrair_conta_agua()
    if os.path.exists("BD/ContaAguaBD.json") and os.path.getsize("BD/ContaAguaBD.json") > 0:
        with(open("BD/ContaAguaBD.json", "r+")) as f:
                dados = json.load(f)
                dados.append(result)
                f.seek(0)
                json.dump(dados, f, ensure_ascii=False, indent=2)
    else:
        with open("BD/ContaAguaBD.json", "w", encoding="utf-8") as f:
            json.dump([result], f, ensure_ascii=False, indent=2)
    print(result)