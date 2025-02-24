from docling.document_converter import DocumentConverter




class DocumentConverter:
    def convert(self, source):
        converter = DocumentConverter()
        result = converter.convert(source)
        final = result.document.export_to_dict()
        return final



if __name__ == "__main__":
    converter = DocumentConverter()
    converter.convert("Especificacao Prefeitura Municipal de Vale do Anari.pdf ")