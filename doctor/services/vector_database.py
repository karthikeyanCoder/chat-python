import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import pickle
import hashlib

# Lazy import for sentence_transformers to avoid DLL issues
SentenceTransformer = None
SENTENCE_TRANSFORMERS_AVAILABLE = False

def _lazy_import_sentence_transformers():
    """Lazy import sentence transformers to avoid DLL issues"""
    global SentenceTransformer, SENTENCE_TRANSFORMERS_AVAILABLE
    if SentenceTransformer is None:
        try:
            from sentence_transformers import SentenceTransformer
            SENTENCE_TRANSFORMERS_AVAILABLE = True
            print("[OK] SentenceTransformers loaded successfully in VectorDatabase")
        except ImportError as e:
            SENTENCE_TRANSFORMERS_AVAILABLE = False
            print(f"[WARN] SentenceTransformers not available: {e}")
        except OSError as e:
            SENTENCE_TRANSFORMERS_AVAILABLE = False
            print(f"[WARN] SentenceTransformers DLL error (PyTorch issue): {e}")
    return SentenceTransformer

class VectorDatabase:
    """
    Simple vector database implementation for medical knowledge chunks.
    Uses sentence transformers for embeddings and cosine similarity for search.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.embeddings = []
        self.chunks = []
        self.metadata = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize the embedding model
        self._initialize_model()
        
        # Load existing data if available
        self._load_data()
    
    def _initialize_model(self):
        """Initialize the sentence transformer model using lazy loading."""
        SentenceTransformer = _lazy_import_sentence_transformers()
        if SENTENCE_TRANSFORMERS_AVAILABLE and SentenceTransformer:
            try:
                self.model = SentenceTransformer(self.model_name)
                self.logger.info(f"Initialized embedding model: {self.model_name}")
            except Exception as e:
                self.logger.error(f"Error initializing embedding model: {str(e)}")
                self.model = None
        else:
            self.model = None
            self.logger.warning("SentenceTransformers not available - embedding model not initialized")
    
    def add_chunks(self, chunks: List[Dict[str, Any]]) -> bool:
        """
        Add medical knowledge chunks to the vector database.
        
        Args:
            chunks: List of medical knowledge chunks with 'content' and 'metadata' fields
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.model:
                self.logger.error("Embedding model not initialized")
                return False
            
            new_embeddings = []
            new_chunks = []
            new_metadata = []
            
            for chunk in chunks:
                if 'content' not in chunk:
                    continue
                
                # Generate embedding
                embedding = self.model.encode(chunk['content'])
                new_embeddings.append(embedding)
                
                # Store chunk and metadata
                new_chunks.append(chunk['content'])
                metadata = chunk.get('metadata', {})
                metadata['chunk_id'] = self._generate_chunk_id(chunk['content'])
                metadata['added_at'] = datetime.utcnow().isoformat()
                new_metadata.append(metadata)
            
            # Add to existing data
            self.embeddings.extend(new_embeddings)
            self.chunks.extend(new_chunks)
            self.metadata.extend(new_metadata)
            
            # Save updated data
            self._save_data()
            
            self.logger.info(f"Added {len(new_chunks)} medical knowledge chunks")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding chunks: {str(e)}")
            return False
    
    def search_similar_chunks(
        self, 
        query: str, 
        top_k: int = 5, 
        filter_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar medical knowledge chunks.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            filter_type: Optional filter by chunk type
        
        Returns:
            List of similar chunks with metadata
        """
        try:
            if not self.model or not self.embeddings:
                return []
            
            # Generate query embedding
            query_embedding = self.model.encode(query)
            
            # Calculate cosine similarities
            similarities = self._calculate_cosine_similarities(query_embedding, self.embeddings)
            
            # Get top-k indices
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            # Filter by type if specified
            if filter_type:
                filtered_indices = []
                for idx in top_indices:
                    if (idx < len(self.metadata) and 
                        self.metadata[idx].get('type', '').lower() == filter_type.lower()):
                        filtered_indices.append(idx)
                top_indices = filtered_indices[:top_k]
            
            # Prepare results
            results = []
            for idx in top_indices:
                if idx < len(self.chunks) and idx < len(self.metadata):
                    results.append({
                        'content': self.chunks[idx],
                        'metadata': self.metadata[idx],
                        'similarity_score': float(similarities[idx])
                    })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching chunks: {str(e)}")
            return []
    
    def _calculate_cosine_similarities(self, query_embedding: np.ndarray, embeddings: List[np.ndarray]) -> np.ndarray:
        """Calculate cosine similarities between query and all embeddings."""
        if not embeddings:
            return np.array([])
        
        # Convert to numpy array
        embeddings_array = np.array(embeddings)
        
        # Calculate cosine similarities
        query_norm = np.linalg.norm(query_embedding)
        embeddings_norm = np.linalg.norm(embeddings_array, axis=1)
        
        # Avoid division by zero
        query_norm = max(query_norm, 1e-8)
        embeddings_norm = np.maximum(embeddings_norm, 1e-8)
        
        similarities = np.dot(embeddings_array, query_embedding) / (query_norm * embeddings_norm)
        
        return similarities
    
    def _generate_chunk_id(self, content: str) -> str:
        """Generate a unique ID for a chunk based on its content."""
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _save_data(self):
        """Save embeddings and metadata to disk."""
        try:
            data_dir = "data/vector_db"
            os.makedirs(data_dir, exist_ok=True)
            
            # Save embeddings
            with open(f"{data_dir}/embeddings.pkl", "wb") as f:
                pickle.dump(self.embeddings, f)
            
            # Save chunks and metadata
            with open(f"{data_dir}/chunks.json", "w") as f:
                json.dump(self.chunks, f, indent=2)
            
            with open(f"{data_dir}/metadata.json", "w") as f:
                json.dump(self.metadata, f, indent=2)
            
            self.logger.info("Vector database data saved successfully")
            
        except Exception as e:
            self.logger.error(f"Error saving vector database data: {str(e)}")
    
    def _load_data(self):
        """Load embeddings and metadata from disk."""
        try:
            data_dir = "data/vector_db"
            
            # Load embeddings
            if os.path.exists(f"{data_dir}/embeddings.pkl"):
                with open(f"{data_dir}/embeddings.pkl", "rb") as f:
                    self.embeddings = pickle.load(f)
            
            # Load chunks
            if os.path.exists(f"{data_dir}/chunks.json"):
                with open(f"{data_dir}/chunks.json", "r") as f:
                    self.chunks = json.load(f)
            
            # Load metadata
            if os.path.exists(f"{data_dir}/metadata.json"):
                with open(f"{data_dir}/metadata.json", "r") as f:
                    self.metadata = json.load(f)
            
            self.logger.info(f"Loaded {len(self.chunks)} medical knowledge chunks")
            
        except Exception as e:
            self.logger.error(f"Error loading vector database data: {str(e)}")
            self.embeddings = []
            self.chunks = []
            self.metadata = []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database."""
        return {
            "total_chunks": len(self.chunks),
            "model_name": self.model_name,
            "last_updated": datetime.utcnow().isoformat(),
            "data_loaded": len(self.chunks) > 0
        }
    
    def clear_data(self) -> bool:
        """Clear all data from the vector database."""
        try:
            self.embeddings = []
            self.chunks = []
            self.metadata = []
            
            # Remove saved files
            data_dir = "data/vector_db"
            for filename in ["embeddings.pkl", "chunks.json", "metadata.json"]:
                filepath = f"{data_dir}/{filename}"
                if os.path.exists(filepath):
                    os.remove(filepath)
            
            self.logger.info("Vector database cleared successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error clearing vector database: {str(e)}")
            return False
