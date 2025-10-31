"""
Routes for Trimester Module

This file contains all Flask routes for the trimester module,
converted from the original FastAPI endpoints.
"""

from flask import Blueprint, request, jsonify, Response
from functools import wraps
import asyncio
import base64
import json
from typing import Optional, Dict, Any
from datetime import datetime

# Create blueprint
trimester_bp = Blueprint('trimester', __name__)

from .services import PregnancyDataService, OpenAIBabySizeService
from .rag import RAGService, QdrantService, PatientBackendService, DualImageService
from .image_generator import BabySizeImageGenerator
from .schemas import (
    PregnancyResponse, QuickActionResponse, RAGPregnancyResponse
)
from .config import settings

# Import auth decorator and database
from app.core.auth import token_required
from app.core.database import db


# Initialize services
pregnancy_service = PregnancyDataService()
openai_service = None
image_generator = None
patient_service = PatientBackendService()
rag_service = None
dual_image_service = None

# Initialize OpenAI service if API key is available
try:
    openai_service = OpenAIBabySizeService()
    print("✅ OpenAI service initialized successfully")
except ValueError as e:
    print(f"Warning: OpenAI service not available: {e}")

# Initialize image generator
try:
    image_generator = BabySizeImageGenerator(openai_service)
    print("✅ Baby size image generator initialized")
except Exception as e:
    print(f"Warning: Image generator initialization failed: {e}")

# Initialize RAG services if Qdrant is available
try:
    if pregnancy_service.use_qdrant and pregnancy_service.qdrant_service:
        rag_service = RAGService(pregnancy_service.qdrant_service, patient_service)
        print("✅ RAG service initialized successfully")
    else:
        print("⚠️  RAG service not available - Qdrant not configured")
except Exception as e:
    print(f"⚠️  RAG service initialization failed: {e}")

# Initialize Dual Image Service
try:
    dual_image_service = DualImageService(
        pregnancy_service=pregnancy_service,
        rag_service=rag_service,
        openai_service=openai_service,
        image_generator=image_generator
    )
    print("✅ Dual Image Service initialized")
except Exception as e:
    print(f"❌ Dual Image Service initialization failed: {e}")
    dual_image_service = None


def _run_async(coro):
    """Helper function to run async functions in Flask"""
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)
    except RuntimeError:
        # Create new event loop if none exists
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()


def _serialize_pydantic(obj):
    """Helper function to serialize Pydantic models"""
    if hasattr(obj, 'model_dump'):
        return obj.model_dump()  # Pydantic v2
    elif hasattr(obj, 'dict'):
        return obj.dict()  # Pydantic v1
    else:
        return obj


def _get_patient_current_week(patient_id: str) -> int:
    """Get current pregnancy week for a patient from database"""
    try:
        # Find patient by patient_id
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            print(f"Patient {patient_id} not found, using default week 1")
            return 1
        
        # Try to get pregnancy week from various sources
        pregnancy_week = 1  # Default
        
        # Try direct pregnancy_week field
        if 'pregnancy_week' in patient:
            pregnancy_week = patient['pregnancy_week']
        # Try health_data.pregnancy_week
        elif 'health_data' in patient and 'pregnancy_week' in patient.get('health_data', {}):
            pregnancy_week = patient['health_data']['pregnancy_week']
        # Try health_data.pregnancy_info.current_week
        elif 'health_data' in patient:
            pregnancy_info = patient.get('health_data', {}).get('pregnancy_info', {})
            if 'current_week' in pregnancy_info:
                pregnancy_week = pregnancy_info['current_week']
        # Try current_pregnancy_week
        elif 'current_pregnancy_week' in patient:
            pregnancy_week = patient['current_pregnancy_week']
        
        print(f"[Trimester Module] Patient {patient_id} is at week {pregnancy_week}")
        return int(pregnancy_week)
        
    except Exception as e:
        print(f"Error getting patient week: {e}")
        return 1


def _get_patient_id_from_token() -> Optional[str]:
    """Extract patient_id from JWT token in request"""
    try:
        if hasattr(request, 'user_data') and request.user_data:
            return request.user_data.get('patient_id')
        return None
    except Exception as e:
        print(f"Error extracting patient_id from token: {e}")
        return None


# Health check endpoint
@trimester_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Trimester API is running"})


# Root endpoint with API information
@trimester_bp.route('/', methods=['GET'])
def root():
    """Root endpoint with API information"""
    return jsonify({
        "message": "Pregnancy Week Development API",
        "version": "1.0.0",
        "endpoints": {
            "get_week": "/trimester/week/{week}",
            "get_enhanced_week": "/trimester/week/{week}/enhanced",
            "get_all_weeks": "/trimester/weeks",
            "get_trimester": "/trimester/trimester/{trimester}",
            "semantic_search": "/trimester/search?query={query}",
            "health": "/trimester/health"
        },
        "features": {
            "qdrant_enabled": pregnancy_service.use_qdrant,
            "semantic_search_available": pregnancy_service.use_qdrant,
            "rag_personalization_available": rag_service is not None,
            "dual_image_service_available": dual_image_service is not None,
            "service_status": dual_image_service.get_service_status() if dual_image_service else {}
        }
    })


# Get pregnancy week information
@trimester_bp.route('/week/<int:week>', methods=['GET'])
def get_pregnancy_week(week: int):
    """Get pregnancy week information including key developments and real fruit images"""
    try:
        if week < 1 or week > 40:
            return jsonify({
                "error": "Week must be between 1 and 40",
                "success": False
            }), 400
        
        # Get query parameters
        use_openai = request.args.get('use_openai', 'false').lower() == 'true'
        include_fruit_image = request.args.get('include_fruit_image', 'true').lower() == 'true'
        
        week_data = pregnancy_service.get_week_data(week)
        
        # Use OpenAI for baby size if requested and available
        if use_openai and openai_service:
            try:
                ai_baby_size = _run_async(openai_service.get_baby_size_for_week(week))
                week_data.baby_size = ai_baby_size
            except Exception as e:
                print(f"OpenAI baby size generation failed: {e}")
        
        # Add real fruit image if requested
        fruit_image_data = None
        if include_fruit_image and image_generator:
            try:
                fruit_image_data = image_generator.generate_real_fruit_only_image(week)
            except Exception as e:
                print(f"Real fruit image generation failed: {e}")
        
        # Create enhanced response
        response_data = {
            "success": True,
            "data": _serialize_pydantic(week_data),
            "message": f"Successfully retrieved data for week {week}",
            "fruit_image": fruit_image_data,
            "fruit_image_available": fruit_image_data is not None
        }
        
        return jsonify(response_data)
    
    except ValueError as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 404
    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "success": False
        }), 500


# Get enhanced week data
@trimester_bp.route('/week/<int:week>/enhanced', methods=['GET'])
def get_enhanced_week_data(week: int):
    """Get enhanced pregnancy week data using both RAG and OpenAI with multiple image options"""
    try:
        if week < 1 or week > 40:
            return jsonify({
                "error": "Week must be between 1 and 40",
                "success": False
            }), 400
        
        # Get query parameters
        patient_id = request.args.get('patient_id')
        use_mock_data = request.args.get('use_mock_data', 'true').lower() == 'true'
        include_rag_analysis = request.args.get('include_rag_analysis', 'true').lower() == 'true'
        image_method = request.args.get('image_method', 'all')
        
        # Get enhanced data using dual service
        if not dual_image_service:
            return jsonify({
                "error": "Dual Image Service not available. Please check service initialization.",
                "success": False
            }), 503
        
        enhanced_data = _run_async(dual_image_service.get_enhanced_week_data_with_image(
            week=week,
            patient_id=patient_id,
            use_mock_data=use_mock_data,
            include_rag_analysis=include_rag_analysis
        ))
        
        # Add service status
        enhanced_data["service_status"] = dual_image_service.get_service_status()
        
        # Filter images based on requested method
        if image_method != "all" and "images" in enhanced_data:
            filtered_images = {}
            if image_method in enhanced_data["images"]:
                filtered_images[image_method] = enhanced_data["images"][image_method]
            enhanced_data["images"] = filtered_images
            enhanced_data["image_method_used"] = image_method
        
        enhanced_data["message"] = f"Enhanced week {week} data with RAG + OpenAI analysis"
        
        return jsonify(enhanced_data)
    
    except ValueError as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 404
    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "success": False
        }), 500


# Get all pregnancy weeks
@trimester_bp.route('/weeks', methods=['GET'])
def get_all_pregnancy_weeks():
    """Get all available pregnancy week data"""
    try:
        all_weeks = pregnancy_service.get_all_weeks()
        return jsonify({
            "success": True,
            "data": {str(k): _serialize_pydantic(v) for k, v in all_weeks.items()},
            "message": f"Successfully retrieved data for {len(all_weeks)} weeks"
        })
    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "success": False
        }), 500


# Get week developments
@trimester_bp.route('/week/<int:week>/developments', methods=['GET'])
def get_week_developments(week: int):
    """Get only the key developments for a specific week"""
    try:
        if week < 1 or week > 40:
            return jsonify({
                "error": "Week must be between 1 and 40",
                "success": False
            }), 400
        
        week_data = pregnancy_service.get_week_data(week)
        
        return jsonify({
            "success": True,
            "week": week,
            "developments": [_serialize_pydantic(dev) for dev in week_data.key_developments],
            "message": f"Successfully retrieved developments for week {week}"
        })
    
    except ValueError as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 404
    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "success": False
        }), 500


# Get trimester weeks
@trimester_bp.route('/trimester/<int:trimester>', methods=['GET'])
def get_trimester_weeks(trimester: int):
    """Get all weeks for a specific trimester using Qdrant filtering with real fruit images"""
    try:
        if trimester not in [1, 2, 3]:
            return jsonify({
                "error": "Trimester must be 1, 2, or 3",
                "success": False
            }), 400
        
        include_fruit_images = request.args.get('include_fruit_images', 'true').lower() == 'true'
        
        # Get trimester weeks
        trimester_weeks = pregnancy_service.get_weeks_by_trimester(trimester)
        
        # Add fruit images to each week if requested
        enhanced_weeks = []
        for week_data in trimester_weeks:
            week_dict = _serialize_pydantic(week_data)
            
            if include_fruit_images and image_generator:
                try:
                    # Generate real fruit image for this week
                    fruit_image = image_generator.generate_real_fruit_only_image(week_data.week)
                    week_dict['fruit_image'] = fruit_image
                    week_dict['fruit_image_available'] = True
                except Exception as e:
                    print(f"Fruit image generation failed for week {week_data.week}: {e}")
                    week_dict['fruit_image'] = None
                    week_dict['fruit_image_available'] = False
            else:
                week_dict['fruit_image'] = None
                week_dict['fruit_image_available'] = False
            
            enhanced_weeks.append(week_dict)
        
        return jsonify({
            "success": True,
            "trimester": trimester,
            "weeks": enhanced_weeks,
            "total_weeks": len(enhanced_weeks),
            "fruit_images_included": include_fruit_images,
            "message": f"Successfully retrieved {len(enhanced_weeks)} weeks for trimester {trimester} with fruit images"
        })
    
    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "success": False
        }), 500


# Get baby size with OpenAI
@trimester_bp.route('/week/<int:week>/baby-size', methods=['GET'])
def get_baby_size_openai(week: int):
    """Get AI-powered baby size information for a specific week"""
    try:
        if week < 1 or week > 40:
            return jsonify({
                "error": "Week must be between 1 and 40",
                "success": False
            }), 400
        
        if not openai_service:
            return jsonify({
                "error": "OpenAI service not available. Please check your API key configuration.",
                "success": False
            }), 503
        
        # Get basic baby size
        baby_size = _run_async(openai_service.get_baby_size_for_week(week))
        
        # Get detailed information
        detailed_info = _run_async(openai_service.get_detailed_baby_info(week))
        
        return jsonify({
            "success": True,
            "week": week,
            "baby_size": _serialize_pydantic(baby_size),
            "detailed_info": _serialize_pydantic(detailed_info),
            "message": f"Successfully generated AI-powered baby size for week {week}"
        })
    
    except ValueError as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 404
    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "success": False
        }), 500


# Get OpenAI status
@trimester_bp.route('/openai/status', methods=['GET'])
def get_openai_status():
    """Check if OpenAI service is available and configured"""
    return jsonify({
        "success": True,
        "openai_available": openai_service is not None,
        "model": settings.OPENAI_MODEL if openai_service else None,
        "api_key_configured": bool(settings.OPENAI_API_KEY),
        "message": "OpenAI service status retrieved successfully"
    })


# Get baby size image
@trimester_bp.route('/week/<int:week>/baby-image', methods=['GET'])
def get_baby_size_image_stream(week: int):
    """Get baby size comparison image - single fruit style generated by OpenAI DALL-E"""
    try:
        if week < 1 or week > 40:
            return jsonify({
                "error": "Week must be between 1 and 40",
                "success": False
            }), 400
        
        format_type = request.args.get('format', 'stream')
        regenerate = request.args.get('regenerate', 'false').lower() == 'true'
        
        if not image_generator:
            return jsonify({
                "error": "Image generator not available",
                "success": False
            }), 503
        
        # Get cached or generate new OpenAI image
        image_data = _run_async(image_generator.get_or_generate_openai_image(week, regenerate))
        
        # Return format based on query parameter
        if format_type == "base64":
            # Return JSON with base64 data
            return jsonify({
                "success": True,
                "week": week,
                "image_data": image_data,
                "format": "base64",
                "regenerated": regenerate,
                "message": f"Successfully generated OpenAI baby size image for week {week}"
            })
        else:
            # Return raw image stream (default for <img> tags)
            # Extract base64 data (remove "data:image/png;base64," prefix if present)
            base64_data = image_data.split(',')[1] if ',' in image_data else image_data
            image_bytes = base64.b64decode(base64_data)
            
            return Response(
                image_bytes,
                mimetype="image/png",
                headers={
                    "Content-Disposition": f"inline; filename=baby_week_{week}_openai.png"
                }
            )
    
    except Exception as e:
        return jsonify({
            "error": f"Error generating image: {str(e)}",
            "success": False
        }), 500


# Get symptoms information
@trimester_bp.route('/week/<int:week>/symptoms', methods=['GET'])
def get_early_symptoms(week: int):
    """Get AI-powered early symptoms information for a specific week"""
    try:
        if week < 1 or week > 40:
            return jsonify({
                "error": "Week must be between 1 and 40",
                "success": False
            }), 400
        
        if not openai_service:
            return jsonify({
                "error": "OpenAI service not available. Please check your API key configuration.",
                "success": False
            }), 503
        
        # Get week data for trimester info
        week_data = pregnancy_service.get_week_data(week)
        
        # Get AI-powered symptoms
        symptoms_info = _run_async(openai_service.get_early_symptoms(week))
        
        return jsonify(_serialize_pydantic(QuickActionResponse(
            success=True,
            week=week,
            trimester=week_data.trimester,
            action_type="early_symptoms",
            data=_serialize_pydantic(symptoms_info),
            message=f"Successfully generated early symptoms information for week {week}"
        )))
    
    except ValueError as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 404
    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "success": False
        }), 500


# Get screening information
@trimester_bp.route('/week/<int:week>/screening', methods=['GET'])
def get_prenatal_screening(week: int):
    """Get AI-powered prenatal screening information for a specific week"""
    try:
        if week < 1 or week > 40:
            return jsonify({
                "error": "Week must be between 1 and 40",
                "success": False
            }), 400
        
        if not openai_service:
            return jsonify({
                "error": "OpenAI service not available. Please check your API key configuration.",
                "success": False
            }), 503
        
        # Get week data for trimester info
        week_data = pregnancy_service.get_week_data(week)
        
        # Get AI-powered screening
        screening_info = _run_async(openai_service.get_prenatal_screening(week))
        
        return jsonify(_serialize_pydantic(QuickActionResponse(
            success=True,
            week=week,
            trimester=week_data.trimester,
            action_type="prenatal_screening",
            data=_serialize_pydantic(screening_info),
            message=f"Successfully generated prenatal screening information for week {week}"
        )))
    
    except ValueError as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 404
    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "success": False
        }), 500


# Get wellness tips
@trimester_bp.route('/week/<int:week>/wellness', methods=['GET'])
def get_wellness_tips(week: int):
    """Get AI-powered wellness tips for a specific week"""
    try:
        if week < 1 or week > 40:
            return jsonify({
                "error": "Week must be between 1 and 40",
                "success": False
            }), 400
        
        if not openai_service:
            return jsonify({
                "error": "OpenAI service not available. Please check your API key configuration.",
                "success": False
            }), 503
        
        # Get week data for trimester info
        week_data = pregnancy_service.get_week_data(week)
        
        # Get AI-powered wellness tips
        wellness_info = _run_async(openai_service.get_wellness_tips(week))
        
        return jsonify(_serialize_pydantic(QuickActionResponse(
            success=True,
            week=week,
            trimester=week_data.trimester,
            action_type="wellness_tips",
            data=_serialize_pydantic(wellness_info),
            message=f"Successfully generated wellness tips for week {week}"
        )))
    
    except ValueError as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 404
    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "success": False
        }), 500


# Get nutrition tips
@trimester_bp.route('/week/<int:week>/nutrition', methods=['GET'])
def get_nutrition_tips(week: int):
    """Get AI-powered nutrition tips for a specific week"""
    try:
        if week < 1 or week > 40:
            return jsonify({
                "error": "Week must be between 1 and 40",
                "success": False
            }), 400
        
        if not openai_service:
            return jsonify({
                "error": "OpenAI service not available. Please check your API key configuration.",
                "success": False
            }), 503
        
        # Get week data for trimester info
        week_data = pregnancy_service.get_week_data(week)
        
        # Get AI-powered nutrition tips
        nutrition_info = _run_async(openai_service.get_nutrition_tips(week))
        
        return jsonify(_serialize_pydantic(QuickActionResponse(
            success=True,
            week=week,
            trimester=week_data.trimester,
            action_type="nutrition_tips",
            data=_serialize_pydantic(nutrition_info),
            message=f"Successfully generated nutrition tips for week {week}"
        )))
    
    except ValueError as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 404
    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "success": False
        }), 500


# Semantic search
@trimester_bp.route('/search', methods=['GET'])
def semantic_search():
    """Perform semantic search on pregnancy data using Qdrant"""
    try:
        query = request.args.get('query', '')
        limit = int(request.args.get('limit', 5))
        
        if not query or len(query.strip()) < 3:
            return jsonify({
                "error": "Query must be at least 3 characters long",
                "success": False
            }), 400
        
        # Perform semantic search
        results = pregnancy_service.semantic_search(query, limit=limit)
        
        return jsonify({
            "success": True,
            "query": query,
            "results": results,
            "total_results": len(results),
            "message": f"Found {len(results)} results for query: {query}"
        })
    
    except ValueError as e:
        # Qdrant not available
        return jsonify({
            "error": str(e),
            "success": False
        }), 503
    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "success": False
        }), 500


# RAG personalized developments
@trimester_bp.route('/patient/<int:week>/rag', methods=['GET'])
def get_personalized_rag_developments(week: int):
    """RAG-powered personalized pregnancy developments based on patient's disease history"""
    try:
        if week < 1 or week > 40:
            return jsonify({
                "error": "Week must be between 1 and 40",
                "success": False
            }), 400
        
        patient_id = request.args.get('patient_id')
        use_ai = request.args.get('use_ai', 'true').lower() == 'true'
        use_mock_data = request.args.get('use_mock_data', 'true').lower() == 'true'
        
        if not patient_id:
            return jsonify({
                "error": "patient_id is required",
                "success": False
            }), 400
        
        if not rag_service:
            return jsonify({
                "error": "RAG service not available. Qdrant must be configured.",
                "success": False
            }), 503
        
        # RAG Pipeline
        rag_response = _run_async(rag_service.get_personalized_developments(
            week=week,
            patient_id=patient_id,
            use_openai=use_ai,
            use_mock_data=use_mock_data
        ))
        
        return jsonify(_serialize_pydantic(rag_response))
    
    except ValueError as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 404
    except Exception as e:
        return jsonify({
            "error": f"RAG processing error: {str(e)}",
            "success": False
        }), 500


# Trimester fruit recommendations
@trimester_bp.route('/trimester/<int:trimester>/fruit-recommendations', methods=['GET'])
def get_trimester_fruit_recommendations(trimester: int):
    """Get RAG-based fruit size recommendations for a specific trimester"""
    
    if not pregnancy_service.use_qdrant or not rag_service:
        return jsonify({
            "error": "RAG service not available. Qdrant integration required.",
            "success": False
        }), 503
    
    try:
        if trimester < 1 or trimester > 3:
            return jsonify({
                "error": "Trimester must be 1, 2, or 3",
                "success": False
            }), 400
        
        patient_id = request.args.get('patient_id')
        use_mock_data = request.args.get('use_mock_data', 'true').lower() == 'true'
        
        # Get trimester fruit recommendations using RAG
        recommendations = _run_async(rag_service.get_trimester_fruit_recommendations(
            trimester=trimester,
            patient_id=patient_id,
            use_mock_data=use_mock_data
        ))
        
        return jsonify(recommendations)
        
    except Exception as e:
        return jsonify({
            "error": f"Error generating trimester fruit recommendations: {str(e)}",
            "success": False
        }), 500


# =============================================================================
# DYNAMIC ENDPOINTS - Based on Logged-in Patient's Pregnancy Week
# =============================================================================

@trimester_bp.route('/my-week', methods=['GET'])
@token_required
def get_my_current_week():
    """Get current pregnancy week for logged-in patient"""
    try:
        patient_id = _get_patient_id_from_token()
        if not patient_id:
            return jsonify({
                "error": "Patient ID not found in token",
                "success": False
            }), 401
        
        current_week = _get_patient_current_week(patient_id)
        
        return jsonify({
            "success": True,
            "patient_id": patient_id,
            "current_week": current_week,
            "message": f"Patient is at week {current_week}"
        })
    
    except Exception as e:
        return jsonify({
            "error": f"Error getting current week: {str(e)}",
            "success": False
        }), 500


@trimester_bp.route('/my-data', methods=['GET'])
@token_required
def get_my_week_data():
    """Get pregnancy data for logged-in patient's current week"""
    try:
        patient_id = _get_patient_id_from_token()
        if not patient_id:
            return jsonify({
                "error": "Patient ID not found in token",
                "success": False
            }), 401
        
        # Get patient's current week
        current_week = _get_patient_current_week(patient_id)
        
        # Get query parameters
        use_openai = request.args.get('use_openai', 'false').lower() == 'true'
        include_fruit_image = request.args.get('include_fruit_image', 'true').lower() == 'true'
        
        week_data = pregnancy_service.get_week_data(current_week)
        
        # Use OpenAI for baby size if requested and available
        if use_openai and openai_service:
            try:
                ai_baby_size = _run_async(openai_service.get_baby_size_for_week(current_week))
                week_data.baby_size = ai_baby_size
            except Exception as e:
                print(f"OpenAI baby size generation failed: {e}")
        
        # Add real fruit image if requested
        fruit_image_data = None
        if include_fruit_image and image_generator:
            try:
                fruit_image_data = image_generator.generate_real_fruit_only_image(current_week)
            except Exception as e:
                print(f"Real fruit image generation failed: {e}")
        
        # Create enhanced response
        response_data = {
            "success": True,
            "patient_id": patient_id,
            "current_week": current_week,
            "data": _serialize_pydantic(week_data),
            "message": f"Successfully retrieved data for your current week {current_week}",
            "fruit_image": fruit_image_data,
            "fruit_image_available": fruit_image_data is not None
        }
        
        return jsonify(response_data)
    
    except ValueError as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 404
    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "success": False
        }), 500


@trimester_bp.route('/my-baby-image', methods=['GET'])
@token_required
def get_my_baby_image():
    """Get baby size image for logged-in patient's current week"""
    try:
        patient_id = _get_patient_id_from_token()
        if not patient_id:
            return jsonify({
                "error": "Patient ID not found in token",
                "success": False
            }), 401
        
        # Get patient's current week
        current_week = _get_patient_current_week(patient_id)
        
        format_type = request.args.get('format', 'stream')
        regenerate = request.args.get('regenerate', 'false').lower() == 'true'
        
        if not image_generator:
            return jsonify({
                "error": "Image generator not available",
                "success": False
            }), 503
        
        # Get cached or generate new OpenAI image
        image_data = _run_async(image_generator.get_or_generate_openai_image(current_week, regenerate))
        
        # Return format based on query parameter
        if format_type == "base64":
            # Return JSON with base64 data
            return jsonify({
                "success": True,
                "patient_id": patient_id,
                "current_week": current_week,
                "image_data": image_data,
                "format": "base64",
                "regenerated": regenerate,
                "message": f"Successfully generated baby size image for your current week {current_week}"
            })
        else:
            # Return raw image stream (default for <img> tags)
            # Extract base64 data (remove "data:image/png;base64," prefix if present)
            base64_data = image_data.split(',')[1] if ',' in image_data else image_data
            image_bytes = base64.b64decode(base64_data)
            
            return Response(
                image_bytes,
                mimetype="image/png",
                headers={
                    "Content-Disposition": f"inline; filename=baby_week_{current_week}_patient_{patient_id}.png"
                }
            )
    
    except Exception as e:
        return jsonify({
            "error": f"Error generating image: {str(e)}",
            "success": False
        }), 500


@trimester_bp.route('/my-enhanced', methods=['GET'])
@token_required
def get_my_enhanced_data():
    """Get enhanced pregnancy data for logged-in patient's current week"""
    try:
        patient_id = _get_patient_id_from_token()
        if not patient_id:
            return jsonify({
                "error": "Patient ID not found in token",
                "success": False
            }), 401
        
        # Get patient's current week
        current_week = _get_patient_current_week(patient_id)
        
        # Get query parameters
        use_mock_data = request.args.get('use_mock_data', 'false').lower() == 'true'
        include_rag_analysis = request.args.get('include_rag_analysis', 'true').lower() == 'true'
        image_method = request.args.get('image_method', 'all')
        
        # Get enhanced data using dual service
        if not dual_image_service:
            return jsonify({
                "error": "Dual Image Service not available. Please check service initialization.",
                "success": False
            }), 503
        
        enhanced_data = _run_async(dual_image_service.get_enhanced_week_data_with_image(
            week=current_week,
            patient_id=patient_id,
            use_mock_data=use_mock_data,
            include_rag_analysis=include_rag_analysis
        ))
        
        # Add service status
        enhanced_data["service_status"] = dual_image_service.get_service_status()
        enhanced_data["current_week"] = current_week
        enhanced_data["patient_id"] = patient_id
        
        # Filter images based on requested method
        if image_method != "all" and "images" in enhanced_data:
            filtered_images = {}
            if image_method in enhanced_data["images"]:
                filtered_images[image_method] = enhanced_data["images"][image_method]
            enhanced_data["images"] = filtered_images
            enhanced_data["image_method_used"] = image_method
        
        enhanced_data["message"] = f"Enhanced data for your current week {current_week} with RAG + OpenAI analysis"
        
        return jsonify(enhanced_data)
    
    except ValueError as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 404
    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "success": False
        }), 500


@trimester_bp.route('/my-rag', methods=['GET'])
@token_required
def get_my_rag_personalized():
    """Get RAG-powered personalized developments for logged-in patient's current week"""
    try:
        patient_id = _get_patient_id_from_token()
        if not patient_id:
            return jsonify({
                "error": "Patient ID not found in token",
                "success": False
            }), 401
        
        # Get patient's current week
        current_week = _get_patient_current_week(patient_id)
        
        use_ai = request.args.get('use_ai', 'true').lower() == 'true'
        use_mock_data = request.args.get('use_mock_data', 'false').lower() == 'true'
        
        if not rag_service:
            return jsonify({
                "error": "RAG service not available. Qdrant must be configured.",
                "success": False
            }), 503
        
        # RAG Pipeline with patient's real data
        rag_response = _run_async(rag_service.get_personalized_developments(
            week=current_week,
            patient_id=patient_id,
            use_openai=use_ai,
            use_mock_data=use_mock_data
        ))
        
        return jsonify(_serialize_pydantic(rag_response))
    
    except ValueError as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 404
    except Exception as e:
        return jsonify({
            "error": f"RAG processing error: {str(e)}",
            "success": False
        }), 500


@trimester_bp.route('/my-symptoms', methods=['GET'])
@token_required
def get_my_symptoms():
    """Get AI-powered symptoms for logged-in patient's current week"""
    try:
        patient_id = _get_patient_id_from_token()
        if not patient_id:
            return jsonify({
                "error": "Patient ID not found in token",
                "success": False
            }), 401
        
        # Get patient's current week
        current_week = _get_patient_current_week(patient_id)
        
        if not openai_service:
            return jsonify({
                "error": "OpenAI service not available. Please check your API key configuration.",
                "success": False
            }), 503
        
        # Get week data for trimester info
        week_data = pregnancy_service.get_week_data(current_week)
        
        # Get AI-powered symptoms
        symptoms_info = _run_async(openai_service.get_early_symptoms(current_week))
        
        return jsonify(_serialize_pydantic(QuickActionResponse(
            success=True,
            week=current_week,
            trimester=week_data.trimester,
            action_type="early_symptoms",
            data=_serialize_pydantic(symptoms_info),
            message=f"Successfully generated symptoms for your current week {current_week}"
        )))
    
    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "success": False
        }), 500


@trimester_bp.route('/my-nutrition', methods=['GET'])
@token_required
def get_my_nutrition():
    """Get AI-powered nutrition tips for logged-in patient's current week"""
    try:
        patient_id = _get_patient_id_from_token()
        if not patient_id:
            return jsonify({
                "error": "Patient ID not found in token",
                "success": False
            }), 401
        
        # Get patient's current week
        current_week = _get_patient_current_week(patient_id)
        
        if not openai_service:
            return jsonify({
                "error": "OpenAI service not available. Please check your API key configuration.",
                "success": False
            }), 503
        
        # Get week data for trimester info
        week_data = pregnancy_service.get_week_data(current_week)
        
        # Get AI-powered nutrition tips
        nutrition_info = _run_async(openai_service.get_nutrition_tips(current_week))
        
        return jsonify(_serialize_pydantic(QuickActionResponse(
            success=True,
            week=current_week,
            trimester=week_data.trimester,
            action_type="nutrition_tips",
            data=_serialize_pydantic(nutrition_info),
            message=f"Successfully generated nutrition tips for your current week {current_week}"
        )))
    
    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "success": False
        }), 500


@trimester_bp.route('/my-wellness', methods=['GET'])
@token_required
def get_my_wellness():
    """Get AI-powered wellness tips for logged-in patient's current week"""
    try:
        patient_id = _get_patient_id_from_token()
        if not patient_id:
            return jsonify({
                "error": "Patient ID not found in token",
                "success": False
            }), 401
        
        # Get patient's current week
        current_week = _get_patient_current_week(patient_id)
        
        if not openai_service:
            return jsonify({
                "error": "OpenAI service not available. Please check your API key configuration.",
                "success": False
            }), 503
        
        # Get week data for trimester info
        week_data = pregnancy_service.get_week_data(current_week)
        
        # Get AI-powered wellness tips
        wellness_info = _run_async(openai_service.get_wellness_tips(current_week))
        
        return jsonify(_serialize_pydantic(QuickActionResponse(
            success=True,
            week=current_week,
            trimester=week_data.trimester,
            action_type="wellness_tips",
            data=_serialize_pydantic(wellness_info),
            message=f"Successfully generated wellness tips for your current week {current_week}"
        )))
    
    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "success": False
        }), 500
