import os
import pickle
from pdfminer.high_level import extract_text
from llama_index.core import Document


class PDFReader:
    def __init__(self, input_dir, chunk_size=512, save_dir="./processed_chunks"):
        self.input_dir = input_dir
        self.chunk_size = chunk_size
        self.save_dir = save_dir

    def load_data(self):
        docs = []
        processed_chunks = self.load_processed_chunks()
        for root, _, files in os.walk(self.input_dir):
            for file in files:
                if file.endswith(".pdf"):
                    file_path = os.path.join(root, file)
                    if file_path in processed_chunks:
                        chunks = processed_chunks[file_path]
                        print(f"Loaded {len(chunks)} processed chunks for {file_path}")
                    else:
                        with open(file_path, "rb") as f:
                            pdf_content = self.extract_text_from_pdf(f)
                            print(f"Extracted text from {file_path}")
                            chunks = self.chunk_text(pdf_content)
                            processed_chunks[file_path] = chunks
                            self.save_processed_chunks(processed_chunks)
                            print(f"Created {len(chunks)} chunks for {file_path}")
                    for i, chunk in enumerate(chunks):
                        doc = Document(text=chunk, extra_info={"file_path": file_path, "chunk_id": i})
                        docs.append(doc)
        return docs

    def extract_text_from_pdf(self, file):
        extracted_text = extract_text(file)
        print("Extracted text from PDF")
        return extracted_text

    def chunk_text(self, text):
        # Split text into chunks of size `self.chunk_size`
        words = text.split()
        chunks = [' '.join(words[i:i + self.chunk_size]) for i in range(0, len(words), self.chunk_size)]
        print(f"Chunked text into {len(chunks)} chunks")
        return chunks

    def save_processed_chunks(self, processed_chunks):
        os.makedirs(self.save_dir, exist_ok=True)
        with open(os.path.join(self.save_dir, "processed_chunks.pkl"), "wb") as f:
            pickle.dump(processed_chunks, f)
        print("Saved processed chunks to file")

    def load_processed_chunks(self):
        try:
            with open(os.path.join(self.save_dir, "processed_chunks.pkl"), "rb") as f:
                processed_chunks = pickle.load(f)
            print("Loaded processed chunks from file")
            return processed_chunks
        except FileNotFoundError:
            return {}
