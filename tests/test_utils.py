import sys
import os
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.services.utils import chunk_document

class TestChunkDocument(unittest.TestCase):
    def test_basic_functionality(self):
        """Test core chunking with overlap and page numbers"""
        text = "1234567890ABCDEFGHIJ"
        result = chunk_document(text, chunk_size=10, overlap=3)
        
        self.assertEqual(len(result), 3)
        self.assertEqual(
            [chunk["content"] for chunk in result],
            ["1234567890", "890ABCDEFG", "EFGHIJ"] 
        )
        
        self.assertEqual(result[0]["chunk_index"], 0)
        self.assertEqual(result[1]["page_number"], 1)
        self.assertEqual(result[2]["page_number"], 1)

if __name__ == "__main__":
    unittest.main()