import os
import sys
import json
import time

# Ensure backend root is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.chromadb_client import ChromaDBClient

def seed_database():
    print("Starting ChromaDB database seeding...")
    
    # Wait for ChromaDB to be reachable
    retries = 10
    client = None
    while retries > 0:
        try:
            client = ChromaDBClient()
            # Attempt a dummy call to verify connection
            client.client.list_collections()
            print("Connected to ChromaDB successfully!")
            break
        except Exception as e:
            print(f"Waiting for ChromaDB server... ({10 - retries + 1}/10) Error: {e}")
            time.sleep(2)
            retries -= 1
            
    if not client:
        print("Could not connect to ChromaDB. Seeding aborted.")
        return

    # Load sample transcripts
    json_path = os.path.join(os.path.dirname(__file__), "sample_transcripts.json")
    if not os.path.exists(json_path):
        print(f"Error: Seeding JSON file not found at {json_path}")
        return
        
    with open(json_path, "r") as f:
        transcripts = json.load(f)
        
    documents = []
    metadatas = []
    ids = []
    
    for item in transcripts:
        documents.append(item["content"])
        metadatas.append({
            "title": item["title"],
            "type": item["type"],
            "source": item["source"]
        })
        ids.append(item["id"])
        
    try:
        client.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Successfully seeded {len(documents)} documents into ChromaDB!")
    except Exception as e:
        print(f"Error seeding ChromaDB: {e}")

if __name__ == "__main__":
    seed_database()
