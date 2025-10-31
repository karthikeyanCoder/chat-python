"""
Dual Image Service - Combines RAG and OpenAI for baby size images
Provides fallback mechanisms for robust image generation
"""

import sys
import os
import base64
from typing import Optional, Dict, Any
from io import BytesIO

# Import from app.shared.pregnancy_rag package
try:
    from app.shared.pregnancy_rag.baby_image_generator import BabySizeImageGenerator
    from app.shared.pregnancy_rag.openai_service import OpenAIBabySizeService
    from app.shared.pregnancy_rag.services.rag_service import RAGService
    from app.shared.pregnancy_rag.services.qdrant_service import QdrantService
    from app.shared.pregnancy_rag.pregnancy_models import PregnancyWeek
except ImportError as e:
    print(f"Import error in dual_image_service: {e}")
    BabySizeImageGenerator = None
    OpenAIBabySizeService = None
    RAGService = None
    QdrantService = None
    PregnancyWeek = None


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
        
        # Extract qdrant_service from pregnancy_service if available
        self.qdrant_service = None
        if pregnancy_service and hasattr(pregnancy_service, 'qdrant_service'):
            self.qdrant_service = pregnancy_service.qdrant_service
        
        # Try to initialize services if not provided
        if not self.image_generator:
            try:
                self.image_generator = BabySizeImageGenerator()
                print("✅ BabySizeImageGenerator initialized")
            except Exception as e:
                print(f"❌ BabySizeImageGenerator failed: {e}")
        
        if not self.openai_service:
            try:
                self.openai_service = OpenAIBabySizeService()
                print("✅ OpenAIBabySizeService initialized")
            except Exception as e:
                print(f"❌ OpenAIBabySizeService failed: {e}")
        
        print(f"✅ DualImageService initialized with services:")
        print(f"   - Image Generator: {self.image_generator is not None}")
        print(f"   - OpenAI Service: {self.openai_service is not None}")
        print(f"   - RAG Service: {self.rag_service is not None}")
        print(f"   - Pregnancy Service: {self.pregnancy_service is not None}")
    
    async def get_enhanced_week_data_with_image(
        self, 
        week: int, 
        patient_id: Optional[str] = None,
        use_mock_data: bool = True,
        include_rag_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        Get comprehensive week data with image using both RAG and OpenAI
        
        Args:
            week: Pregnancy week (1-40)
            patient_id: Optional patient ID for RAG personalization
            use_mock_data: Use mock patient data if real data unavailable
            include_rag_analysis: Include RAG-based analysis
            
        Returns:
            Enhanced week data with multiple image options and analysis
        """
        result = {
            "week": week,
            "success": True,
            "images": {},
            "analysis": {},
            "fallback_used": [],
            "errors": []
        }
        
        # Get base week data from Qdrant
        week_data = None
        if self.qdrant_service:
            try:
                week_data = self.qdrant_service.get_week_by_number(week)
                if week_data:
                    result["base_data"] = week_data.dict() if hasattr(week_data, 'dict') else week_data
            except Exception as e:
                result["errors"].append(f"Qdrant week data failed: {str(e)}")
        
        # Generate images using different methods
        image_methods = [
            ("rag_fruit_only", self._generate_rag_fruit_only_image),
            ("openai_enhanced", self._generate_openai_enhanced_image),
            ("traditional_chart", self._generate_traditional_chart),
            ("simple_visualization", self._generate_simple_visualization),
            ("infographic_style", self._generate_infographic_style_image),
            ("exact_reference_style", self._generate_exact_reference_style_image),
            ("single_fruit_style", self._generate_single_fruit_style_image)
        ]
        
        for method_name, method_func in image_methods:
            try:
                # Check if method is async or sync
                import asyncio
                if asyncio.iscoroutinefunction(method_func):
                    image_data = await method_func(week, week_data, patient_id, use_mock_data)
                else:
                    image_data = method_func(week, week_data, patient_id, use_mock_data)
                
                if image_data:
                    result["images"][method_name] = image_data
                    print(f"✅ Generated {method_name} image for week {week}")
                else:
                    result["fallback_used"].append(f"{method_name} returned None")
            except Exception as e:
                error_msg = f"{method_name} failed: {str(e)}"
                result["errors"].append(error_msg)
                result["fallback_used"].append(error_msg)
                print(f"❌ {error_msg}")
        
        # Add RAG analysis if requested
        if include_rag_analysis and self.rag_service and patient_id:
            try:
                rag_response = await self.rag_service.get_personalized_developments(
                    week=week,
                    patient_id=patient_id,
                    use_mock_data=use_mock_data
                )
                result["analysis"]["rag_personalized"] = rag_response
                print(f"✅ RAG analysis completed for week {week}")
            except Exception as e:
                result["errors"].append(f"RAG analysis failed: {str(e)}")
        
        # Add OpenAI analysis
        if self.openai_service:
            try:
                openai_baby_size = await self.openai_service.get_baby_size_for_week(week)
                result["analysis"]["openai_baby_size"] = openai_baby_size
                print(f"✅ OpenAI analysis completed for week {week}")
            except Exception as e:
                result["errors"].append(f"OpenAI analysis failed: {str(e)}")
        
        return result
    
    def _generate_rag_fruit_only_image(
        self, 
        week: int, 
        week_data: Optional[PregnancyWeek], 
        patient_id: Optional[str], 
        use_mock_data: bool
    ) -> Optional[str]:
        """Generate RAG-based fruit-only image"""
        if not self.image_generator:
            return None
        
        try:
            return self.image_generator.generate_real_fruit_only_image(week)
        except Exception as e:
            print(f"RAG fruit image generation failed: {e}")
            return None
    
    def _generate_openai_enhanced_image(
        self, 
        week: int, 
        week_data: Optional[PregnancyWeek], 
        patient_id: Optional[str], 
        use_mock_data: bool
    ) -> Optional[str]:
        """Generate OpenAI-enhanced baby size image"""
        if not self.image_generator:
            return None
        
        try:
            # Generate traditional chart for now (OpenAI integration can be enhanced later)
            return self.image_generator.generate_baby_size_image(week)
        except Exception as e:
            print(f"OpenAI enhanced image generation failed: {e}")
            return None
    
    def _generate_traditional_chart(
        self, 
        week: int, 
        week_data: Optional[PregnancyWeek], 
        patient_id: Optional[str], 
        use_mock_data: bool
    ) -> Optional[str]:
        """Generate traditional matplotlib chart"""
        if not self.image_generator:
            return None
        
        try:
            return self.image_generator.generate_baby_size_image(week)
        except Exception as e:
            print(f"Traditional chart generation failed: {e}")
            return None
    
    def _generate_simple_visualization(
        self, 
        week: int, 
        week_data: Optional[PregnancyWeek], 
        patient_id: Optional[str], 
        use_mock_data: bool
    ) -> Optional[str]:
        """Generate simple visualization as fallback"""
        if not self.image_generator:
            return None
        
        try:
            return self.image_generator.generate_simple_baby_image(week)
        except Exception as e:
            print(f"Simple visualization generation failed: {e}")
            return None
    
    def _generate_infographic_style_image(
        self, 
        week: int, 
        week_data: Optional[PregnancyWeek], 
        patient_id: Optional[str], 
        use_mock_data: bool
    ) -> Optional[str]:
        """Generate infographic-style baby size image"""
        if not self.image_generator:
            return None
        
        try:
            return self.image_generator.generate_infographic_style_image(week)
        except Exception as e:
            print(f"Infographic style generation failed: {e}")
            return None
    
    def _generate_exact_reference_style_image(
        self, 
        week: int, 
        week_data: Optional[PregnancyWeek], 
        patient_id: Optional[str], 
        use_mock_data: bool
    ) -> Optional[str]:
        """Generate exact reference style baby size image"""
        if not self.image_generator:
            return None
        
        try:
            return self.image_generator.generate_exact_reference_style_image(week)
        except Exception as e:
            print(f"Exact reference style generation failed: {e}")
            return None
    
    def _generate_single_fruit_style_image(
        self, 
        week: int, 
        week_data: Optional[PregnancyWeek], 
        patient_id: Optional[str], 
        use_mock_data: bool
    ) -> Optional[str]:
        """Generate single fruit style baby size image"""
        if not self.image_generator:
            return None
        
        try:
            return self.image_generator.generate_single_fruit_style_image(week)
        except Exception as e:
            print(f"Single fruit style generation failed: {e}")
            return None
    
    def get_service_status(self) -> Dict[str, bool]:
        """Get status of all services"""
        return {
            "rag_service": self.rag_service is not None,
            "openai_service": self.openai_service is not None,
            "image_generator": self.image_generator is not None,
            "qdrant_service": self.qdrant_service is not None,
            "pregnancy_service": self.pregnancy_service is not None
        }
