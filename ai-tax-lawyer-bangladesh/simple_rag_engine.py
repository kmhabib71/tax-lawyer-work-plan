#!/usr/bin/env python3
"""
Simple RAG Engine for Bangladesh Tax Laws
Uses existing legal data without requiring Docker/RAGFlow
Implements basic search and retrieval functionality
"""

import json
import os
import re
import math
from pathlib import Path
from typing import List, Dict, Tuple, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SimpleTaxRAG:
    """
    Simple RAG implementation for Bangladesh tax laws
    Uses TF-IDF for search and retrieval without external dependencies
    """
    
    def __init__(self, data_directory: str = None):
        self.data_directory = data_directory or "../ragflow/phase0_foundation/data_assets"
        self.documents = []
        self.document_index = {}
        self.term_frequencies = {}
        self.inverse_document_frequencies = {}
        self.is_loaded = False
    
    def load_legal_documents(self) -> bool:
        """Load all legal documents from the data directory"""
        try:
            data_path = Path(self.data_directory)
            if not data_path.exists():
                logger.error(f"Data directory not found: {data_path}")
                return False
            
            json_files = list(data_path.glob("*.json"))
            logger.info(f"Found {len(json_files)} JSON files")
            
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        content = json.load(f)
                    
                    # Extract searchable text from JSON
                    searchable_text = self._extract_searchable_text(content)
                    
                    doc = {
                        'id': len(self.documents),
                        'filename': json_file.name,
                        'content': content,
                        'searchable_text': searchable_text,
                        'word_count': len(searchable_text.split())
                    }
                    
                    self.documents.append(doc)
                    logger.info(f"Loaded: {json_file.name} ({doc['word_count']} words)")
                    
                except Exception as e:
                    logger.error(f"Failed to load {json_file.name}: {e}")
            
            if self.documents:
                self._build_search_index()
                self.is_loaded = True
                logger.info(f"Successfully loaded {len(self.documents)} documents")
                return True
            else:
                logger.error("No documents loaded")
                return False
                
        except Exception as e:
            logger.error(f"Failed to load documents: {e}")
            return False
    
    def _extract_searchable_text(self, content: Dict) -> str:
        """Extract searchable text from JSON content"""
        text_parts = []
        
        # Common text fields to extract
        text_fields = ['title', 'content', 'description', 'text', 'bengali_text', 'english_text']
        
        for field in text_fields:
            if field in content and isinstance(content[field], str):
                text_parts.append(content[field])
        
        # Handle nested structures
        if isinstance(content, dict):
            for key, value in content.items():
                if isinstance(value, str) and len(value) > 20:  # Long text fields
                    text_parts.append(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            text_parts.append(self._extract_searchable_text(item))
                        elif isinstance(item, str):
                            text_parts.append(item)
        
        return ' '.join(text_parts)
    
    def _build_search_index(self):
        """Build TF-IDF index for search"""
        logger.info("Building search index...")
        
        # Calculate term frequencies for each document
        for doc in self.documents:
            words = self._tokenize(doc['searchable_text'])
            word_count = {}
            
            for word in words:
                word_count[word] = word_count.get(word, 0) + 1
            
            # Calculate TF (term frequency)
            total_words = len(words)
            tf = {}
            for word, count in word_count.items():
                tf[word] = count / total_words
            
            self.term_frequencies[doc['id']] = tf
        
        # Calculate IDF (inverse document frequency)
        all_words = set()
        for tf in self.term_frequencies.values():
            all_words.update(tf.keys())
        
        total_docs = len(self.documents)
        for word in all_words:
            docs_with_word = sum(1 for tf in self.term_frequencies.values() if word in tf)
            self.inverse_document_frequencies[word] = math.log(total_docs / docs_with_word)
        
        logger.info(f"Index built with {len(all_words)} unique terms")
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization for both English and Bengali"""
        # Remove special characters and convert to lowercase
        text = re.sub(r'[^\w\s\u0980-\u09FF]', ' ', text.lower())
        
        # Split into words and filter out very short words
        words = [word.strip() for word in text.split() if len(word) > 2]
        
        return words
    
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for relevant documents"""
        if not self.is_loaded:
            logger.error("Documents not loaded. Call load_legal_documents() first.")
            return []
        
        query_words = self._tokenize(query)
        if not query_words:
            return []
        
        # Calculate TF-IDF scores for each document
        doc_scores = []
        
        for doc in self.documents:
            score = 0
            tf = self.term_frequencies.get(doc['id'], {})
            
            for word in query_words:
                if word in tf:
                    tfidf = tf[word] * self.inverse_document_frequencies.get(word, 0)
                    score += tfidf
            
            if score > 0:
                doc_scores.append({
                    'document': doc,
                    'score': score,
                    'relevance': min(score * 100, 100)  # Normalize to percentage
                })
        
        # Sort by score and return top results
        doc_scores.sort(key=lambda x: x['score'], reverse=True)
        
        results = []
        for item in doc_scores[:limit]:
            # Extract relevant snippets
            snippets = self._extract_snippets(item['document']['searchable_text'], query_words)
            
            results.append({
                'filename': item['document']['filename'],
                'score': round(item['relevance'], 2),
                'snippets': snippets,
                'content': item['document']['content']
            })
        
        return results
    
    def _extract_snippets(self, text: str, query_words: List[str], max_snippets: int = 3) -> List[str]:
        """Extract relevant snippets containing query words"""
        sentences = re.split(r'[।\.\!\?]+', text)
        scored_sentences = []
        
        for sentence in sentences:
            if len(sentence.strip()) < 20:  # Skip very short sentences
                continue
                
            score = sum(1 for word in query_words if word in sentence.lower())
            if score > 0:
                scored_sentences.append((sentence.strip(), score))
        
        # Sort by relevance and return top snippets
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        
        snippets = []
        for sentence, _ in scored_sentences[:max_snippets]:
            # Highlight query words (simple approach)
            highlighted = sentence
            for word in query_words:
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                highlighted = pattern.sub(f"**{word}**", highlighted)
            
            snippets.append(highlighted[:300] + "..." if len(highlighted) > 300 else highlighted)
        
        return snippets
    
    def chat(self, question: str, context_limit: int = 3) -> Dict[str, Any]:
        """Simple chat functionality using search results"""
        if not self.is_loaded:
            return {
                'success': False,
                'error': 'Documents not loaded'
            }
        
        # Search for relevant documents
        search_results = self.search(question, context_limit)
        
        if not search_results:
            return {
                'success': True,
                'answer': "I couldn't find specific information about your question in the tax laws. Please try rephrasing your query or be more specific.",
                'sources': []
            }
        
        # Generate a simple answer based on search results
        answer_parts = []
        sources = []
        
        for result in search_results:
            if result['snippets']:
                answer_parts.extend(result['snippets'][:2])  # Take top 2 snippets
                sources.append({
                    'filename': result['filename'],
                    'relevance': result['score']
                })
        
        # Combine snippets into a coherent answer
        if answer_parts:
            answer = "Based on Bangladesh tax laws:\n\n" + "\n\n".join(answer_parts)
        else:
            answer = "I found relevant documents but couldn't extract specific information. Please refer to the source documents for detailed information."
        
        return {
            'success': True,
            'question': question,
            'answer': answer,
            'sources': sources,
            'search_results_count': len(search_results)
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded documents"""
        if not self.is_loaded:
            return {'loaded': False}
        
        total_words = sum(doc['word_count'] for doc in self.documents)
        
        return {
            'loaded': True,
            'total_documents': len(self.documents),
            'total_words': total_words,
            'average_words_per_doc': total_words / len(self.documents) if self.documents else 0,
            'unique_terms': len(self.inverse_document_frequencies),
            'data_directory': self.data_directory
        }

def main():
    """Test the Simple RAG Engine"""
    print("🔍 Testing Simple RAG Engine for Bangladesh Tax Laws")
    
    # Initialize RAG engine
    rag = SimpleTaxRAG()
    
    # Load documents
    print("\n📚 Loading legal documents...")
    if not rag.load_legal_documents():
        print("❌ Failed to load documents")
        return
    
    # Show statistics
    stats = rag.get_stats()
    print(f"✅ Loaded {stats['total_documents']} documents")
    print(f"📊 Total words: {stats['total_words']:,}")
    print(f"📊 Unique terms: {stats['unique_terms']:,}")
    
    # Test queries
    test_queries = [
        "আয়কর হার কত",  # Bengali: What is the income tax rate
        "income tax exemption",
        "business expense deduction",
        "VAT registration",
        "tax calculation"
    ]
    
    print("\n🔍 Testing search functionality...")
    for query in test_queries:
        print(f"\n Query: {query}")
        results = rag.search(query, limit=3)
        
        if results:
            print(f"   ✅ Found {len(results)} results")
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result['filename']} (Score: {result['score']}%)")
                if result['snippets']:
                    print(f"      Snippet: {result['snippets'][0][:100]}...")
        else:
            print("   ❌ No results found")
    
    # Test chat functionality
    print("\n💬 Testing chat functionality...")
    chat_questions = [
        "What are the current income tax rates in Bangladesh?",
        "How much investment rebate can I get?"
    ]
    
    for question in chat_questions:
        print(f"\n Question: {question}")
        response = rag.chat(question)
        
        if response['success']:
            print(f"   ✅ Answer: {response['answer'][:200]}...")
            print(f"   📚 Sources: {len(response['sources'])} documents")
        else:
            print(f"   ❌ Error: {response['error']}")
    
    print("\n🎉 Simple RAG Engine testing complete!")

if __name__ == "__main__":
    main()