"""
Advanced Symptoms Service - Integrated from FastAPI symptoms module
Provides AI-powered pregnancy symptom analysis using vector embeddings and LLM
"""

import os
import json
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
import openai
# Optional imports with fallbacks - lazy loading to avoid DLL issues
SENTENCE_TRANSFORMERS_AVAILABLE = False
QDRANT_AVAILABLE = False
SentenceTransformer = None
QdrantClient = None
models = None

def _lazy_import_sentence_transformers():
    """Lazy import sentence transformers to avoid DLL issues"""
    global SentenceTransformer, SENTENCE_TRANSFORMERS_AVAILABLE
    if SentenceTransformer is None:
        try:
            from sentence_transformers import SentenceTransformer
            SENTENCE_TRANSFORMERS_AVAILABLE = True
            print("[OK] SentenceTransformers loaded successfully in SymptomsService")
        except ImportError as e:
            SENTENCE_TRANSFORMERS_AVAILABLE = False
            print(f"[WARN] sentence_transformers not available: {e}")
        except OSError as e:
            SENTENCE_TRANSFORMERS_AVAILABLE = False
            print(f"[WARN] sentence_transformers DLL error (PyTorch issue): {e}")
    return SentenceTransformer

def _lazy_import_qdrant():
    """Lazy import qdrant client"""
    global QdrantClient, models, QDRANT_AVAILABLE
    if QdrantClient is None:
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.http import models
            QDRANT_AVAILABLE = True
            print("[OK] Qdrant client loaded successfully in SymptomsService")
        except ImportError as e:
            QDRANT_AVAILABLE = False
            print(f"[WARN] qdrant_client not available: {e}")
    return QdrantClient

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    print("[WARN] openai not available, using fallback mode")
    OPENAI_AVAILABLE = False
    openai = None

class SymptomsService:
    def __init__(self):
        """Initialize the symptoms service with vector database and LLM"""
        self.embedding_model = None
        self.qdrant_client = None
        self.openai_client = None
        self.mongo_client = None
        self.db = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize all required services"""
        try:
            # Initialize embedding model using lazy loading
            SentenceTransformer = _lazy_import_sentence_transformers()
            if SENTENCE_TRANSFORMERS_AVAILABLE and SentenceTransformer is not None:
                model_name = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
                self.embedding_model = SentenceTransformer(model_name)
                print(f"[OK] Embedding model loaded: {model_name}")
            else:
                print("[WARN] SentenceTransformers not available, using fallback mode")
                self.embedding_model = None
            
            # Initialize Qdrant client using lazy loading
            QdrantClient = _lazy_import_qdrant()
            if QDRANT_AVAILABLE and QdrantClient is not None:
                qdrant_url = os.getenv('QDRANT_URL')
                qdrant_api_key = os.getenv('QDRANT_API_KEY')
                if qdrant_url and qdrant_api_key:
                    self.qdrant_client = QdrantClient(
                        url=qdrant_url,
                        api_key=qdrant_api_key,
                        timeout=60
                    )
                    print("[OK] Qdrant client initialized")
                else:
                    print("[WARN] Qdrant credentials not found, using fallback mode")
            else:
                print("[WARN] Qdrant client not available, using fallback mode")
            
            # Initialize OpenAI client
            if OPENAI_AVAILABLE and openai is not None:
                openai_api_key = os.getenv('OPENAI_API_KEY')
                if openai_api_key:
                    self.openai_client = openai.OpenAI(api_key=openai_api_key)
                    print("[OK] OpenAI client initialized")
                else:
                    print("[WARN] OpenAI API key not found, using fallback mode")
            else:
                print("[WARN] OpenAI client not available, using fallback mode")
            
            # Initialize MongoDB client
            mongo_uri = os.getenv('MONGO_URI')
            if mongo_uri:
                self.mongo_client = MongoClient(mongo_uri)
                db_name = os.getenv('DB_NAME', 'patients_db')
                self.db = self.mongo_client[db_name]
                print("[OK] MongoDB client initialized")
            else:
                print("[WARN] MongoDB URI not found")
                
        except Exception as e:
            print(f"[ERROR] Error initializing symptoms service: {e}")
    
    def get_embeddings(self, text: str) -> List[float]:
        """Generate embeddings for text"""
        try:
            if self.embedding_model is not None:
                return self.embedding_model.encode(text).tolist()
            else:
                # Fallback: return random embeddings
                return np.random.random(384).tolist()
        except Exception as e:
            print(f"[ERROR] Error generating embeddings: {e}")
            return np.random.random(384).tolist()
    
    def retrieve_knowledge(self, query: str, weeks_pregnant: int, top_k: int = 5) -> List[Dict]:
        """Retrieve relevant knowledge from vector database"""
        try:
            if not self.qdrant_client:
                return []
            
            # Generate query embedding
            query_embedding = self.get_embeddings(query)
            
            # Determine trimester
            trimester = self._get_trimester(weeks_pregnant)
            
            # Search in Qdrant
            collection_name = os.getenv('QDRANT_COLLECTION', 'pregnancy_knowledge')
            search_result = self.qdrant_client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=top_k,
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="trimester",
                            match=models.MatchValue(value=trimester)
                        )
                    ]
                ) if trimester != "all" else None
            )
            
            # Format results
            suggestions = []
            for hit in search_result:
                suggestions.append({
                    'id': str(hit.id),
                    'text': hit.payload.get('text', ''),
                    'source': hit.payload.get('source', 'Unknown'),
                    'score': hit.score,
                    'metadata': hit.payload
                })
            
            print(f"[*] Retrieved {len(suggestions)} knowledge items")
            return suggestions
            
        except Exception as e:
            print(f"[ERROR] Error retrieving knowledge: {e}")
            return []
    
    def generate_llm_response(self, query: str, weeks_pregnant: int, suggestions: List[Dict]) -> Optional[Dict]:
        """Generate LLM response based on retrieved suggestions"""
        try:
            if not self.openai_client or not suggestions:
                return None
            
            # Prepare context from suggestions
            context_text = "\n\n".join([s['text'] for s in suggestions])
            
            # System prompt
            system_prompt = os.getenv(
                'SUMMARY_SYSTEM_PROMPT',
                "You are a cautious medical assistant supporting an obstetrician. "
                "Your ONLY knowledge source is the evidence bullets provided in the user message. "
                "Do NOT use outside knowledge.\n\n"
                "Primary task:\n"
                "- Based on the evidence, determine the overall urgency level (mild, moderate, urgent) for the patient's symptoms.\n"
                "- Provide a concise, trimester-specific guidance summary for a pregnant patient.\n\n"
                "Instructions:\n"
                "- Use 3–5 short bullets.\n"
                "- Include one bullet explicitly stating when to seek urgent care, based on evidence triage tags.\n"
                "- Be clear, factual, and non-alarmist.\n"
                "- If evidence is conflicting or insufficient, state that clearly.\n"
                "- Do NOT invent facts not present in evidence.\n"
                "- Do NOT recommend medications, dosages, diagnostic codes, or brand names.\n"
                "- Do NOT make definitive diagnoses; frame as possible concerns and next steps.\n"
                "- Keep lay-friendly tone; avoid jargon where possible.\n"
                "- Assume this is general guidance, not a substitute for clinical judgment.\n\n"
                "Output format:\n"
                "- Start with: 'Urgency level: <mild/moderate/urgent/uncertain>'\n"
                "- Then list plain text bullets (no numbering, no markdown headings).\n"
                "- Each bullet ≤ 25 words."
            )
            
            # User message
            user_message = f"Patient query: {query}\n\nPregnancy week: {weeks_pregnant}\n\nEvidence:\n{context_text}"
            
            # Call OpenAI
            response = self.openai_client.chat.completions.create(
                model=os.getenv('LLM_MODEL', 'gpt-4o-mini'),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            return {
                'text': response.choices[0].message.content,
                'disclaimers': os.getenv('DISCLAIMER_TEXT', 'This information is educational and not a medical diagnosis.')
            }
            
        except Exception as e:
            print(f"[ERROR] Error generating LLM response: {e}")
            return None
    
    def generate_fallback_response(self, query: str, weeks_pregnant: int) -> Dict:
        """Generate fallback response when vector search or LLM fails"""
        try:
            if self.openai_client:
                # Use LLM for fallback
                system_prompt = os.getenv(
                    'FALLBACK_SYSTEM_PROMPT',
                    "You are a cautious pregnancy symptom assistant. Provide 3-5 concise, trimester-aware self-care suggestions, "
                    "avoid medications/doses, include when to seek urgent care, and always add a medical disclaimer."
                )
                
                user_message = f"Patient query: {query}\n\nPregnancy week: {weeks_pregnant}"
                
                response = self.openai_client.chat.completions.create(
                    model=os.getenv('LLM_MODEL', 'gpt-4o-mini'),
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=300,
                    temperature=0.3
                )
                
                return {
                    'text': response.choices[0].message.content,
                    'disclaimers': os.getenv('DISCLAIMER_TEXT', 'This information is educational and not a medical diagnosis.')
                }
            else:
                # Static fallback
                return {
                    'text': os.getenv(
                        'FALLBACK_STATIC_TEXT',
                        "General guidance: rest, hydrate, track symptoms, avoid triggers, and contact your prenatal provider for advice."
                    ),
                    'disclaimers': os.getenv('DISCLAIMER_TEXT', 'This information is educational and not a medical diagnosis.')
                }
                
        except Exception as e:
            print(f"[ERROR] Error generating fallback response: {e}")
            return {
                'text': "Please consult your healthcare provider for personalized advice.",
                'disclaimers': "This information is educational and not a medical diagnosis."
            }
    
    def _get_trimester(self, weeks_pregnant: int) -> str:
        """Determine trimester from weeks pregnant"""
        if weeks_pregnant <= 0:
            return "all"
        elif weeks_pregnant <= 13:
            return "first"
        elif weeks_pregnant <= 26:
            return "second"
        elif weeks_pregnant <= 42:
            return "third"
        else:
            return "all"
    
    def analyze_symptoms(self, query: str, weeks_pregnant: int, user_id: Optional[str] = None) -> Dict:
        """Main method to analyze symptoms and provide recommendations"""
        try:
            print(f"[*] Analyzing symptoms: '{query}' for week {weeks_pregnant}")
            
            # Step 1: Retrieve knowledge from vector database
            suggestions = self.retrieve_knowledge(query, weeks_pregnant)
            
            if suggestions:
                # Step 2: Generate LLM response based on retrieved knowledge
                llm_response = self.generate_llm_response(query, weeks_pregnant, suggestions)
                if llm_response:
                    return llm_response
            
            # Step 3: Fallback response
            return self.generate_fallback_response(query, weeks_pregnant)
            
        except Exception as e:
            print(f"[ERROR] Error analyzing symptoms: {e}")
            return self.generate_fallback_response(query, weeks_pregnant)
    
    def save_knowledge_to_mongo(self, text: str, source: str = "YourClinic", 
                               tags: List[str] = None, trimester: str = "all") -> str:
        """Save knowledge to MongoDB for later ingestion"""
        try:
            if not self.db:
                return None
            
            collection_name = os.getenv('MONGO_COLLECTION', 'pregnancy_knowledge')
            collection = self.db[collection_name]
            
            doc = {
                'text': text,
                'source': source,
                'tags': tags or [],
                'trimester': trimester,
                'updated_at': datetime.utcnow()
            }
            
            result = collection.insert_one(doc)
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"[ERROR] Error saving knowledge to MongoDB: {e}")
            return None

# Global instance
symptoms_service = SymptomsService()
