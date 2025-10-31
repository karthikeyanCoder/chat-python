from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue,
    PayloadSchemaType
)
from typing import List, Dict, Optional
from app.shared.pregnancy_rag.pregnancy_models import PregnancyWeek, KeyDevelopment
from app.shared.pregnancy_rag.pregnancy_config import settings
import uuid

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
            print("[OK] SentenceTransformers loaded successfully in QdrantService")
        except ImportError as e:
            SENTENCE_TRANSFORMERS_AVAILABLE = False
            print(f"[WARN] SentenceTransformers not available: {e}")
        except OSError as e:
            SENTENCE_TRANSFORMERS_AVAILABLE = False
            print(f"[WARN] SentenceTransformers DLL error (PyTorch issue): {e}")
    return SentenceTransformer


class QdrantService:
    def __init__(self):
        """Initialize Qdrant client and embedding model"""
        if not settings.QDRANT_URL:
            raise ValueError("QDRANT_URL is not configured. Please set it in your .env file.")
        
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            timeout=60  # Increase timeout for cloud Qdrant operations
        )
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        
        # Lazy load embedding model
        SentenceTransformer = _lazy_import_sentence_transformers()
        if SENTENCE_TRANSFORMERS_AVAILABLE and SentenceTransformer:
            try:
                self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
                print("[OK] Embedding model initialized successfully in QdrantService")
            except Exception as e:
                print(f"[ERROR] Embedding model initialization failed: {e}")
                self.embedding_model = None
        else:
            self.embedding_model = None
            print("[WARN] Embedding model not available - semantic search will be disabled")
        
        self.vector_size = 384  # all-MiniLM-L6-v2 produces 384-dimensional vectors
        
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
        """Create indexes on payload fields for efficient filtering"""
        try:
            # Create index on 'week' field (integer)
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="week",
                field_schema=PayloadSchemaType.INTEGER
            )
            print(f"Created index on 'week' field")
            
            # Create index on 'trimester' field (integer)
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="trimester",
                field_schema=PayloadSchemaType.INTEGER
            )
            print(f"Created index on 'trimester' field")
        except Exception as e:
            # Indexes might already exist, that's okay
            print(f"Note: {e}")
    
    def _convert_week_to_text(self, week_data: PregnancyWeek) -> str:
        """Convert PregnancyWeek object to searchable text"""
        # Combine all relevant information
        developments_text = " ".join([
            f"{dev.title}: {dev.description}" for dev in week_data.key_developments
        ])
        symptoms_text = " ".join(week_data.symptoms)
        tips_text = " ".join(week_data.tips)
        
        text = f"""
        Week {week_data.week} of pregnancy, Trimester {week_data.trimester}.
        Baby size: {week_data.baby_size.size}, weight {week_data.baby_size.weight}, length {week_data.baby_size.length}.
        Key developments: {developments_text}.
        Common symptoms: {symptoms_text}.
        Tips: {tips_text}.
        """
        return text.strip()
    
    def upload_week_data(self, week_data: PregnancyWeek):
        """Upload a single week's data to Qdrant"""
        if not self.embedding_model:
            print("[WARN] Embedding model not available - cannot upload week data")
            return
            
        # Convert to searchable text and generate embedding
        text = self._convert_week_to_text(week_data)
        embedding = self.embedding_model.encode(text).tolist()
        
        # Prepare payload with all week data
        payload = {
            "week": week_data.week,
            "trimester": week_data.trimester,
            "days_remaining": week_data.days_remaining,
            "baby_size": week_data.baby_size.dict(),
            "key_developments": [dev.dict() for dev in week_data.key_developments],
            "symptoms": week_data.symptoms,
            "tips": week_data.tips,
            "searchable_text": text
        }
        
        # Upload to Qdrant
        point_id = str(uuid.uuid4())
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                )
            ]
        )
        print(f"Uploaded week {week_data.week} to Qdrant")
    
    def upload_multiple_weeks(self, weeks_data: List[PregnancyWeek]):
        """Upload multiple weeks data to Qdrant"""
        if not self.embedding_model:
            print("[WARN] Embedding model not available - cannot upload weeks data")
            return
            
        points = []
        
        for week_data in weeks_data:
            text = self._convert_week_to_text(week_data)
            embedding = self.embedding_model.encode(text).tolist()
            
            payload = {
                "week": week_data.week,
                "trimester": week_data.trimester,
                "days_remaining": week_data.days_remaining,
                "baby_size": week_data.baby_size.dict(),
                "key_developments": [dev.dict() for dev in week_data.key_developments],
                "symptoms": week_data.symptoms,
                "tips": week_data.tips,
                "searchable_text": text
            }
            
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload=payload
                )
            )
        
        # Upload all points at once
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        print(f"Uploaded {len(points)} weeks to Qdrant")
    
    def get_week_by_number(self, week: int) -> Optional[PregnancyWeek]:
        """Retrieve a specific week's data by week number"""
        search_filter = Filter(
            must=[
                FieldCondition(
                    key="week",
                    match=MatchValue(value=week)
                )
            ]
        )
        
        results = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=search_filter,
            limit=1
        )
        
        if results[0]:
            payload = results[0][0].payload
            return self._payload_to_pregnancy_week(payload)
        return None
    
    def get_weeks_by_trimester(self, trimester: int) -> List[PregnancyWeek]:
        """Retrieve all weeks for a specific trimester"""
        search_filter = Filter(
            must=[
                FieldCondition(
                    key="trimester",
                    match=MatchValue(value=trimester)
                )
            ]
        )
        
        results = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=search_filter,
            limit=100
        )
        
        weeks = []
        for point in results[0]:
            week_data = self._payload_to_pregnancy_week(point.payload)
            weeks.append(week_data)
        
        # Sort by week number
        weeks.sort(key=lambda x: x.week)
        return weeks
    
    def get_all_weeks(self) -> Dict[int, PregnancyWeek]:
        """Retrieve all weeks data"""
        results = self.client.scroll(
            collection_name=self.collection_name,
            limit=100
        )
        
        weeks_dict = {}
        for point in results[0]:
            week_data = self._payload_to_pregnancy_week(point.payload)
            weeks_dict[week_data.week] = week_data
        
        return weeks_dict
    
    def semantic_search(self, query: str, limit: int = 5) -> List[Dict]:
        """Perform semantic search on pregnancy data"""
        if not self.embedding_model:
            print("[WARN] Embedding model not available - semantic search disabled")
            return []
            
        # Generate embedding for the query
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Search in Qdrant
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit
        )
        
        results = []
        for result in search_results:
            results.append({
                "score": result.score,
                "week": result.payload["week"],
                "trimester": result.payload["trimester"],
                "data": self._payload_to_pregnancy_week(result.payload),
                "matched_text": result.payload["searchable_text"][:200] + "..."
            })
        
        return results
    
    def _payload_to_pregnancy_week(self, payload: dict) -> PregnancyWeek:
        """Convert Qdrant payload back to PregnancyWeek object"""
        from app.shared.pregnancy_rag.pregnancy_models import BabySize
        
        return PregnancyWeek(
            week=payload["week"],
            trimester=payload["trimester"],
            days_remaining=payload["days_remaining"],
            baby_size=BabySize(**payload["baby_size"]),
            key_developments=[KeyDevelopment(**dev) for dev in payload["key_developments"]],
            symptoms=payload["symptoms"],
            tips=payload["tips"]
        )
    
    def delete_collection(self):
        """Delete the collection (use with caution)"""
        self.client.delete_collection(collection_name=self.collection_name)
        print(f"Deleted collection: {self.collection_name}")

