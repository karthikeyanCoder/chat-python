"""
Quantum & LLM Module Services - FUNCTION-BASED MVC
EXTRACTED FROM app_simple.py lines 5467-5706
Business logic for quantum vector search and LLM operations

NO CHANGES TO LOGIC - Exact extraction, converted to function-based
"""

from flask import jsonify
from datetime import datetime
import uuid
from app.shared.quantum_service import quantum_service
from app.shared.llm_service import llm_service


def quantum_health_check_service(qdrant_available, sentence_transformers_available):
    """Check quantum vector service health - EXACT from line 5469"""
    return jsonify({
        'success': True,
        'qdrant_available': qdrant_available,
        'qdrant_connected': quantum_service.client is not None,
        'embedding_model_available': sentence_transformers_available,
        'embedding_model_loaded': quantum_service.embedding_model is not None,
        'collection_status': quantum_service.ensure_collection(),
        'timestamp': datetime.now().isoformat()
    })


def quantum_collections_service():
    """Get Qdrant collections information - EXACT from line 5482"""
    if not quantum_service.client:
        return jsonify({
            'success': False,
            'message': 'Qdrant client not available'
        }), 503
    
    try:
        collections = quantum_service.client.get_collections().collections
        names = [c.name for c in collections]
        return jsonify({
            'success': True,
            'collections': names,
            'total_collections': len(names),
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting collections: {str(e)}'
        }), 500


def quantum_collection_status_service(collection_name):
    """Get specific collection status and statistics - EXACT from line 5506"""
    if not quantum_service.client:
        return jsonify({
            'success': False,
            'message': 'Qdrant client not available'
        }), 503
    
    try:
        collection_info = quantum_service.client.get_collection(collection_name)
        collection_stats = quantum_service.client.get_collection(collection_name).dict()
        
        return jsonify({
            'success': True,
            'collection_name': collection_name,
            'status': collection_stats.get('status'),
            'vectors_count': collection_stats.get('vectors_count', 0),
            'points_count': collection_stats.get('points_count', 0),
            'segments_count': collection_stats.get('segments_count', 0),
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting collection status: {str(e)}'
        }), 500


def llm_health_check_service(openai_available, openai_api_key, llm_model):
    """Check LLM service health - EXACT from line 5534"""
    return jsonify({
        'success': True,
        'openai_available': openai_available,
        'openai_configured': bool(openai_api_key),
        'llm_client_connected': llm_service.client is not None,
        'model': llm_model,
        'timestamp': datetime.now().isoformat()
    })


def llm_test_service(data, llm_model):
    """Test LLM functionality with a simple prompt - EXACT from line 5546"""
    try:
        test_prompt = data.get('prompt', 'Hello, how are you?') if data else 'Hello, how are you?'
        
        if not llm_service.client:
            return jsonify({
                'success': False,
                'message': 'LLM service not available'
            }), 503
        
        response = llm_service.client.chat.completions.create(
            model=llm_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Respond briefly."},
                {"role": "user", "content": test_prompt}
            ],
            temperature=0.1,
            max_tokens=50
        )
        
        content = response.choices[0].message.content.strip()
        
        return jsonify({
            'success': True,
            'test_prompt': test_prompt,
            'response': content,
            'model_used': llm_model,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'LLM test failed: {str(e)}'
        }), 500


def add_knowledge_service(data, qdrant_collection):
    """Add knowledge document to Qdrant vector database - EXACT from line 5591"""
    try:
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        required_fields = ['text', 'source', 'trimester']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        if not quantum_service.client or not quantum_service.embedding_model:
            return jsonify({
                'success': False,
                'message': 'Quantum vector service not available'
            }), 503
        
        # Generate embedding for the text
        text_vector = quantum_service.embed_text(data['text'])
        if not text_vector:
            return jsonify({
                'success': False,
                'message': 'Failed to generate text embedding'
            }), 500
        
        # Create point structure
        from qdrant_client.models import PointStruct
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=text_vector,
            payload={
                "text": data['text'],
                "source": data['source'],
                "trimester": data['trimester'],
                "tags": data.get('tags', []),
                "triage": data.get('triage', 'general'),
                "updated_at": datetime.now().isoformat()
            }
        )
        
        # Ensure collection exists
        quantum_service.ensure_collection()
        
        # Upsert point
        quantum_service.client.upsert(
            collection_name=qdrant_collection,
            points=[point]
        )
        
        return jsonify({
            'success': True,
            'message': 'Knowledge document added successfully',
            'document_id': point.id,
            'vector_size': len(text_vector),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"Error adding knowledge: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


def search_knowledge_service(data, top_k):
    """Search knowledge base using vector similarity - EXACT from line 5662"""
    try:
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        query_text = data.get('text', '').strip()
        weeks_pregnant = data.get('weeks_pregnant', 1)
        limit = data.get('limit', top_k)
        
        if not query_text:
            return jsonify({
                'success': False,
                'message': 'Query text is required'
            }), 400
        
        if not quantum_service.client or not quantum_service.embedding_model:
            return jsonify({
                'success': False,
                'message': 'Quantum vector service not available'
            }), 503
        
        # Search knowledge base
        suggestions = quantum_service.search_knowledge(query_text, weeks_pregnant)
        
        return jsonify({
            'success': True,
            'query_text': query_text,
            'weeks_pregnant': weeks_pregnant,
            'suggestions': suggestions,
            'total_found': len(suggestions),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"Error searching knowledge: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500
