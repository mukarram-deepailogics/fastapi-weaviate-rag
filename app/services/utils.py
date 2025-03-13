from typing import List, Dict

def chunk_document(document_content: str, chunk_size: int, overlap: int) -> List[Dict]:
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Invalid chunk_size or overlap parameters")
    
    if not document_content:
        return []

    characters_per_page = 2000
    chunks = []
    start_idx = 0
    chunk_index = 0
    content_length = len(document_content)

    while start_idx < content_length:
        end_idx = min(start_idx + chunk_size, content_length)
        chunk_content = document_content[start_idx:end_idx]
        
        page_number = (start_idx // characters_per_page) + 1
        
        chunks.append({
            "content": chunk_content,
            "chunk_index": chunk_index,
            "page_number": page_number
        })
        
        if end_idx == content_length:
            break
            
        start_idx += chunk_size - overlap
        chunk_index += 1

    return chunks