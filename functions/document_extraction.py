from docling.document_converter import DocumentConverter
import re

class DoclingExtractor():

    def __init__(self, document_path):
        self.document=document_path

    def run(self):
        return self.extract_paragraphs(self.document)


    def docling_extraction(self,document):
        #hf_tokenizer = AutoTokenizer.from_pretrained(self.model)
        converter = DocumentConverter()
        result = converter.convert(document)
        doc=result.document.export_to_text()

        return doc

    def extract_paragraphs(self, document):
        #text = extract_text(document)
        text = self.docling_extraction(document)
        #raw_paragraphs = text.split('\n\n')
        text = re.sub(r'-\n', '', text)
        text = re.sub(r'\n', '', text)
        raw_paragraphs = text.split('.')
        return [p.strip().replace('\n', ' ') for p in raw_paragraphs if len(p.strip()) > 40]
