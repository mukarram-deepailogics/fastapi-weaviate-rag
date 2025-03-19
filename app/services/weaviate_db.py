import weaviate
import os
import sys
import uuid
import hashlib
from weaviate.auth import AuthApiKey
from weaviate.classes.config import DataType, Property, Configure, VectorDistances

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from app.services.utils import chunk_document  # ✅ Import chunking function

# Environment variables
WCD_URL = os.getenv("WCD_URL")
WCD_API_KEY = os.getenv("WCD_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def create_weaviate_schema():
    class_name = "DocumentChunk"

    with weaviate.connect_to_weaviate_cloud(
        cluster_url=WCD_URL,
        auth_credentials=AuthApiKey(WCD_API_KEY),
        headers={"X-OpenAI-Api-Key": OPENAI_API_KEY},
    ) as client:
        if client.collections.exists(class_name):
            print(f"Class {class_name} already exists")
            return

        client.collections.create(
            name=class_name,
            properties=[
                Property(name="content", data_type=DataType.TEXT),
                Property(name="chunk_index", data_type=DataType.INT, index_inverted=False),
                Property(name="page_number", data_type=DataType.INT, index_inverted=False),
                Property(name="document_id", data_type=DataType.TEXT, index_inverted=False),
            ],
            vectorizer_config=Configure.Vectorizer.text2vec_openai(),
            vector_index_config=Configure.VectorIndex.hnsw(
                distance_metric=VectorDistances.COSINE  # ✅ Correct way to set distance
            ),
        )
        print(f"Created {class_name} class")

def generate_chunk_id(document_id: str, chunk_index: int) -> str:
    """Generate deterministic UUID for chunk"""
    unique_str = f"{document_id}_{chunk_index}"
    return str(uuid.UUID(hashlib.md5(unique_str.encode()).hexdigest()))

def insert_chunks_into_weaviate(content: str, document_id: str, chunk_size: int, overlap: int):
    """Insert document chunks into Weaviate"""
    chunks = chunk_document(content, chunk_size, overlap)  # ✅ Use function from utils
    
    with weaviate.connect_to_weaviate_cloud(
        cluster_url=WCD_URL,
        auth_credentials=AuthApiKey(WCD_API_KEY),
        headers={"X-OpenAI-Api-Key": OPENAI_API_KEY}
    ) as client:
        collection = client.collections.get("DocumentChunk")
        
        for idx, chunk in enumerate(chunks):
            chunk_data = {
                "content": chunk["content"],  # ✅ Fix key name (not "text")
                "chunk_index": idx,
                "page_number": chunk.get("page_number", 0),
                "document_id": document_id
            }
            
            collection.data.insert(
                properties=chunk_data,
                uuid=generate_chunk_id(document_id, idx)
            )
        print(chunk_data)
if __name__ == "__main__":
    create_weaviate_schema()
