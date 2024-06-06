import os
import pickle
import openai
import numpy as np

class EmbeddingsGenerator:
    def __init__(self, processed_chunks_dir="./processed_chunks", embeddings_dir="./embeddings"):
        self.processed_chunks_dir = processed_chunks_dir
        self.embeddings_dir = embeddings_dir
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def load_processed_chunks(self):
        with open(os.path.join(self.processed_chunks_dir, "processed_chunks.pkl"), "rb") as f:
            processed_chunks = pickle.load(f)
        return processed_chunks

    def embed_text(self, text):
        response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
        embedding = response['data'][0]['embedding']
        return np.array(embedding)

    def generate_embeddings(self):
        processed_chunks = self.load_processed_chunks()
        embeddings = {}

        for file_path, chunks in processed_chunks.items():
            file_embeddings = []
            for chunk in chunks:
                embedding = self.embed_text(chunk)
                file_embeddings.append(embedding)
            embeddings[file_path] = file_embeddings
            print(f"Generated embeddings for {file_path}")

        self.save_embeddings(embeddings)
        return embeddings

    def save_embeddings(self, embeddings):
        os.makedirs(self.embeddings_dir, exist_ok=True)
        with open(os.path.join(self.embeddings_dir, "embeddings.pkl"), "wb") as f:
            pickle.dump(embeddings, f)
        print("Saved embeddings to file")

    def load_embeddings(self):
        with open(os.path.join(self.embeddings_dir, "embeddings.pkl"), "rb") as f:
            embeddings = pickle.load(f)
        return embeddings

if __name__ == "__main__":
    generator = EmbeddingsGenerator()
    generator.generate_embeddings()
