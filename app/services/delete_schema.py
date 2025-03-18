import os
from weaviate import connect_to_weaviate_cloud
from weaviate.auth import AuthApiKey

# Load environment variables
WCD_URL = os.getenv("WCD_URL")
WCD_API_KEY = os.getenv("WCD_API_KEY")

# Connect to Weaviate
with connect_to_weaviate_cloud(
    cluster_url=WCD_URL,
    auth_credentials=AuthApiKey(WCD_API_KEY)
) as client:
    if client.collections.exists("DocumentChunk"):
        client.collections.delete("DocumentChunk")
        print("Deleted existing DocumentChunk schema.")
    else:
        print("DocumentChunk schema does not exist.")