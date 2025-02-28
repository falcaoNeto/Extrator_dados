from pydantic import BaseModel, create_model, Field


class ContaAgua(BaseModel):
    data_de_vencimento: str = Field(description="Data de vencimento da fatura")
    valor_total_da_fatura: float = Field(description="Valor total da fatura")
    valor_de_encargos_multas: float = Field(description="Valor de encargos/multas (caso haja atraso)")
    mes_de_referencia: str = Field(description="Mês de referência")
    consumo_registrado_em_m3: float = Field(description="Consumo registrado em m3")




dadosCOntaAgua = {
    "data_de_vencimento": (
        str, "Data de vencimento da fatura"),
    "valor_total_da_fatura": (
        float, "Valor total da fatura"),
    "valor_de_encargos_multas": (
        float, "Valor de encargos/multas (caso haja atraso)"),
    "mes_de_referencia": (
        str, "Mês de referência"),
    "consumo_registrado_em_m3": (
        float, "Consumo registrado em m3"),
}



campos = {
    dado: (tipo, Field(description=descricao))  
    for dado, (tipo, descricao) in dadosCOntaAgua.items()
}

# Cria o modelo
DinamicModel = create_model(
    "ContaAgua",
    **campos  # Desempacota o dicionário de campos
)


print(DinamicModel.__fields__)