"""
Quantum & LLM Module Routes
Handles quantum vector search and LLM operations
EXTRACTED FROM app_simple.py lines 5467-5706
"""

from flask import Blueprint, request
from .services import (
    quantum_health_check_service,
    quantum_collections_service,
    quantum_collection_status_service,
    llm_health_check_service,
    llm_test_service,
    add_knowledge_service,
    search_knowledge_service
)

# Get config values
import os
QDRANT_AVAILABLE = True  # Will be set based on actual availability
SENTENCE_TRANSFORMERS_AVAILABLE = True
OPENAI_AVAILABLE = True
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-4o-mini')
TOP_K = int(os.getenv('TOP_K', '5'))
QDRANT_COLLECTION = os.getenv('QDRANT_COLLECTION', 'pregnancy_knowledge')

quantum_llm_bp = Blueprint('quantum_llm', __name__)


@quantum_llm_bp.route('/quantum/health', methods=['GET'])
def quantum_health_check():
    """Check quantum vector service health"""
    return quantum_health_check_service(QDRANT_AVAILABLE, SENTENCE_TRANSFORMERS_AVAILABLE)


@quantum_llm_bp.route('/quantum/collections', methods=['GET'])
def quantum_collections():
    """Get Qdrant collections information"""
    return quantum_collections_service()


@quantum_llm_bp.route('/quantum/collection-status/<collection_name>', methods=['GET'])
def quantum_collection_status(collection_name):
    """Get specific collection status and statistics"""
    return quantum_collection_status_service(collection_name)


@quantum_llm_bp.route('/llm/health', methods=['GET'])
def llm_health_check():
    """Check LLM service health"""
    return llm_health_check_service(OPENAI_AVAILABLE, OPENAI_API_KEY, LLM_MODEL)


@quantum_llm_bp.route('/llm/test', methods=['POST'])
def llm_test():
    """Test LLM functionality with a simple prompt"""
    data = request.get_json()
    return llm_test_service(data, LLM_MODEL)


@quantum_llm_bp.route('/quantum/add-knowledge', methods=['POST'])
def add_knowledge():
    """Add knowledge document to Qdrant vector database"""
    data = request.get_json()
    return add_knowledge_service(data, QDRANT_COLLECTION)


@quantum_llm_bp.route('/quantum/search-knowledge', methods=['POST'])
def search_knowledge():
    """Search knowledge base using vector similarity"""
    data = request.get_json()
    return search_knowledge_service(data, TOP_K)
