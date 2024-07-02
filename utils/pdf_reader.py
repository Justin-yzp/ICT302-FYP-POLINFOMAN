import os
import pickle
import logging
import fitz  # PyMuPDF
from llama_index.core import Document
import nltk
from nltk.tokenize import word_tokenize

class PDFReader:
    def __init__(self, input_dir, chunk_size=100, overlap_size=20, save_dir="./processed_chunks"):
        self.input_dir = input_dir
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        self.save_dir = save_dir
        nltk.download('punkt', quiet=True)  # Download the punkt tokenizer for sentence splitting
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def load_data(self):
        docs = []
        processed_chunks = self.load_processed_chunks()
        for root, _, files in os.walk(self.input_dir):
            for file in files:
                if file.endswith(".pdf"):
                    file_path = os.path.join(root, file)
                    try:
                        current_mod_time = os.path.getmtime(file_path)
                        cache_key = f"{file_path}_{self.chunk_size}_{self.overlap_size}"
                        if cache_key not in processed_chunks or processed_chunks[cache_key]["mod_time"] < current_mod_time:
                            pdf_content = self.extract_text_from_pdf(file_path)
                            self.logger.info(f"Extracted text from {file_path}")
                            chunks = self.chunk_text(pdf_content)
                            processed_chunks[cache_key] = {
                                "chunks": chunks,
                                "mod_time": current_mod_time
                            }
                            self.save_processed_chunks(processed_chunks)
                            self.logger.info(f"Created {len(chunks)} chunks for {file_path}")
                        else:
                            chunks = processed_chunks[cache_key]["chunks"]
                            self.logger.info(f"Loaded {len(chunks)} processed chunks for {file_path}")
                        for i, chunk in enumerate(chunks):
                            doc = Document(text=chunk, extra_info={"file_path": file_path, "chunk_id": i})
                            docs.append(doc)
                    except Exception as e:
                        self.logger.error(f"Error processing {file_path}: {e}")
        return docs

    def extract_text_from_pdf(self, file_path):
        doc = fitz.open(file_path)
        text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
        doc.close()
        self.logger.info("Extracted text from PDF")
        return text

    def chunk_text(self, text):
        words = word_tokenize(text)
        chunks = []
        start = 0
        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunk = ' '.join(words[start:end])
            chunks.append(chunk)
            start += self.chunk_size - self.overlap_size
        self.logger.info(f"Chunked text into {len(chunks)} chunks")
        return chunks

    def save_processed_chunks(self, processed_chunks):
        os.makedirs(self.save_dir, exist_ok=True)
        with open(os.path.join(self.save_dir, "processed_chunks.pkl"), "wb") as f:
            pickle.dump(processed_chunks, f)
        self.logger.info("Saved processed chunks to file")

    def load_processed_chunks(self):
        try:
            with open(os.path.join(self.save_dir, "processed_chunks.pkl"), "rb") as f:
                processed_chunks = pickle.load(f)
            self.logger.info("Loaded processed chunks from file")
            return processed_chunks
        except FileNotFoundError:
            return {}