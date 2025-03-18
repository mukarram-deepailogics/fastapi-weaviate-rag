import weaviate
from weaviate.auth import AuthApiKey
import os

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=os.getenv("WCD_URL"),
    auth_credentials=AuthApiKey(os.getenv("WCD_API_KEY")),
    headers={"X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")}
)

query_text = "What is Weaviate?"
collection = client.collections.get("DocumentChunk")

query_results = collection.query.near_text(
    query=query_text,
    limit=3,
    return_properties=["content", "document_id", "page_number"],
    return_metadata=["certainty"]
).objects

print("🔍 Query Results:", query_results)

client.close()
