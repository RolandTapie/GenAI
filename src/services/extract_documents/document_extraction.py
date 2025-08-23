from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker
import re

class DoclingExtractor():

    def __init__(self, document_path):
        self.document=document_path
        self.doc=None
        self.meta = None
        self.chunker=None
    def run(self):
        """Réaliser le pipeline de chunckage et de vectorization"""
        return self.extract_paragraphs(self.document), self.meta



    def docling_extraction(self,document):
        """extraction des documents avec Docling"""
        #hf_tokenizer = AutoTokenizer.from_pretrained(self.model)
        converter = DocumentConverter()
        result = converter.convert(document)
        doc=result.document.export_to_text()
        print("le document")
        print(doc)
        self.doc=doc
        self.meta="meta test"
        return doc

    def extract_paragraphs(self, document):
        """Création des chunks à vectoriser"""
        #text = extract_text(document)
        text = self.docling_extraction(document)
        if text != "":
            #raw_paragraphs = text.split('\n\n')
            text = re.sub(r'-\n', '', text)
            text = re.sub(r'\n', '', text)
            #raw_paragraphs = text.split('.')
            raw_paragraphs = text.split('\n\n')
            return [p.strip().replace('\n', ' ') for p in raw_paragraphs if len(p.strip()) > 40]
        else:
            raise Exception(f"aucune donnée extraite du document {document}")


    def get_doc(self):
        return self.doc

    def get_chunks(self):
        return self.chunker

    def get_meta(self):
        return self.meta

    def traduct_en_fr(self):
        pass