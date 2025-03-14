import weaviate
import os
from weaviate.auth import AuthApiKey
from weaviate.classes.config import DataType, Property, Configure, VectorDistances
from app.services.utils import chunk_document
import uuid
import hashlib

wcd_url = os.getenv("WCD_URL")
wcd_api_key = os.getenv("WCD_API_KEY")

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=wcd_url,
    auth_credentials=AuthApiKey(wcd_api_key),
)

def create_weaviate_schema():
    class_name = "DocumentChunk"

    try:
        if client.collections.exists(class_name):
            print(f"Class '{class_name}' already exists in Weaviate.")
            return

        client.collections.create(
            name=class_name,
            properties=[
                Property(name="content", data_type=DataType.TEXT),
                Property(name="chunk_index", data_type=DataType.INT),
                Property(name="page_number", data_type=DataType.INT),
                Property(name="document_id", data_type=DataType.TEXT, index_inverted=False)
            ],
            vectorizer_config=None,  # No auto-vectorization
            vector_index_config=Configure.VectorIndex.hnsw(
                distance_metric=VectorDistances.COSINE
            )
        )

        print(f"Class '{class_name}' created successfully.")

    except Exception as e:
        print(f"Error while creating schema: {e}")

#if __name__ == "__main__":
#    create_weaviate_schema()
#    client.close()

def generate_uuid_from_id(document_id: str, chunk_index: int) -> str:
    """Generate a UUID based on Firestore document ID and chunk index."""
    unique_str = f"{document_id}_{chunk_index}"
    return str(uuid.UUID(hashlib.md5(unique_str.encode()).hexdigest()))
    
def insert_chunks_into_weaviate(document_content: str, document_id: str, chunk_size: int, overlap: int):
    create_weaviate_schema()
    
    chunks = chunk_document(document_content, chunk_size, overlap)
    
    if not chunks:
        print("No chunks generated.")
        return

    collection = client.collections.get("DocumentChunk")

    for i, chunk in enumerate(chunks):
        chunk["document_id"] = document_id
        
        print(f"Inserting chunk {i}: {chunk}")

        try:
            collection.data.insert(
                properties=chunk,
                uuid=generate_uuid_from_id(document_id, i)
            )
        except Exception as e:
            print(f"Error inserting chunk {i}: {e}")
            raise e