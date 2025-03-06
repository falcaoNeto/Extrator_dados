
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import  Field, create_model
from typing import List
import json


load_dotenv()
KEY_API = os.getenv("GOOGLE_API_KEY")


class NotaFiscal:
    def __init__(self, texto, model="gemini-1.5-flash", api_key=KEY_API):
        self.texto = texto
        self.llm = GoogleGenerativeAI(model=model, api_key=api_key)
        

    def extrair_nota_fiscal(self, campo_extra=None):
        with open('view/notaFiscal.json') as f:
            dadosNotaFiscal = json.load(f)
        camposProdutos = {
            dado["description"]: (str, Field(description=dado["description"]))  
            for dado in dadosNotaFiscal[1]
        }
        DinamicModelProdutos = create_model(    
            "Produtos",
            **camposProdutos
        )
        camposNotaFiscal = {
            dado["description"]: (str, Field(description=dado["description"]))  
            for dado in dadosNotaFiscal[0]
        }
        camposNotaFiscal["produtos"] = (List[DinamicModelProdutos], Field(description="Lista de produtos na nota fiscal"))
        DinamicModelNotaFiscal = create_model(
            "NotaFiscal",  
            **camposNotaFiscal
)

        parser = PydanticOutputParser(pydantic_object=DinamicModelNotaFiscal)
        
    
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
            json_text = resposta_llm.split("```json")[1].split("```")[0].strip()
            dados_json = json.loads(json_text)
            return dados_json
        except Exception as e:
            print(f"Erro ao fazer parsing da resposta: {e}")
            print(f"Resposta original do LLM: {resposta_llm}")
            return None
        


if __name__ == "__main__":
    text = """N°693983

DATA DE RECEBIMENTO

IDENTIFICA˙ˆO E ASSINATURA DO RECEBEDOR

## NF-e

25 SÉRIE

RECEBEMOS DE MAGAZINE LUIZA S/A OS PRODUTOS CONSTANTES DA NOTA FISCAL INDICADA ABAIXO

## MAGAZINE LUIZA S/A

ROD BANDEIRANTES S/N, 0 KM 68 E 760 METROS S - RIO ABAIXO LOUVEIRA - SP - CEP: 13290000

NATUREZA DA OPERA˙ˆO

VENDA MERCADORIA  ADQUIR/RECEB TERCEIROS TP:51

INSCRI˙ˆO ESTADUAL

INSC.ESTADUAL DO SUBST. TRIBUT'RIO

CNPJ

## DANFE

DOCUMENTO AUXILIAR DA NOTA FISCAL ELETRÔNICA

0 - ENTRADA 1 - SA˝DA 1

693983 N°

25 SÉRIE

FOLHA 1/ 1

<!-- image -->

CHAVE DE ACESSO

3519 0547 9609 5008 9785 5502 5000 6939 8310 5123 1858

Consulta de autenticidade no portal nacional da NF-e www.nfe.fazenda.gov.br/portal ou no site da Sefaz Autorizadora

PROTOCOLO DE AUTORIZA˙ˆO DE USO

135190361212099 21/05/2019 15:25:00

1

VOLUMES

FONE/FAX

11976643126

- Nœm. Duplicata/Parcela

Vencimento

Valor

- Nœm. Duplicata/Parcela

Vencimento

Valor

0,00

BASE DE C'LCULO DO ICMS ST

VALOR DO ICMS ST

VALOR APROXIMADO DOS TRIBUTOS

0,00

OUTRAS DESPESAS ACESSÓRIAS

0,00

0,00

VALOR DO IPI

PLACA DO VE"CULO

CNPJ / CPF

0,00

0,00

UF

UF

INSCRI˙ˆO ESTADUAL

PESO BRUTO

PESO L"QUIDO

4.000

4.000

## DADOS DO PRODUTO / SERVI˙O

| COD.PROD.   | DADOS DO PRODUTO / SERVIÇOS DESCRI˙ˆO DO PRODUTO / SERVI˙O                                                 | NCM/SH CST   | CFOP UNID   | QTDE   | VL. UNIT'RIO   | VL. TOTAL   | VL.           | BC.ICMS   | VL. ICMS   | V. IPI   | AL"Q. IPI AL"Q. ICMS   |
|-------------|------------------------------------------------------------------------------------------------------------|--------------|-------------|--------|----------------|-------------|---------------|-----------|------------|----------|------------------------|
|             |                                                                                                            | 84713019 460 | 5405 PC     | 1.0000 | 3,254.0700     | 3.254,07    | DESCONTO 0,00 |           |            |          |                        |
| 5763764     | NOTEBOOK CI7 8GB 2TB 2GB W10 3576-A70C CINZA NA VLR BC-ST RETIDO R$ 2821,85 / VLR ICMS-ST RETIDO R$ 117,42 |              |             |        |                |             |               |           |            |          |                        |

## C'LCULO DO ISSQN

INSCRI˙ˆO MUNICIPAL

VALOR TOTAL DOS SERVI˙OS

BASE DE C'LCULO DO ISSQN

VALOR DO ISSQN

## DADOS ADICIONAIS

INFORMA˙ÕES COMPLEMENTARES

Valores totais do ICMS Interestadual: DIFAL da UF destino R$0,00 + FCP R$0,00; DIFAL da UF origem R$0,00.

Inf. Contribuinte: Val Aprox Tributos R$824,26(25,33%) Fonte:IBPT FEDERAIS 13,33%,ESTADUAIS 12,00%,MUNICIPAIS 0%/BC. RED. ART. 27, INCISO I, ANEXO II, RESOL. SF 14/13BC. RED. ART. 27, INCISO I, ANEXO II, RESOL. SF 14/13ICMS RET. POR ST CFE 313-Z19/NUM. PEDIDO:496581204 / CODCLI:19773157 / LOTE:1685932 / CODVENDR:6001 / OBS.PED:REF.:  (11 ) 976643126/ENDERECO LOJA ENTREGA: DOUTOR EDUARDO COTCHING 2130 BAIRRO VILA FORMOSA SAO PAULO SP / MODAL: RLE

RESERVADO AO FISCO

0,00

VALOR TOTAL DOS PRODUTOS

3.254,07

VALOR TOTAL DA NOTA

421021117115

47.960.950/0897-85

DESTINAT'RIO / REMETENTE

NOME/RAZˆO SOCIAL

OLLYVER OTTOBONI

ENDERE˙O

BAIRRO / DISTRITO

CEP

ANTONIO BORGES DA FONSECA 39

MUNIC"PIO

SAO PAULO

FATURA / DUPLICATAS

FATURA

Nœm. Duplicata/Parcela

Vencimento

Valor

## C'LCULO DO IMPOSTO

BASE DE C'LCULO DO ICMS

VALOR DO ICMS

VALOR DO FRETE

0,00

VALOR DO SEGURO

DESCONTO

0,00

TRANSPORTADOR / VOLUMES TRANSPORTADOS DADOS

RAZˆO SOCIAL

FRETE POR CONTA

CÓDIGO ANTT

ENDERE˙O

QUANTIDADE

0 - Emitente

MUNIC"PIO

JD FLORESTA

04836-120

UF SP

CNPJ/CPF

DATA DA EMISSˆO

21/05/2019

DATA DA SA"DA/ENTRADA

21/05/2019

HORA DE SA"DA/ENTRADA

16:24:33-03:00

ESPÉCIE

MARCA

NUMERA˙ˆO

0,00

0,00

126.295.868-71

INSCRI˙ˆO ESTADUAL

3.254,07"""
    extrai = NotaFiscal(text)
    result = extrai.extrair_nota_fiscal()
    if os.path.exists("BD/NotaFiscalBD.json") and os.path.getsize("BD/NotaFiscalBD.json") > 0:
        with(open("BD/NotaFiscalBD.json", "r+")) as f:
                dados = json.load(f)
                dados.append(result)
                f.seek(0)
                json.dump(dados, f, ensure_ascii=False, indent=2)
    else:
        with open("BD/NotaFiscalBD.json", "w", encoding="utf-8") as f:
            json.dump([result], f, ensure_ascii=False, indent=2)
    print(result)

            