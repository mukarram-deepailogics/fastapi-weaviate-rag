import os 
import weaviate
from weaviate.auth import AuthApiKey
from weaviate.classes.query import Filter  

def query_weaviate(question: str, document_id: str = None):
    """Queries Weaviate for relevant document chunks with certainty scores"""
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=os.getenv("WCD_URL"),
        auth_credentials=AuthApiKey(os.getenv("WCD_API_KEY")),
        headers={"X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")}
    )

    try:
        collection = client.collections.get("DocumentChunk")

        print("🔍 Querying Weaviate with question:", question)
        print("🔍 Using document_id filter:", document_id)

        filters = None
        if document_id:
            filters = Filter.by_property("document_id").equal(document_id)

        query_results = collection.query.near_text(
            query=question,
            limit=3,
            return_properties=["content", "document_id", "page_number"],
            return_metadata=["certainty"],
            filters=filters  
        ).objects  

        print("🔍 Raw Query Results from Weaviate:", query_results)

        if not query_results:
            print("⚠️ No results found. Weaviate might not be indexing properly.")

        formatted_results = []
        for obj in query_results:
            properties = obj.properties if hasattr(obj, "properties") else obj.get("properties", {})
            metadata = obj.metadata if hasattr(obj, "metadata") else obj.get("metadata", {})

            formatted_results.append({
                "content": properties.get("content", ""),
                "document_id": properties.get("document_id", ""),
                "page_number": properties.get("page_number", 0),
                "certainty": metadata.certainty if metadata else None
            })

        print("✅ Formatted Results:", formatted_results)
        return formatted_results

    except Exception as e:
        raise RuntimeError(f"Weaviate query error: {str(e)}")
    finally:
        client.close()
