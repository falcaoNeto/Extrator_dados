from agent import LangChainOllamaChain

chain_instance = LangChainOllamaChain(dado="a casa do senhor sergio é veremelha")
resposta = chain_instance.ask("qual é a cor da casa do senhor sergio?")
print(resposta)