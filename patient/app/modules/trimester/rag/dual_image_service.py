"""
Dual Image Service for Trimester Module

This service combines RAG and OpenAI for baby size images
with intelligent fallback mechanisms.
"""

import base64
from typing import Optional, Dict, Any
from io import BytesIO

from ..services import PregnancyDataService, OpenAIBabySizeService
from ..schemas import PregnancyWeek


class DualImageService:
    """
    Service that combines RAG and OpenAI for generating baby size images
    with intelligent fallback mechanisms
    """
    
    def __init__(self, pregnancy_service=None, rag_service=None, openai_service=None, image_generator=None):
        """
        Initialize DualImageService with existing services
        
        Args:
            pregnancy_service: Existing PregnancyDataService instance
            rag_service: Existing RAGService instance  
            openai_service: Existing OpenAIBabySizeService instance
            image_generator: Existing BabySizeImageGenerator instance
        """
        self.pregnancy_service = pregnancy_service
        self.rag_service = rag_service
        self.openai_service = openai_service
        self.image_generator = image_generator
        
        # Initialize fallback image generator if none provided
        if not self.image_generator:
            try:
                from ..image_generator import BabySizeImageGenerator
                self.image_generator = BabySizeImageGenerator(openai_service)
            except Exception as e:
                print(f"Failed to initialize image generator: {e}")
                self.image_generator = None
    
    async def get_enhanced_week_data_with_image(
        self,
        week: int,
        patient_id: str = None,
        use_mock_data: bool = True,
        include_rag_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        Get enhanced week data with multiple image generation methods
        
        Args:
            week: Pregnancy week (1-40)
            patient_id: Optional patient ID for RAG personalization
            use_mock_data: Whether to use mock patient data
            include_rag_analysis: Whether to include RAG-based analysis
        
        Returns:
            Enhanced week data with multiple image options
        """
        try:
            # Get base week data
            week_data = self.pregnancy_service.get_week_data(week)
            
            # Initialize response structure
            enhanced_data = {
                "success": True,
                "week": week,
                "trimester": week_data.trimester,
                "base_data": week_data.dict() if hasattr(week_data, 'dict') else week_data,
                "images": {},
                "rag_analysis": {},
                "personalized_info": {}
            }
            
            # Generate images using different methods
            enhanced_data["images"] = await self._generate_all_image_types(week)
            
            # Add RAG analysis if requested
            if include_rag_analysis and self.rag_service and patient_id:
                try:
                    rag_response = await self.rag_service.get_personalized_developments(
                        week=week,
                        patient_id=patient_id,
                        use_mock_data=use_mock_data
                    )
                    enhanced_data["rag_analysis"] = rag_response.dict() if hasattr(rag_response, 'dict') else rag_response
                except Exception as e:
                    print(f"RAG analysis failed: {e}")
                    enhanced_data["rag_analysis"] = {"error": str(e)}
            
            # Add personalized information
            enhanced_data["personalized_info"] = {
                "patient_id": patient_id,
                "use_mock_data": use_mock_data,
                "rag_available": self.rag_service is not None,
                "openai_available": self.openai_service is not None,
                "image_generator_available": self.image_generator is not None
            }
            
            return enhanced_data
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "week": week,
                "message": f"Failed to get enhanced week data: {str(e)}"
            }
    
    async def _generate_all_image_types(self, week: int) -> Dict[str, Any]:
        """Generate all types of images for a given week"""
        images = {}
        
        # 1. RAG-based real fruit image
        try:
            if self.image_generator:
                rag_image = self.image_generator.generate_real_fruit_only_image(week)
                images["rag"] = {
                    "type": "real_fruit",
                    "data": rag_image,
                    "source": "RAG + Real Fruit Images",
                    "available": True
                }
        except Exception as e:
            images["rag"] = {
                "type": "real_fruit",
                "error": str(e),
                "source": "RAG + Real Fruit Images",
                "available": False
            }
        
        # 2. OpenAI-generated image
        try:
            if self.image_generator and self.openai_service:
                openai_image = await self.image_generator.get_or_generate_openai_image(week)
                images["openai"] = {
                    "type": "ai_generated",
                    "data": openai_image,
                    "source": "OpenAI DALL-E",
                    "available": True
                }
        except Exception as e:
            images["openai"] = {
                "type": "ai_generated",
                "error": str(e),
                "source": "OpenAI DALL-E",
                "available": False
            }
        
        # 3. Traditional matplotlib image
        try:
            if self.image_generator:
                traditional_image = self.image_generator.generate_baby_size_image(week)
                images["traditional"] = {
                    "type": "matplotlib",
                    "data": traditional_image,
                    "source": "Matplotlib Visualization",
                    "available": True
                }
        except Exception as e:
            images["traditional"] = {
                "type": "matplotlib",
                "error": str(e),
                "source": "Matplotlib Visualization",
                "available": False
            }
        
        # 4. Simple text-based representation
        try:
            week_data = self.pregnancy_service.get_week_data(week)
            simple_repr = {
                "week": week,
                "baby_size": week_data.baby_size.size,
                "weight": week_data.baby_size.weight,
                "length": week_data.baby_size.length,
                "trimester": week_data.trimester
            }
            images["simple"] = {
                "type": "text_representation",
                "data": simple_repr,
                "source": "Text-based Size Info",
                "available": True
            }
        except Exception as e:
            images["simple"] = {
                "type": "text_representation",
                "error": str(e),
                "source": "Text-based Size Info",
                "available": False
            }
        
        return images
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get the status of all services"""
        return {
            "pregnancy_service": self.pregnancy_service is not None,
            "rag_service": self.rag_service is not None,
            "openai_service": self.openai_service is not None,
            "image_generator": self.image_generator is not None,
            "overall_status": "healthy" if all([
                self.pregnancy_service,
                self.image_generator
            ]) else "degraded",
            "features": {
                "rag_personalization": self.rag_service is not None,
                "openai_image_generation": self.openai_service is not None and self.image_generator is not None,
                "traditional_visualization": self.image_generator is not None,
                "real_fruit_images": self.image_generator is not None
            }
        }
    
    async def get_best_available_image(self, week: int, preference: str = "openai") -> Dict[str, Any]:
        """
        Get the best available image based on preference
        
        Args:
            week: Pregnancy week
            preference: Preferred image type ("openai", "rag", "traditional", "simple")
        
        Returns:
            Best available image data
        """
        images = await self._generate_all_image_types(week)
        
        # Try preferred method first
        if preference in images and images[preference].get("available"):
            return images[preference]
        
        # Fallback order: openai -> rag -> traditional -> simple
        fallback_order = ["openai", "rag", "traditional", "simple"]
        
        for method in fallback_order:
            if method in images and images[method].get("available"):
                return images[method]
        
        # If nothing is available, return error
        return {
            "type": "error",
            "error": "No image generation methods available",
            "available": False
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health of the dual image service"""
        return {
            "status": "healthy" if self.pregnancy_service and self.image_generator else "degraded",
            "services": self.get_service_status(),
            "service_type": "dual_image_service"
        }
