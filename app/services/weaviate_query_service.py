import os
import weaviate
from weaviate.auth import AuthApiKey
from weaviate.classes.query import Filter
from weaviate.exceptions import WeaviateBaseError

class WeaviateConnectionError(Exception):
    pass

class NoResultsFoundError(Exception):
    pass

def query_weaviate(question: str, document_id: str = None):
    

    WCD_URL = os.getenv("WCD_URL")
    WCD_API_KEY = os.getenv("WCD_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    if not WCD_URL or not WCD_API_KEY:
        raise WeaviateConnectionError("Missing Weaviate cloud credentials. Check environment variables.")

    try:

        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=WCD_URL,
            auth_credentials=AuthApiKey(WCD_API_KEY),
            headers={"X-OpenAI-Api-Key": OPENAI_API_KEY}
        )

        if not client.is_ready():
            raise WeaviateConnectionError("Failed to connect to Weaviate. Check your API key or server status.")

        collection = client.collections.get("DocumentChunk")
        
        print("Querying Weaviate with question : ", question)
        print("Using document_id filter : ", document_id)

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

        if not query_results:
            raise NoResultsFoundError("No relevant information found in the documents.")

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

        print("Formatted Results:", formatted_results)
        return formatted_results

    except WeaviateBaseError as e:
        raise WeaviateConnectionError(f"Weaviate connection error: {str(e)}")

    except Exception as e:
        raise RuntimeError(f"Unexpected Weaviate query error: {str(e)}")

    finally:
        client.close()
