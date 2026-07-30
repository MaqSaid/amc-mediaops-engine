import os
import chromadb
from chromadb.utils import embedding_functions

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8000))

class ChromaDBClient:
    def __init__(self):
        # Connect to ChromaDB server
        self.client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        # Using default chroma embedding function (runs locally)
        self.emb_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection_name = "nine_editorial_archive"

    def get_collection(self):
        return self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.emb_fn
        )

    def add_documents(self, documents: list[str], metadatas: list[dict], ids: list[str]):
        collection = self.get_collection()
        collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def query_documents(self, query_text: str, n_results: int = 3, filter_dict: dict = None):
        collection = self.get_collection()
        try:
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=filter_dict
            )
            
            # Format results into a list of dicts
            formatted = []
            if results and results["documents"]:
                for idx in range(len(results["documents"][0])):
                    formatted.append({
                        "document": results["documents"][0][idx],
                        "metadata": results["metadatas"][0][idx] if results["metadatas"] else {},
                        "id": results["ids"][0][idx],
                        "distance": results["distances"][0][idx] if "distances" in results and results["distances"] else 0.0
                    })
            return formatted
        except Exception as e:
            print(f"Error querying ChromaDB: {e}")
            return []
