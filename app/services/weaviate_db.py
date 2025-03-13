import weaviate
import os
from weaviate.classes.init import Auth

wcd_url = os.getenv("WCD_URL")
wcd_api_key = os.getenv("WCD_API_KEY")

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=wcd_url,
    auth_credentials=Auth.api_key(wcd_api_key),
)

def get_weaviate_meta():
    """Retrieve Weaviate's meta information."""
    if client.is_ready():
        meta = client.get_meta()
        return meta
    return "Weaviate is not ready."

if __name__ == "__main__":
    meta_info = get_weaviate_meta()
    print(meta_info)
    client.close()