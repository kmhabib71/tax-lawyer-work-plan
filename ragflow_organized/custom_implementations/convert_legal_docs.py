import json
import os

def convert_legal_json_to_ragflow():
    data_dir = "data"
    
    print("=== Legal Document Analysis ===")
    
    # Process each legal JSON file
    for filename in os.listdir(data_dir):
        if filename.endswith('.json'):
            try:
                print(f"\nProcessing: {filename}")
            except UnicodeEncodeError:
                print(f"\nProcessing: [Bengali filename - {len(filename)} chars]")
            
            try:
                with open(os.path.join(data_dir, filename), 'r', encoding='utf-8') as f:
                    legal_data = json.load(f)
                
                file_size_chars = len(str(legal_data))
                file_size_mb = file_size_chars / (1024 * 1024)
                
                print(f"  File size: {file_size_chars:,} characters ({file_size_mb:.2f} MB)")
                
                # Analyze structure
                if isinstance(legal_data, dict):
                    print(f"  Structure: Dictionary with {len(legal_data)} keys")
                    if 'sections' in legal_data:
                        print(f"  Sections: {len(legal_data.get('sections', []))}")
                    if 'chapters' in legal_data:
                        print(f"  Chapters: {len(legal_data.get('chapters', []))}")
                elif isinstance(legal_data, list):
                    print(f"  Structure: List with {len(legal_data)} items")
                
            except Exception as e:
                print(f"  Error processing {filename}: {e}")
    
    print("\n=== Legal Document Analysis Complete! ===")

if __name__ == "__main__":
    convert_legal_json_to_ragflow()