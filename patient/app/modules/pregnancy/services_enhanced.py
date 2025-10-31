"""
Enhanced Pregnancy Services - Adds RAG + OpenAI features
KEEPS ALL EXISTING FUNCTIONALITY - just adds new enhanced features
NO BREAKING CHANGES to existing endpoints
"""
from flask import jsonify
from app.shared.external_services.pregnancy_service import PregnancyService
from app.core.database import db
import asyncio

# Import enhanced RAG services
try:
    from app.shared.pregnancy_rag.pregnancy_data import PregnancyDataService
    from app.shared.pregnancy_rag.openai_service import OpenAIBabySizeService
    from app.shared.pregnancy_rag.baby_image_generator import BabySizeImageGenerator
    from app.shared.pregnancy_rag.services.rag_service import RAGService
    from app.shared.pregnancy_rag.services.patient_backend_service import PatientBackendService
    from app.shared.pregnancy_rag.services.dual_image_service import DualImageService
    RAG_AVAILABLE = True
    print("✅ Enhanced RAG pregnancy services available")
except ImportError as e:
    print(f"[WARN] Enhanced RAG services not available: {e}")
    RAG_AVAILABLE = False

# Initialize existing service (KEEP EXISTING)
pregnancy_service = PregnancyService()

# Initialize enhanced services (NEW)
if RAG_AVAILABLE:
    try:
        pregnancy_data_service_rag = PregnancyDataService()
        
        # Initialize OpenAI (optional)
        try:
            openai_service_rag = OpenAIBabySizeService()
            print("✅ OpenAI RAG service initialized")
        except:
            openai_service_rag = None
            print("⚠️  OpenAI service not available")
        
        # Initialize image generator
        image_generator_rag = BabySizeImageGenerator(openai_service_rag)
        
        # Initialize RAG service (optional)
        rag_service = None
        try:
            patient_backend_service_rag = PatientBackendService()
            if pregnancy_data_service_rag.use_qdrant and pregnancy_data_service_rag.qdrant_service:
                rag_service = RAGService(
                    pregnancy_data_service_rag.qdrant_service,
                    patient_backend_service_rag
                )
                print("✅ RAG personalization service initialized")
        except Exception as e:
            print(f"⚠️  RAG service initialization failed: {e}")
        
        # Initialize Dual Image Service
        dual_image_service = DualImageService(
            pregnancy_service=pregnancy_data_service_rag,
            rag_service=rag_service,
            openai_service=openai_service_rag,
            image_generator=image_generator_rag
        )
        print("✅ Dual Image Service initialized")
        
    except Exception as e:
        print(f"⚠️  Enhanced services initialization failed: {e}")
        RAG_AVAILABLE = False
else:
    pregnancy_data_service_rag = None
    rag_service = None
    dual_image_service = None

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _serialize_pydantic(obj):
    """Convert Pydantic models to dict for JSON serialization"""
    if hasattr(obj, 'model_dump'):
        return obj.model_dump()
    elif hasattr(obj, 'dict'):
        return obj.dict()
    elif isinstance(obj, dict):
        return {k: _serialize_pydantic(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_serialize_pydantic(item) for item in obj]
    else:
        return obj

def _run_async(coro, timeout=60):
    """Helper to run async functions in Flask sync context"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(asyncio.wait_for(coro, timeout=timeout))
        finally:
            loop.close()
    except asyncio.TimeoutError:
        raise TimeoutError(f"Operation timed out after {timeout} seconds")
    except Exception as e:
        print(f"Async execution error: {e}")
        raise

# =============================================================================
# EXISTING SERVICES - KEEP ALL (NO CHANGES)
# =============================================================================

def get_pregnancy_week_service(week):
    """KEEP EXISTING - NO CHANGES"""
    try:
        result = pregnancy_service.get_pregnancy_week_data(week)
        return jsonify(result.dict()), 200 if result.success else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

def get_all_pregnancy_weeks_service():
    """KEEP EXISTING - NO CHANGES"""
    try:
        weeks_data = pregnancy_service.get_all_pregnancy_weeks()
        return jsonify({
            'success': True,
            'data': {str(week): week_data.dict() for week, week_data in weeks_data.items()},
            'message': f'Successfully retrieved data for {len(weeks_data)} weeks'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

def get_trimester_weeks_service(trimester):
    """KEEP EXISTING - NO CHANGES"""
    try:
        if trimester not in [1, 2, 3]:
            return jsonify({
                'success': False,
                'message': 'Trimester must be 1, 2, or 3'
            }), 400
        
        weeks_data = pregnancy_service.get_trimester_weeks(trimester)
        return jsonify({
            'success': True,
            'trimester': trimester,
            'weeks': {str(week): week_data.dict() for week, week_data in weeks_data.items()},
            'message': f'Successfully retrieved weeks for trimester {trimester}'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

# KEEP ALL OTHER EXISTING SERVICES (baby size, symptoms, tracking, etc.)
# Import from original services.py
from app.modules.pregnancy.services import (
    get_baby_size_image_service,
    save_pregnancy_tracking_service,
    get_pregnancy_tracking_history_service,
    calculate_pregnancy_progress_service,
    update_patient_pregnancy_week_service,
    save_kick_session_service,
    get_kick_history_service,
    get_current_pregnancy_week_service
)

# =============================================================================
# NEW ENHANCED SERVICES - ADD RAG + OpenAI features
# =============================================================================

def get_enhanced_week_data_service(week, patient_id=None, use_mock_data=True, include_rag_analysis=True, image_method='all'):
    """NEW: Get enhanced week data with RAG + OpenAI"""
    if not RAG_AVAILABLE or not dual_image_service:
        return jsonify({
            'success': False,
            'error': 'Enhanced RAG features not available'
        }), 503
    
    try:
        enhanced_data = _run_async(
            dual_image_service.get_enhanced_week_data_with_image(
                week=week,
                patient_id=patient_id,
                use_mock_data=use_mock_data,
                include_rag_analysis=include_rag_analysis
            )
        )
        
        # Add service status
        enhanced_data['service_status'] = dual_image_service.get_service_status()
        
        # Filter images if requested
        if image_method != 'all' and 'images' in enhanced_data:
            filtered_images = {}
            if image_method in enhanced_data['images']:
                filtered_images[image_method] = enhanced_data['images'][image_method]
            enhanced_data['images'] = filtered_images
        
        enhanced_data['message'] = f'Enhanced week {week} data with RAG + OpenAI'
        
        serialized_data = _serialize_pydantic(enhanced_data)
        return jsonify(serialized_data), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}'
        }), 500

def semantic_search_service(query, limit=5):
    """NEW: Semantic search on pregnancy data"""
    if not RAG_AVAILABLE or not pregnancy_data_service_rag:
        return jsonify({
            'success': False,
            'error': 'Semantic search requires Qdrant RAG service'
        }), 503
    
    try:
        if not query or len(query.strip()) < 3:
            return jsonify({
                'success': False,
                'error': 'Query must be at least 3 characters'
            }), 400
        
        results = pregnancy_data_service_rag.semantic_search(query, limit=limit)
        serialized_results = _serialize_pydantic(results)
        
        return jsonify({
            'success': True,
            'query': query,
            'results': serialized_results,
            'total_results': len(results),
            'message': f'Found {len(results)} results'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Search failed: {str(e)}'
        }), 500

def get_rag_personalized_developments_service(week, patient_id, use_ai=True, use_mock_data=False):
    """NEW: RAG-powered personalized developments"""
    if not RAG_AVAILABLE or not rag_service:
        return jsonify({
            'success': False,
            'error': 'RAG personalization requires Qdrant service'
        }), 503
    
    try:
        rag_response = _run_async(
            rag_service.get_personalized_developments(
                week=week,
                patient_id=patient_id,
                use_openai=use_ai,
                use_mock_data=use_mock_data
            ),
            timeout=60
        )
        
        response_dict = _serialize_pydantic(rag_response)
        return jsonify(response_dict), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'RAG processing error: {str(e)}'
        }), 500

# Keep using existing OpenAI services for symptoms, wellness, nutrition, screening
# These are already in the original services.py - just re-export them
async def get_ai_baby_size_service(week):
    """KEEP EXISTING - Use original service"""
    try:
        result = await pregnancy_service.get_ai_baby_size(week)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

async def get_early_symptoms_service(week):
    """KEEP EXISTING - Use original service"""
    try:
        result = await pregnancy_service.get_early_symptoms(week)
        return jsonify(result.dict()), 200 if result.success else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

async def get_prenatal_screening_service(week):
    """KEEP EXISTING - Use original service"""
    try:
        result = await pregnancy_service.get_prenatal_screening(week)
        return jsonify(result.dict()), 200 if result.success else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

async def get_wellness_tips_service(week):
    """KEEP EXISTING - Use original service"""
    try:
        result = await pregnancy_service.get_wellness_tips(week)
        return jsonify(result.dict()), 200 if result.success else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

async def get_nutrition_tips_service(week):
    """KEEP EXISTING - Use original service"""
    try:
        result = await pregnancy_service.get_nutrition_tips(week)
        return jsonify(result.dict()), 200 if result.success else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

def get_openai_status_service():
    """KEEP EXISTING - Use original service"""
    try:
        status = pregnancy_service.get_openai_status()
        return jsonify(status), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

