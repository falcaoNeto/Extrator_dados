import json
import os

class JsonDocumentManager:
    """
    Classe para gerenciar as alterações nos arquivos JSON dos documentos.
    
    Para 'agua', o arquivo é um JSON contendo uma lista de atributos.
    Para 'nota', o arquivo é um JSON que, se vazio, será inicializado como [[], []]:
      - Índice 0: Atributos Gerais
      - Índice 1: Atributos de Produtos
    """
    def __init__(self, base_path="model"):
        self.base_path = base_path

    def get_file_path(self, doc_type):
        """Retorna o caminho do arquivo baseado no tipo de documento."""
        if doc_type.lower() == 'agua':
            return os.path.join(self.base_path, "agua.json")
        elif doc_type.lower() == 'nota':
            return os.path.join(self.base_path, "notaFiscal.json")
        else:
            raise ValueError("Documento inválido. Use 'agua' ou 'nota'.")

    def load_data(self, doc_type):
        """Carrega os dados do arquivo JSON correspondente.
        
        Se o documento for 'nota' e o arquivo estiver vazio, inicializa com [[], []].
        """
        file_path = self.get_file_path(doc_type)
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []

        # Se for nota fiscal e estiver vazio, inicializa com [[], []]
        if doc_type.lower() == 'nota' and (not data or data == []):
            data = [[], []]
            self.write_data(doc_type, data)
        return data

    def write_data(self, doc_type, data):
        """Grava os dados no arquivo JSON correspondente."""
        file_path = self.get_file_path(doc_type)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def add_attribute(self, doc_type, attribute, section=None):
        """
        Adiciona um novo atributo ao documento.
        
        Parâmetros:
          - doc_type: 'agua' ou 'nota'
          - attribute: string do novo atributo
          - section: para 'nota', informe 0 para Atributos Gerais ou 1 para Atributos de Produtos.
          
        Retorna o atributo adicionado.
        """
        data = self.load_data(doc_type)
        new_attr = {
            "index": None,  # será definido após contar os elementos atuais
            "type": "string",
            "description": attribute
        }
        
        if doc_type.lower() == "nota":
            if section is None or section not in [0, 1]:
                raise ValueError("Para nota fiscal, informe a seção: 0 (Geral) ou 1 (Produtos).")
            new_index = len(data[section])
            new_attr["index"] = new_index
            data[section].append(new_attr)
        else:  # 'agua'
            new_index = len(data)
            new_attr["index"] = new_index
            data.append(new_attr)
        
        self.write_data(doc_type, data)
        return new_attr

    def remove_attribute(self, doc_type, index, section=None):
        """
        Remove um atributo com base no index.
        
        Parâmetros:
          - doc_type: 'agua' ou 'nota'
          - index: número do atributo a ser removido
          - section: para 'nota', informe 0 para Atributos Gerais ou 1 para Atributos de Produtos.
          
        Retorna o atributo removido ou None se não encontrado.
        """
        data = self.load_data(doc_type)
        removed_attr = None
        
        if doc_type.lower() == "nota":
            if section is None or section not in [0, 1]:
                raise ValueError("Para nota fiscal, informe a seção: 0 (Geral) ou 1 (Produtos).")
            for i, item in enumerate(data[section]):
                if item.get("index") == index:
                    removed_attr = data[section].pop(i)
                    break
            # Reindexa os atributos restantes
            for idx, item in enumerate(data[section]):
                item["index"] = idx
        else:
            for i, item in enumerate(data):
                if item.get("index") == index:
                    removed_attr = data.pop(i)
                    break
            for idx, item in enumerate(data):
                item["index"] = idx

        self.write_data(doc_type, data)
        return removed_attr

# Bloco para testar todos os métodos
if __name__ == "__main__":
    # Instancia o gerenciador utilizando a pasta "model"
    manager = JsonDocumentManager("model")
    
    # Testando os métodos para "agua"
    print("=== Testando métodos para 'agua' ===")
    try:
        agua_data = manager.load_data("agua")
        print("Dados atuais (agua):", agua_data)
    except Exception as e:
        print("Erro ao carregar dados de agua:", e)
    
    # Adiciona um atributo para água
    new_attr_agua = manager.add_attribute("agua", "novo atributo água")
    print("\nAtributo adicionado (agua):", new_attr_agua)
    print("Dados após adição (agua):", manager.load_data("agua"))
    
    # Remove o atributo recém-adicionado
    removed_attr_agua = manager.remove_attribute("agua", new_attr_agua["index"])
    print("\nAtributo removido (agua):", removed_attr_agua)
    print("Dados após remoção (agua):", manager.load_data("agua"))
    
    # Testando os métodos para "nota"
    print("\n=== Testando métodos para 'nota' ===")
    try:
        nota_data = manager.load_data("nota")
        print("Dados atuais (nota):", nota_data)
    except Exception as e:
        print("Erro ao carregar dados de nota:", e)
    
    # Adiciona um atributo para "nota" na seção 0 (Atributos Gerais)
    new_attr_nota_geral = manager.add_attribute("nota", "novo atributo nota geral", section=0)
    print("\nAtributo adicionado em 'nota' (seção 0):", new_attr_nota_geral)
    print("Dados após adição (nota):", manager.load_data("nota"))
    
    # Adiciona um atributo para "nota" na seção 1 (Atributos de Produtos)
    new_attr_nota_prod = manager.add_attribute("nota", "novo atributo nota produto", section=1)
    print("\nAtributo adicionado em 'nota' (seção 1):", new_attr_nota_prod)
    print("Dados após adição (nota):", manager.load_data("nota"))
    
    # Remove o atributo da seção 0
    removed_attr_nota_geral = manager.remove_attribute("nota", new_attr_nota_geral["index"], section=0)
    print("\nAtributo removido em 'nota' (seção 0):", removed_attr_nota_geral)
    print("Dados após remoção (nota):", manager.load_data("nota"))
    
    # Remove o atributo da seção 1
    removed_attr_nota_prod = manager.remove_attribute("nota", new_attr_nota_prod["index"], section=1)
    print("\nAtributo removido em 'nota' (seção 1):", removed_attr_nota_prod)
    print("Dados após remoção (nota):", manager.load_data("nota"))
