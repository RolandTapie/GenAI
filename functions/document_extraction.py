from docling.document_converter import DocumentConverter
import re
from pdfminer.high_level import extract_text

class DoclingExtractor():

    def __init__(self, document_path):
        self.document=document_path
        self.doc=None
    def run(self):
        return self.extract_paragraphs(self.document)


    def docling_extraction(self,document):
        print(f"le document docling extraact {document}")
        #hf_tokenizer = AutoTokenizer.from_pretrained(self.model)
        converter = DocumentConverter()
        result = converter.convert(document)
        doc=result.document.export_to_text()
        self.doc=doc
        return doc

    def extract_paragraphs(self, document):
        #text = extract_text(document)
        text = self.docling_extraction(document)
        #raw_paragraphs = text.split('\n\n')
        #text = re.sub(r'-\n', '', text)
        text = re.sub(r'\n', '', text)
        raw_paragraphs = text.split('.')
        return [p.strip().replace('\n', ' ') for p in raw_paragraphs if len(p.strip()) > 40]

    def get_doc(self):
        return self.doc

    def get_meta(self):
        pass

    def traduct_en_fr(self):
        pass