import json
import os
from rag.nlp import rag_tokenizer, naive
from rag.utils import num_tokens_from_string

def test_ragflow_legal_processing():
    print("=== Testing RAGFlow Legal Document Processing ===")
    
    # Test with income tax act
    test_file = "data/income_tax_act_2023_cleaned.json"
    
    if os.path.exists(test_file):
        print(f"\nTesting with: {test_file}")
        
        with open(test_file, 'r', encoding='utf-8') as f:
            legal_data = json.load(f)
        
        # Extract sample text for processing
        sample_text = ""
        if 'chapters' in legal_data:
            for chapter in legal_data['chapters'][:2]:  # First 2 chapters
                if 'content' in chapter:
                    sample_text += chapter['content'][:1000]  # First 1000 chars
                elif 'sections' in chapter:
                    for section in chapter['sections'][:3]:  # First 3 sections
                        if 'content' in section:
                            sample_text += section['content'][:500]
        
        if sample_text:
            print(f"Sample text length: {len(sample_text)} characters")
            
            # Test RAGFlow tokenization
            try:
                tokens = num_tokens_from_string(sample_text)
                print(f"Token count: {tokens}")
                
                # Test chunking with RAGFlow
                chunks = naive.naive_merge(sample_text, chunk_token_num=512)
                print(f"Generated chunks: {len(chunks)}")
                
                # Show first chunk
                if chunks:
                    print(f"First chunk preview: {chunks[0][:200]}...")
                
                print("✅ RAGFlow processing successful!")
                
            except Exception as e:
                print(f"❌ RAGFlow processing error: {e}")
        
        else:
            print("❌ No suitable content found for processing")
    
    else:
        print(f"❌ Test file not found: {test_file}")

if __name__ == "__main__":
    test_ragflow_legal_processing()