#!/usr/bin/env python3
"""
Vector Embedding Engine - Week 1 Foundation
Generate semantic embeddings for legal documents without Docker dependency
"""

import json
import numpy as np
import pickle
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime
import hashlib

# Try to import sentence-transformers, fallback to basic implementation
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

logger = logging.getLogger(__name__)

class LightweightEmbeddingEngine:
    """
    Lightweight embedding engine for legal documents
    Falls back to TF-IDF if sentence-transformers not available
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.embeddings_cache = {}
        self.document_chunks = {}
        self.chunk_embeddings = {}
        self.embedding_dim = 384  # Default for MiniLM
        
        # Initialize embedding model
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the embedding model"""
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                logger.info(f"🤖 Loading sentence transformer model: {self.model_name}")
                self.model = SentenceTransformer(self.model_name)
                self.embedding_dim = self.model.get_sentence_embedding_dimension()
                logger.info(f"✅ Model loaded successfully (dim: {self.embedding_dim})")
            except Exception as e:
                logger.error(f"❌ Failed to load model: {e}")
                self.model = None
        else:
            logger.warning("⚠️ sentence-transformers not available, using fallback TF-IDF")
            self._initialize_tfidf_fallback()
    
    def _initialize_tfidf_fallback(self):
        """Initialize TF-IDF fallback when sentence-transformers not available"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.decomposition import TruncatedSVD
        
        # Create TF-IDF vectorizer for basic semantic similarity
        self.tfidf = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2
        )
        
        # SVD for dimensionality reduction to simulate embeddings
        self.svd = TruncatedSVD(n_components=384)
        self.embedding_dim = 384
        
        logger.info("✅ TF-IDF fallback model initialized")
    
    def chunk_document(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Chunk document into smaller pieces for better embedding
        """
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            # Only add meaningful chunks
            if len(chunk_text.strip()) > 100:
                chunks.append(chunk_text)
        
        return chunks
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a single text"""
        if not text.strip():
            return np.zeros(self.embedding_dim)
        
        # Use sentence transformer if available
        if self.model is not None:
            try:
                embedding = self.model.encode(text, convert_to_numpy=True)
                return embedding
            except Exception as e:
                logger.error(f"❌ Embedding generation failed: {e}")
                return np.zeros(self.embedding_dim)
        
        # Fallback to TF-IDF
        return self._generate_tfidf_embedding(text)
    
    def _generate_tfidf_embedding(self, text: str) -> np.ndarray:
        """Generate TF-IDF based embedding as fallback"""
        try:
            # For single text, we need to fit on a corpus first
            # This is a simplified approach
            tfidf_vector = self.tfidf.fit_transform([text])
            
            # Pad or truncate to match embedding dimension
            dense_vector = tfidf_vector.toarray()[0]
            
            if len(dense_vector) < self.embedding_dim:
                # Pad with zeros
                padded = np.zeros(self.embedding_dim)
                padded[:len(dense_vector)] = dense_vector
                return padded
            else:
                # Truncate
                return dense_vector[:self.embedding_dim]
                
        except Exception as e:
            logger.error(f"❌ TF-IDF embedding failed: {e}")
            return np.zeros(self.embedding_dim)
    
    def process_legal_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a legal document and generate embeddings for all chunks
        """
        doc_id = document.get('document_id', str(hash(str(document))))
        
        # Extract searchable text
        searchable_text = document.get('searchable_text', '')
        if not searchable_text:
            searchable_text = self._extract_text_from_document(document)
        
        # Chunk the document
        chunks = self.chunk_document(searchable_text)
        
        # Generate embeddings for each chunk
        chunk_embeddings = []
        for i, chunk in enumerate(chunks):
            embedding = self.generate_embedding(chunk)
            
            chunk_data = {
                'chunk_id': f"{doc_id}_chunk_{i}",
                'text': chunk,
                'embedding': embedding.tolist(),  # Convert to list for JSON serialization
                'token_count': len(chunk.split()),
                'char_count': len(chunk)
            }
            
            chunk_embeddings.append(chunk_data)
        
        # Generate document-level embedding (average of chunks)
        if chunk_embeddings:
            doc_embedding = np.mean([np.array(chunk['embedding']) for chunk in chunk_embeddings], axis=0)
        else:
            doc_embedding = np.zeros(self.embedding_dim)
        
        # Return processed document with embeddings
        return {
            'document_id': doc_id,
            'original_document': document,
            'chunks': chunk_embeddings,
            'document_embedding': doc_embedding.tolist(),
            'chunk_count': len(chunks),
            'total_tokens': sum(chunk['token_count'] for chunk in chunk_embeddings),
            'embedding_model': self.model_name if self.model else 'tfidf_fallback',
            'processed_at': datetime.now().isoformat()
        }
    
    def _extract_text_from_document(self, document: Dict[str, Any]) -> str:
        """Extract text from document structure"""
        text_parts = []
        
        def extract_text_recursive(obj):
            if isinstance(obj, str) and len(obj) > 20:
                text_parts.append(obj)
            elif isinstance(obj, dict):
                for value in obj.values():
                    extract_text_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_text_recursive(item)
        
        extract_text_recursive(document)
        return ' '.join(text_parts)
    
    def semantic_search(self, query: str, document_embeddings: List[Dict], top_k: int = 5) -> List[Dict]:
        """
        Perform semantic search using embeddings
        """
        query_embedding = self.generate_embedding(query)
        
        # Calculate similarities
        similarities = []
        for doc in document_embeddings:
            doc_embedding = np.array(doc['document_embedding'])
            
            # Cosine similarity
            similarity = np.dot(query_embedding, doc_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding) + 1e-10
            )
            
            similarities.append({
                'document': doc,
                'similarity': float(similarity),
                'score': float(similarity * 100)  # Convert to percentage
            })
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:top_k]
    
    def save_embeddings(self, embeddings: List[Dict], filepath: str):
        """Save embeddings to file"""
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(embeddings, f)
            logger.info(f"✅ Embeddings saved to {filepath}")
        except Exception as e:
            logger.error(f"❌ Failed to save embeddings: {e}")
    
    def load_embeddings(self, filepath: str) -> List[Dict]:
        """Load embeddings from file"""
        try:
            with open(filepath, 'rb') as f:
                embeddings = pickle.load(f)
            logger.info(f"✅ Embeddings loaded from {filepath}")
            return embeddings
        except Exception as e:
            logger.error(f"❌ Failed to load embeddings: {e}")
            return []

class VectorKnowledgeBase:
    """
    Vector-based knowledge base for legal documents
    """
    
    def __init__(self, embedding_engine: LightweightEmbeddingEngine):
        self.embedding_engine = embedding_engine
        self.documents = []
        self.embeddings = []
        self.is_loaded = False
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to the knowledge base and generate embeddings"""
        logger.info(f"🔄 Processing {len(documents)} documents for vector knowledge base...")
        
        for i, document in enumerate(documents):
            if i % 10 == 0:
                logger.info(f"   Processing document {i+1}/{len(documents)}")
            
            # Process document and generate embeddings
            processed_doc = self.embedding_engine.process_legal_document(document)
            
            self.documents.append(document)
            self.embeddings.append(processed_doc)
        
        self.is_loaded = True
        logger.info(f"✅ Vector knowledge base ready with {len(self.embeddings)} documents")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search using semantic similarity"""
        if not self.is_loaded:
            logger.error("❌ Knowledge base not loaded")
            return []
        
        return self.embedding_engine.semantic_search(query, self.embeddings, top_k)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        if not self.is_loaded:
            return {'loaded': False}
        
        total_chunks = sum(emb['chunk_count'] for emb in self.embeddings)
        total_tokens = sum(emb['total_tokens'] for emb in self.embeddings)
        
        return {
            'loaded': True,
            'total_documents': len(self.documents),
            'total_chunks': total_chunks,
            'total_tokens': total_tokens,
            'embedding_model': self.embeddings[0]['embedding_model'] if self.embeddings else 'none',
            'average_chunks_per_doc': total_chunks / len(self.embeddings) if self.embeddings else 0
        }

def main():
    """Test the vector embedding engine"""
    print("🚀 Testing Vector Embedding Engine for Week 1 Foundation")
    
    # Initialize embedding engine
    embedding_engine = LightweightEmbeddingEngine()
    
    # Test with sample legal documents
    sample_docs = [
        {
            'document_id': 'test_1',
            'searchable_text': 'Income tax rates for individual taxpayers in Bangladesh. The current tax rates are structured in slabs.',
            'metadata': {'category': 'income_tax'}
        },
        {
            'document_id': 'test_2', 
            'searchable_text': 'VAT registration requirements for businesses. Companies must register if annual turnover exceeds threshold.',
            'metadata': {'category': 'vat_customs'}
        }
    ]
    
    # Create vector knowledge base
    kb = VectorKnowledgeBase(embedding_engine)
    kb.add_documents(sample_docs)
    
    # Test semantic search
    query = "What are the tax rates for individuals?"
    results = kb.search(query, top_k=2)
    
    print(f"\n🔍 Search Query: {query}")
    for i, result in enumerate(results, 1):
        print(f"{i}. Score: {result['score']:.2f}%")
        print(f"   Text: {result['document']['original_document']['searchable_text'][:100]}...")
    
    # Show statistics
    stats = kb.get_stats()
    print(f"\n📊 Knowledge Base Stats:")
    print(f"   Documents: {stats['total_documents']}")
    print(f"   Chunks: {stats['total_chunks']}")
    print(f"   Tokens: {stats['total_tokens']}")
    print(f"   Model: {stats['embedding_model']}")
    
    print("\n✅ Vector embedding engine test complete!")

if __name__ == "__main__":
    main()