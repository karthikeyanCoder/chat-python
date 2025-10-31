"""
RAG Service for Trimester Module

This service implements the Retrieval-Augmented Generation pipeline
for personalized pregnancy information based on patient medical history.
"""

from typing import List, Dict, Optional, Any
import json
import re

from ..schemas import (
    PregnancyWeek, KeyDevelopment, PersonalizedKeyDevelopment, 
    PatientProfile, PatientDiseaseHistory, RAGPregnancyResponse
)
from .qdrant_service import QdrantService
from .patient_backend_service import PatientBackendService


class RAGService:
    """Service for RAG-based personalized pregnancy information"""
    
    def __init__(self, qdrant_service: QdrantService, patient_service: PatientBackendService):
        self.qdrant_service = qdrant_service
        self.patient_service = patient_service
    
    async def get_personalized_developments(
        self, 
        week: int, 
        patient_id: str,
        use_openai: bool = True,
        use_mock_data: bool = False
    ) -> RAGPregnancyResponse:
        """RAG pipeline for personalized pregnancy developments"""
        
        try:
            # STEP 1: RETRIEVAL - Get relevant pregnancy data
            week_data = self.qdrant_service.get_week_by_number(week)
            if not week_data:
                raise ValueError(f"Week {week} data not found")
            
            # Get related weeks for broader context
            related_weeks = self.qdrant_service.semantic_search(
                f"week {week} pregnancy developments symptoms", 
                limit=3
            )
            
            # STEP 2: RETRIEVAL - Get patient medical history
            try:
                if use_mock_data:
                    patient_profile = self.patient_service.get_mock_patient_profile(patient_id)
                else:
                    patient_profile = await self.patient_service.get_patient_profile(patient_id)
            except Exception as e:
                print(f"Backend not available, using mock data: {e}")
                patient_profile = self.patient_service.get_mock_patient_profile(patient_id)
            
            # STEP 3: GENERATION - Create personalized developments
            personalized_developments = []
            medical_advisories = []
            special_monitoring = []
            
            # Process each key development
            for development_data in week_data.get("key_developments", []):
                personalized_dev = self._personalize_development(
                    development_data, 
                    patient_profile, 
                    week
                )
                personalized_developments.append(personalized_dev)
                
                # Collect medical advisories and monitoring recommendations
                if personalized_dev.medical_consideration:
                    medical_advisories.append(personalized_dev.medical_consideration)
                
                special_monitoring.extend(personalized_dev.monitoring_recommendations)
            
            # Remove duplicates
            medical_advisories = list(set(medical_advisories))
            special_monitoring = list(set(special_monitoring))
            
            # STEP 4: Create RAG context
            rag_context = self._create_rag_context(week_data, patient_profile, related_weeks)
            
            # STEP 5: Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                week_data, patient_profile, related_weeks
            )
            
            return RAGPregnancyResponse(
                patient_id=patient_id,
                week=week,
                trimester=week_data.get("trimester", 1),
                personalized_developments=personalized_developments,
                medical_advisories=medical_advisories,
                special_monitoring=special_monitoring,
                rag_context=rag_context,
                confidence_score=confidence_score,
                message=f"Personalized pregnancy information for week {week}"
            )
            
        except Exception as e:
            print(f"RAG processing error: {e}")
            raise
    
    def _personalize_development(
        self, 
        development_data: Dict, 
        patient_profile: PatientProfile, 
        week: int
    ) -> PersonalizedKeyDevelopment:
        """Personalize a key development based on patient's medical history"""
        
        # Create KeyDevelopment object from data
        development = KeyDevelopment(
            title=development_data.get("title", ""),
            description=development_data.get("description", ""),
            icon=development_data.get("icon", ""),
            category=development_data.get("category", "")
        )
        
        # Start with original description
        personalized_note = development.description
        medical_consideration = ""
        risk_level = "low"
        monitoring_recommendations = []
        
        # Analyze patient's disease history
        for disease in patient_profile.disease_history:
            if disease.current_status == "active" or disease.current_status == "remission":
                
                # Diabetes considerations
                if "diabetes" in disease.disease_name.lower():
                    personalized_note += f" Given your diabetes history, blood sugar control is crucial during this development phase."
                    medical_consideration = "Diabetes can affect fetal growth and development"
                    risk_level = "medium"
                    monitoring_recommendations.extend([
                        "Daily blood glucose monitoring",
                        "Nutritionist consultation",
                        "Endocrinologist review"
                    ])
                
                # Hypertension considerations
                if "hypertension" in disease.disease_name.lower():
                    personalized_note += f" Due to your blood pressure history, cardiovascular monitoring is important."
                    medical_consideration = "Hypertension increases risk of preeclampsia and other complications"
                    risk_level = "medium"
                    monitoring_recommendations.extend([
                        "Daily blood pressure monitoring",
                        "Preeclampsia screening",
                        "Cardiologist consultation"
                    ])
                
                # Cancer considerations
                if "cancer" in disease.disease_name.lower():
                    personalized_note += f" Your previous cancer treatment history requires special monitoring during pregnancy."
                    medical_consideration = "Previous cancer treatment may affect fetal development and pregnancy risks"
                    risk_level = "high"
                    monitoring_recommendations.extend([
                        "Oncologist consultation",
                        "Specialized blood work",
                        "High-risk pregnancy monitoring"
                    ])
                
                # General medication considerations
                if disease.treatment:
                    personalized_note += f" Current medications ({', '.join(disease.treatment)}) may need review during pregnancy."
                    medical_consideration = "Medication safety during pregnancy needs evaluation"
                    monitoring_recommendations.append("Medication review with healthcare provider")
        
        # Age considerations
        if patient_profile.age > 35:
            personalized_note += " Given your age, additional screening may be recommended."
            medical_consideration = "Advanced maternal age increases certain pregnancy risks"
            if risk_level == "low":
                risk_level = "medium"
            monitoring_recommendations.extend([
                "Genetic counseling",
                "Additional ultrasound monitoring"
            ])
        
        # Previous pregnancy considerations
        if patient_profile.previous_pregnancies > 0:
            personalized_note += " Your previous pregnancy experience may provide insights for this pregnancy."
            monitoring_recommendations.append("Review previous pregnancy records")
        
        return PersonalizedKeyDevelopment(
            original_development=development,
            personalized_note=personalized_note,
            medical_consideration=medical_consideration,
            risk_level=risk_level,
            monitoring_recommendations=list(set(monitoring_recommendations))
        )
    
    def _create_rag_context(
        self, 
        week_data: Dict, 
        patient_profile: PatientProfile, 
        related_weeks: List[Dict]
    ) -> str:
        """Create RAG context for the personalized response"""
        
        context_parts = [
            f"Pregnancy Week {week_data.get('week', 'unknown')} Information:",
            f"Baby Size: {week_data.get('baby_size', {}).get('size', 'unknown')}",
            f"Key Developments: {len(week_data.get('key_developments', []))} developments identified"
        ]
        
        # Add patient context
        context_parts.extend([
            f"Patient Profile: Age {patient_profile.age}, Blood Type {patient_profile.blood_type}",
            f"Medical History: {len(patient_profile.disease_history)} conditions documented"
        ])
        
        # Add disease history context
        for disease in patient_profile.disease_history:
            if disease.current_status != "healthy":
                context_parts.append(
                    f"- {disease.disease_name}: {disease.severity} severity, "
                    f"{disease.current_status} status"
                )
        
        # Add related weeks context
        if related_weeks:
            context_parts.append(f"Related Weeks Context: {len(related_weeks)} similar weeks analyzed")
        
        return " | ".join(context_parts)
    
    def _calculate_confidence_score(
        self, 
        week_data: Dict, 
        patient_profile: PatientProfile, 
        related_weeks: List[Dict]
    ) -> float:
        """Calculate confidence score for the RAG response"""
        
        base_score = 0.7  # Base confidence
        
        # Boost confidence based on data availability
        if week_data and week_data.get("key_developments"):
            base_score += 0.1
        
        if patient_profile and patient_profile.disease_history:
            base_score += 0.1
        
        if related_weeks and len(related_weeks) > 1:
            base_score += 0.1
        
        # Cap at 1.0
        return min(base_score, 1.0)
    
    async def get_trimester_fruit_recommendations(
        self,
        trimester: int,
        patient_id: str,
        use_mock_data: bool = True
    ) -> Dict[str, Any]:
        """Get RAG-based fruit size recommendations for a specific trimester"""
        
        try:
            # Get trimester weeks
            trimester_weeks = self.qdrant_service.get_weeks_by_trimester(trimester)
            
            if not trimester_weeks:
                raise ValueError(f"No data found for trimester {trimester}")
            
            # Get patient profile
            try:
                if use_mock_data:
                    patient_profile = self.patient_service.get_mock_patient_profile(patient_id)
                else:
                    patient_profile = await self.patient_service.get_patient_profile(patient_id)
            except Exception as e:
                print(f"Using mock data for fruit recommendations: {e}")
                patient_profile = self.patient_service.get_mock_patient_profile(patient_id)
            
            # Generate fruit recommendations
            fruit_recommendations = []
            
            for week_data in trimester_weeks:
                week_num = week_data.get("week", 0)
                baby_size = week_data.get("baby_size", {})
                
                # Create personalized fruit recommendation
                recommendation = {
                    "week": week_num,
                    "fruit_name": baby_size.get("size", "Unknown"),
                    "weight": baby_size.get("weight", "Unknown"),
                    "length": baby_size.get("length", "Unknown"),
                    "personalized_note": f"Baby size comparison for week {week_num}",
                    "medical_consideration": ""
                }
                
                # Add medical considerations based on patient history
                for disease in patient_profile.disease_history:
                    if "diabetes" in disease.disease_name.lower():
                        recommendation["medical_consideration"] = "Monitor blood sugar levels as baby grows"
                    elif "hypertension" in disease.disease_name.lower():
                        recommendation["medical_consideration"] = "Blood pressure monitoring important during growth spurts"
                
                fruit_recommendations.append(recommendation)
            
            return {
                "success": True,
                "trimester": trimester,
                "patient_id": patient_id,
                "fruit_recommendations": fruit_recommendations,
                "total_weeks": len(fruit_recommendations),
                "message": f"Generated {len(fruit_recommendations)} fruit recommendations for trimester {trimester}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "trimester": trimester,
                "patient_id": patient_id,
                "fruit_recommendations": [],
                "error": str(e),
                "message": f"Failed to generate trimester fruit recommendations: {str(e)}"
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health of the RAG service"""
        return {
            "status": "healthy",
            "qdrant_available": self.qdrant_service is not None,
            "patient_service_available": self.patient_service is not None,
            "service_type": "rag_service"
        }
