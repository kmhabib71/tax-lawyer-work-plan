#!/usr/bin/env python3
"""
Simple Vector System - Week 1 Foundation
Basic semantic search using only Python standard library
"""

import json
import math
import re
from collections import Counter, defaultdict
from typing import List, Dict, Any, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SimpleVectorEngine:
    """
    Simple vector engine using TF-IDF with cosine similarity
    No external dependencies required
    """
    
    def __init__(self):
        self.documents = []
        self.tf_idf_vectors = []
        self.vocabulary = set()
        self.idf_scores = {}
        self.is_built = False
    
    def preprocess_text(self, text: str) -> List[str]:
        """Simple text preprocessing"""
        # Convert to lowercase and remove special characters
        text = re.sub(r'[^\w\s\u0980-\u09FF]', ' ', text.lower())
        
        # Split into words and filter
        words = text.split()
        
        # Remove very short words and common stop words
        stop_words = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but', 'in', 'with', 'to', 'for', 'of', 'as', 'by'}
        
        filtered_words = []
        for word in words:
            if len(word) > 2 and word not in stop_words:
                filtered_words.append(word)
        
        return filtered_words
    
    def calculate_tf(self, doc_words: List[str]) -> Dict[str, float]:
        """Calculate term frequency for a document"""
        word_count = len(doc_words)
        tf_scores = {}
        
        for word in set(doc_words):
            tf_scores[word] = doc_words.count(word) / word_count
        
        return tf_scores
    
    def calculate_idf(self, documents: List[List[str]]) -> Dict[str, float]:
        """Calculate inverse document frequency"""
        total_docs = len(documents)
        idf_scores = {}
        
        # Get all unique words
        all_words = set()
        for doc in documents:
            all_words.update(doc)
        
        # Calculate IDF for each word
        for word in all_words:
            docs_containing_word = sum(1 for doc in documents if word in doc)
            idf_scores[word] = math.log(total_docs / docs_containing_word)
        
        return idf_scores
    
    def build_vectors(self, documents: List[Dict[str, Any]]):
        """Build TF-IDF vectors for all documents"""
        logger.info(f"🔨 Building vectors for {len(documents)} documents...")
        
        self.documents = documents
        processed_docs = []
        
        # Preprocess all documents
        for doc in documents:
            # Extract text
            text = doc.get('searchable_text', '')
            if not text:
                text = self._extract_text_from_doc(doc)
            
            # Preprocess
            words = self.preprocess_text(text)
            processed_docs.append(words)
            
            # Update vocabulary
            self.vocabulary.update(words)
        
        # Calculate IDF scores
        self.idf_scores = self.calculate_idf(processed_docs)
        
        # Build TF-IDF vectors
        self.tf_idf_vectors = []
        for doc_words in processed_docs:
            tf_scores = self.calculate_tf(doc_words)
            
            # Create TF-IDF vector
            vector = {}
            for word in self.vocabulary:
                tf = tf_scores.get(word, 0)
                idf = self.idf_scores.get(word, 0)
                vector[word] = tf * idf
            
            self.tf_idf_vectors.append(vector)
        
        self.is_built = True
        logger.info(f"✅ Vector system built with {len(self.vocabulary)} terms")
    
    def _extract_text_from_doc(self, doc: Dict[str, Any]) -> str:
        """Extract searchable text from document"""
        text_parts = []
        
        def extract_recursive(obj):
            if isinstance(obj, str) and len(obj) > 10:
                text_parts.append(obj)
            elif isinstance(obj, dict):
                for value in obj.values():
                    extract_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_recursive(item)
        
        extract_recursive(doc)
        return ' '.join(text_parts)
    
    def cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Calculate cosine similarity between two vectors"""
        # Get common terms
        common_terms = set(vec1.keys()) & set(vec2.keys())
        
        if not common_terms:
            return 0.0
        
        # Calculate dot product
        dot_product = sum(vec1[term] * vec2[term] for term in common_terms)
        
        # Calculate magnitudes
        magnitude1 = math.sqrt(sum(vec1[term] ** 2 for term in vec1))
        magnitude2 = math.sqrt(sum(vec2[term] ** 2 for term in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def create_query_vector(self, query: str) -> Dict[str, float]:
        """Create TF-IDF vector for query"""
        query_words = self.preprocess_text(query)
        
        if not query_words:
            return {}
        
        # Calculate TF for query
        tf_scores = self.calculate_tf(query_words)
        
        # Create TF-IDF vector using existing IDF scores
        query_vector = {}
        for word in query_words:
            if word in self.idf_scores:
                tf = tf_scores.get(word, 0)
                idf = self.idf_scores[word]
                query_vector[word] = tf * idf
        
        return query_vector
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        if not self.is_built:
            logger.error("❌ Vector system not built. Call build_vectors() first.")
            return []
        
        # Create query vector
        query_vector = self.create_query_vector(query)
        
        if not query_vector:
            return []
        
        # Calculate similarities
        similarities = []
        for i, doc_vector in enumerate(self.tf_idf_vectors):
            similarity = self.cosine_similarity(query_vector, doc_vector)
            
            if similarity > 0:
                similarities.append({
                    'document_index': i,
                    'document': self.documents[i],
                    'similarity': similarity,
                    'score': similarity * 100
                })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similarities[:top_k]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        return {
            'built': self.is_built,
            'total_documents': len(self.documents),
            'vocabulary_size': len(self.vocabulary),
            'average_doc_terms': len(self.vocabulary) / len(self.documents) if self.documents else 0
        }

class SimpleKnowledgeBase:
    """
    Simple knowledge base using the vector engine
    """
    
    def __init__(self):
        self.vector_engine = SimpleVectorEngine()
        self.documents = []
        self.is_ready = False
    
    def load_documents(self, documents: List[Dict[str, Any]]):
        """Load documents into the knowledge base"""
        logger.info(f"📚 Loading {len(documents)} documents into knowledge base...")
        
        self.documents = documents
        self.vector_engine.build_vectors(documents)
        self.is_ready = True
        
        logger.info("✅ Knowledge base ready for search")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search the knowledge base"""
        if not self.is_ready:
            return []
        
        results = self.vector_engine.search(query, top_k)
        
        # Add snippets to results
        for result in results:
            result['snippets'] = self._extract_snippets(
                result['document'].get('searchable_text', ''), 
                query
            )
        
        return results
    
    def _extract_snippets(self, text: str, query: str, max_snippets: int = 2) -> List[str]:
        """Extract relevant snippets from text"""
        query_words = set(self.vector_engine.preprocess_text(query))
        sentences = re.split(r'[।\.!?]+', text)
        
        scored_sentences = []
        for sentence in sentences:
            if len(sentence.strip()) < 30:
                continue
            
            sentence_words = set(self.vector_engine.preprocess_text(sentence))
            score = len(query_words & sentence_words)
            
            if score > 0:
                scored_sentences.append((sentence.strip(), score))
        
        # Sort by score and return top snippets
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        
        snippets = []
        for sentence, _ in scored_sentences[:max_snippets]:
            # Highlight query words
            highlighted = sentence
            for word in query_words:
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                highlighted = pattern.sub(f"**{word}**", highlighted)
            
            snippets.append(highlighted[:200] + "..." if len(highlighted) > 200 else highlighted)
        
        return snippets
    
    def chat(self, question: str) -> Dict[str, Any]:
        """Simple chat functionality"""
        if not self.is_ready:
            return {
                'success': False,
                'error': 'Knowledge base not ready'
            }
        
        # Search for relevant documents
        results = self.search(question, top_k=3)
        
        if not results:
            return {
                'success': True,
                'question': question,
                'answer': "I couldn't find specific information about your question in the legal documents. Please try rephrasing your query.",
                'sources': []
            }
        
        # Generate answer from top results
        answer_parts = []
        sources = []
        
        for result in results:
            if result['snippets']:
                answer_parts.extend(result['snippets'])
                sources.append({
                    'filename': result['document'].get('metadata', {}).get('filename', 'Unknown'),
                    'score': round(result['score'], 2)
                })
        
        if answer_parts:
            answer = "Based on Bangladesh tax laws:\n\n" + "\n\n".join(answer_parts[:3])
        else:
            answer = "I found relevant documents but couldn't extract specific snippets. Please refer to the source documents."
        
        return {
            'success': True,
            'question': question,
            'answer': answer,
            'sources': sources,
            'total_results': len(results)
        }

def main():
    """Test the simple vector system"""
    print("🔍 Testing Simple Vector System - Week 1 Foundation")
    
    # Sample legal documents
    sample_docs = [
        {
            'document_id': 'income_tax_1',
            'searchable_text': 'Income tax rates for individual taxpayers in Bangladesh are structured in progressive slabs. The tax exemption limit is 3.5 lakh taka for male taxpayers.',
            'metadata': {'filename': 'income_tax_rates.json', 'category': 'income_tax'}
        },
        {
            'document_id': 'vat_1',
            'searchable_text': 'VAT registration is mandatory for businesses with annual turnover exceeding 30 lakh taka. The VAT rate is 15% on most goods and services.',
            'metadata': {'filename': 'vat_registration.json', 'category': 'vat'}
        },
        {
            'document_id': 'investment_1',
            'searchable_text': 'Investment rebate allows taxpayers to claim 15% of qualifying investments as tax rebate, subject to maximum limits.',
            'metadata': {'filename': 'investment_rebate.json', 'category': 'income_tax'}
        }
    ]
    
    # Create knowledge base
    kb = SimpleKnowledgeBase()
    kb.load_documents(sample_docs)
    
    # Test searches
    test_queries = [
        "What are the income tax rates?",
        "VAT registration requirements",
        "Investment rebate rules",
        "Tax exemption limits"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        results = kb.search(query, top_k=2)
        
        for i, result in enumerate(results, 1):
            print(f"   {i}. Score: {result['score']:.1f}% - {result['document']['metadata']['filename']}")
            if result['snippets']:
                print(f"      Snippet: {result['snippets'][0]}")
    
    # Test chat
    print(f"\n💬 Chat Test:")
    question = "How much investment rebate can I get?"
    response = kb.chat(question)
    print(f"Q: {question}")
    print(f"A: {response['answer'][:200]}...")
    
    # Show stats
    stats = kb.vector_engine.get_stats()
    print(f"\n📊 System Stats:")
    print(f"   Documents: {stats['total_documents']}")
    print(f"   Vocabulary: {stats['vocabulary_size']} terms")
    print(f"   Average terms per doc: {stats['average_doc_terms']:.1f}")
    
    print("\n✅ Simple vector system test complete!")

if __name__ == "__main__":
    main()