"""
Qdrant Service for Trimester Module

This service handles all interactions with the Qdrant vector database
for semantic search and RAG functionality.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue,
    PayloadSchemaType
)
from typing import List, Dict, Optional, Any
import uuid
import json

from ..schemas import PregnancyWeek, KeyDevelopment
from ..config import settings

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
            print("[OK] SentenceTransformers loaded successfully in Trimester QdrantService")
        except ImportError as e:
            SENTENCE_TRANSFORMERS_AVAILABLE = False
            print(f"[WARN] SentenceTransformers not available: {e}")
        except OSError as e:
            SENTENCE_TRANSFORMERS_AVAILABLE = False
            print(f"[WARN] SentenceTransformers DLL error (PyTorch issue): {e}")
    return SentenceTransformer


class QdrantService:
    """Service for Qdrant vector database operations"""
    
    def __init__(self):
        """Initialize Qdrant client and embedding model"""
        if not settings.QDRANT_URL:
            raise ValueError("QDRANT_URL is not configured. Please set it in your .env file.")
        
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            timeout=60  # Increased timeout for patient app
        )
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        
        # Lazy load embedding model
        SentenceTransformer = _lazy_import_sentence_transformers()
        if SENTENCE_TRANSFORMERS_AVAILABLE and SentenceTransformer:
            try:
                self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
                print("[OK] Embedding model initialized successfully in Trimester QdrantService")
            except Exception as e:
                print(f"[ERROR] Embedding model initialization failed: {e}")
                self.embedding_model = None
        else:
            self.embedding_model = None
            print("[WARN] Embedding model not available - semantic search will be disabled")
        
        self.vector_size = 384  # all-MiniLM-L6-v2 produces 384-dimensional vectors
        
        # Initialize collection
        self.create_collection()
    
    def create_collection(self):
        """Create Qdrant collection if it doesn't exist"""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
                )
                print(f"Created collection: {self.collection_name}")
                
                # Create payload indexes for filtering
                self._create_payload_indexes()
            else:
                print(f"Collection {self.collection_name} already exists")
                # Ensure indexes exist
                self._create_payload_indexes()
        except Exception as e:
            print(f"Error creating collection: {e}")
            raise
    
    def _create_payload_indexes(self):
        """Create payload indexes for efficient filtering"""
        try:
            # Create index for week field
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="week",
                field_schema=PayloadSchemaType.INTEGER
            )
            
            # Create index for trimester field
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="trimester",
                field_schema=PayloadSchemaType.INTEGER
            )
            
            print("Created payload indexes for week and trimester")
        except Exception as e:
            print(f"Error creating payload indexes: {e}")
    
    def add_pregnancy_week(self, week_data: PregnancyWeek):
        """Add a pregnancy week to the vector database"""
        if not self.embedding_model:
            print("[WARN] Embedding model not available - cannot add pregnancy week")
            return
            
        try:
            # Create text content for embedding
            text_content = self._create_text_content(week_data)
            
            # Generate embedding
            embedding = self.embedding_model.encode(text_content).tolist()
            
            # Create point
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "week": week_data.week,
                    "trimester": week_data.trimester,
                    "days_remaining": week_data.days_remaining,
                    "baby_size": week_data.baby_size.dict() if hasattr(week_data.baby_size, 'dict') else week_data.baby_size,
                    "key_developments": [dev.dict() if hasattr(dev, 'dict') else dev for dev in week_data.key_developments],
                    "symptoms": week_data.symptoms,
                    "tips": week_data.tips,
                    "text_content": text_content
                }
            )
            
            # Insert point
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            print(f"Added week {week_data.week} to Qdrant")
            
        except Exception as e:
            print(f"Error adding pregnancy week {week_data.week}: {e}")
            raise
    
    def _create_text_content(self, week_data: PregnancyWeek) -> str:
        """Create searchable text content from pregnancy week data"""
        content_parts = [
            f"Week {week_data.week}",
            f"Trimester {week_data.trimester}",
            f"Baby size: {week_data.baby_size.size}",
        ]
        
        # Add key developments
        for dev in week_data.key_developments:
            content_parts.append(f"Development: {dev.title} - {dev.description}")
        
        # Add symptoms
        if week_data.symptoms:
            content_parts.append(f"Symptoms: {', '.join(week_data.symptoms)}")
        
        # Add tips
        if week_data.tips:
            content_parts.append(f"Tips: {', '.join(week_data.tips)}")
        
        return " ".join(content_parts)
    
    def semantic_search(self, query: str, limit: int = 5, week_filter: Optional[int] = None) -> List[Dict[str, Any]]:
        """Perform semantic search on pregnancy data"""
        if not self.embedding_model:
            print("[WARN] Embedding model not available - semantic search disabled")
            return []
            
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Build filter
            search_filter = None
            if week_filter is not None:
                search_filter = Filter(
                    must=[
                        FieldCondition(
                            key="week",
                            match=MatchValue(value=week_filter)
                        )
                    ]
                )
            
            # Perform search
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                query_filter=search_filter
            )
            
            # Format results
            results = []
            for hit in search_result:
                results.append({
                    "week": hit.payload.get("week"),
                    "trimester": hit.payload.get("trimester"),
                    "score": hit.score,
                    "content": hit.payload.get("text_content", ""),
                    "baby_size": hit.payload.get("baby_size"),
                    "key_developments": hit.payload.get("key_developments", []),
                    "symptoms": hit.payload.get("symptoms", []),
                    "tips": hit.payload.get("tips", [])
                })
            
            return results
            
        except Exception as e:
            print(f"Error performing semantic search: {e}")
            return []
    
    def get_week_by_number(self, week: int) -> Optional[Dict[str, Any]]:
        """Get specific week data by week number"""
        try:
            # Search for specific week
            results = self.semantic_search(f"week {week}", limit=1, week_filter=week)
            
            if results:
                return results[0]
            else:
                return None
                
        except Exception as e:
            print(f"Error getting week {week}: {e}")
            return None
    
    def get_weeks_by_trimester(self, trimester: int) -> List[Dict[str, Any]]:
        """Get all weeks for a specific trimester"""
        if not self.embedding_model:
            print("[WARN] Embedding model not available - cannot get weeks by trimester")
            return []
            
        try:
            # Search with trimester filter
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="trimester",
                        match=MatchValue(value=trimester)
                    )
                ]
            )
            
            # Generate a generic embedding for trimester search
            query_embedding = self.embedding_model.encode(f"trimester {trimester} pregnancy").tolist()
            
            # Perform search
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=20,  # Maximum weeks per trimester
                query_filter=search_filter
            )
            
            # Format results
            results = []
            for hit in search_result:
                results.append({
                    "week": hit.payload.get("week"),
                    "trimester": hit.payload.get("trimester"),
                    "score": hit.score,
                    "baby_size": hit.payload.get("baby_size"),
                    "key_developments": hit.payload.get("key_developments", []),
                    "symptoms": hit.payload.get("symptoms", []),
                    "tips": hit.payload.get("tips", [])
                })
            
            # Sort by week number
            results.sort(key=lambda x: x.get("week", 0))
            
            return results
            
        except Exception as e:
            print(f"Error getting weeks for trimester {trimester}: {e}")
            return []
    
    def health_check(self) -> Dict[str, Any]:
        """Check Qdrant service health"""
        try:
            # Try to get collections
            collections = self.client.get_collections()
            
            return {
                "status": "healthy",
                "collection_name": self.collection_name,
                "collections_count": len(collections.collections),
                "embedding_model": settings.EMBEDDING_MODEL,
                "vector_size": self.vector_size
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "collection_name": self.collection_name
            }
