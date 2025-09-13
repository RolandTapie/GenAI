from docling.document_converter import DocumentConverter
from src.services.logs.loggers import log

from docling.chunking import HybridChunker
import re

class DoclingExtractor():

    def __init__(self, document_path, sep):
        self.document=document_path
        self.doc=None
        self.meta = None
        self.chunker=None
        self.sep = sep

    def get_document(self):
        return self.document

    def run(self):
        """Réaliser le pipeline de chunckage et de vectorization"""
        return self.extract_paragraphs(self.document, self.sep), self.meta



    def docling_extraction(self,document):
        """extraction des documents avec Docling"""
        #hf_tokenizer = AutoTokenizer.from_pretrained(self.model)
        converter = DocumentConverter()
        result = converter.convert(document)
        doc=result.document.export_to_text()
        #print(doc)
        self.doc=doc
        self.meta="meta test"
        return doc

    def chunk_by_chars(self, text, chunk_size=500):
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    def extract_paragraphs(self, document, sep):
        """Création des chunks à vectoriser"""

        text = self.docling_extraction(document)

        if text != "":
            #raw_paragraphs = text.split('\n\n')
            #text = re.sub(r'-\n', '', text)
            #text = re.sub(r'\n', '', text)
            #raw_paragraphs = text.split('.')
            if isinstance(sep, (int, float)):
                return self.chunk_by_chars(text,sep)

            raw_paragraphs = text.split(sep)
            result = [p.strip().replace('\n', ' ') for p in raw_paragraphs if len(p.strip()) > 40]
            log(f" le resultat de l'extraction : {len(result)} chunks")
            return result
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