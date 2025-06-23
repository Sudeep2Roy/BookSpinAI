import chromadb
from chromadb.utils import embedding_functions

class VersionManager:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.ef = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name="book_versions",
            embedding_function=self.ef
        )
    
    def save_version(self, content, metadata):
        version_id = f"version_{len(self.collection.peek())}"
        self.collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[version_id]
        )
        return version_id