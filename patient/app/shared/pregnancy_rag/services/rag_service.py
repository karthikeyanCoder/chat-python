from typing import List, Dict, Optional
from app.shared.pregnancy_rag.pregnancy_models import (
    PregnancyWeek, KeyDevelopment, PersonalizedKeyDevelopment, 
    PatientProfile, PatientDiseaseHistory, RAGPregnancyResponse
)
from app.shared.pregnancy_rag.services.qdrant_service import QdrantService
from app.shared.pregnancy_rag.services.patient_backend_service import PatientBackendService
import json
import re
from app.shared.pregnancy_rag.baby_image_generator import BabySizeImageGenerator


class RAGService:
    def __init__(self, qdrant_service: QdrantService, patient_service: PatientBackendService):
        self.qdrant_service = qdrant_service
        self.patient_service = patient_service
        self.image_generator = BabySizeImageGenerator()
    
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
            
            disease_history = patient_profile.disease_history
            
            # STEP 3: AUGMENTATION - Build comprehensive context
            rag_context = self._build_rag_context(week_data, related_weeks, patient_profile)
            
            # STEP 4: GENERATION - Use LLM or rule-based for personalized developments
            if use_openai:
                personalized_developments = await self._generate_personalized_developments_ai(
                    rag_context, week_data, patient_profile
                )
            else:
                # Fallback to rule-based personalization
                personalized_developments = self._rule_based_personalization(
                    week_data, disease_history
                )
            
            return RAGPregnancyResponse(
                patient_id=patient_id,
                week=week,
                trimester=week_data.trimester,
                personalized_developments=personalized_developments,
                medical_advisories=self._generate_medical_advisories(disease_history, week),
                special_monitoring=self._get_monitoring_recommendations(disease_history),
                rag_context=rag_context,
                confidence_score=self._calculate_confidence_score(patient_profile, week_data),
                message=f"Personalized information for week {week} based on medical history"
            )
        
        except Exception as e:
            raise Exception(f"RAG processing error: {str(e)}")
    
    def _build_rag_context(
        self, 
        week_data: PregnancyWeek, 
        related_weeks: List[Dict], 
        patient: PatientProfile
    ) -> str:
        """Build comprehensive context for LLM"""
        
        context = f"""
        PREGNANCY CONTEXT:
        Week: {week_data.week}
        Trimester: {week_data.trimester}
        Baby Size: {week_data.baby_size.size} ({week_data.baby_size.weight}, {week_data.baby_size.length})
        
        KEY DEVELOPMENTS:
        """
        
        for dev in week_data.key_developments:
            context += f"- {dev.title}: {dev.description}\n"
        
        context += f"""
        SYMPTOMS: {', '.join(week_data.symptoms)}
        TIPS: {', '.join(week_data.tips)}
        
        PATIENT PROFILE:
        Age: {patient.age}
        Blood Type: {patient.blood_type}
        Previous Pregnancies: {patient.previous_pregnancies}
        Current Medications: {', '.join(patient.current_medications)}
        Allergies: {', '.join(patient.allergies)}
        
        DISEASE HISTORY:
        """
        
        if patient.disease_history:
            for disease in patient.disease_history:
                context += f"""
        - {disease.disease_name}
          Severity: {disease.severity}
          Status: {disease.current_status}
          Treatment: {', '.join(disease.treatment)}
          Pregnancy Impact: {disease.pregnancy_impact or 'Not specified'}
        """
        else:
            context += "No significant disease history"
        
        # Add related weeks context
        if related_weeks:
            context += "\n\nRELATED WEEKS CONTEXT:\n"
            for week_info in related_weeks[:2]:  # Limit to top 2 related weeks
                context += f"Week {week_info['week']}: {week_info['matched_text'][:100]}...\n"
        
        return context
    
    async def _generate_personalized_developments_ai(
        self, 
        context: str, 
        week_data: PregnancyWeek, 
        patient: PatientProfile
    ) -> List[PersonalizedKeyDevelopment]:
        """Use AI to generate personalized developments"""
        
        # This would integrate with your existing OpenAI service
        # For now, we'll use a structured prompt approach
        
        prompt = f"""
        You are a medical AI assistant specializing in pregnancy care. 
        Based on the following patient context and pregnancy week information, 
        provide personalized key developments that consider the patient's medical history.
        
        {context}
        
        For each original development, provide:
        1. A personalized note considering their medical conditions
        2. Medical considerations specific to their diseases
        3. Risk level assessment (low/medium/high)
        4. Monitoring recommendations
        
        Respond in JSON format with this structure:
        {{
            "developments": [
                {{
                    "original_title": "Original development title",
                    "personalized_note": "Personalized explanation considering medical history",
                    "medical_consideration": "Specific medical consideration for their condition",
                    "risk_level": "low/medium/high",
                    "monitoring_recommendations": ["recommendation1", "recommendation2"]
                }}
            ]
        }}
        """
        
        # For now, we'll use rule-based approach as fallback
        # In production, you would call your OpenAI service here
        return self._rule_based_personalization(week_data, patient.disease_history)
    
    def _rule_based_personalization(
        self, 
        week_data: PregnancyWeek, 
        disease_history: List[PatientDiseaseHistory]
    ) -> List[PersonalizedKeyDevelopment]:
        """Rule-based personalization as fallback"""
        
        personalized_developments = []
        
        for development in week_data.key_developments:
            personalized_note = development.description
            medical_consideration = "Standard monitoring recommended"
            risk_level = "low"
            monitoring_recommendations = []
            
            # Apply rules based on disease history
            for disease in disease_history:
                if "cancer" in disease.disease_name.lower():
                    personalized_note += f" Due to your {disease.disease_name} history, extra monitoring is recommended."
                    medical_consideration = f"Previous {disease.disease_name} treatment may affect fetal development"
                    risk_level = "medium" if disease.severity == "moderate" else "high"
                    monitoring_recommendations.extend([
                        "Weekly ultrasound monitoring",
                        "Oncologist consultation",
                        "Specialized blood work"
                    ])
                
                elif "diabetes" in disease.disease_name.lower():
                    personalized_note += f" Blood sugar control is crucial during this development phase."
                    medical_consideration = "Diabetes can affect fetal growth and development"
                    risk_level = "medium"
                    monitoring_recommendations.extend([
                        "Daily blood glucose monitoring",
                        "Nutritionist consultation",
                        "Fetal growth monitoring"
                    ])
                
                elif "hypertension" in disease.disease_name.lower():
                    personalized_note += f" Blood pressure monitoring is essential."
                    medical_consideration = "Hypertension increases risk of complications"
                    risk_level = "medium"
                    monitoring_recommendations.extend([
                        "Daily blood pressure monitoring",
                        "Preeclampsia screening",
                        "Cardiologist consultation"
                    ])
                
                elif "autoimmune" in disease.disease_name.lower() or "lupus" in disease.disease_name.lower():
                    personalized_note += f" Autoimmune conditions require specialized care."
                    medical_consideration = "Autoimmune disease can affect pregnancy outcomes"
                    risk_level = "high"
                    monitoring_recommendations.extend([
                        "Rheumatologist consultation",
                        "Immune system monitoring",
                        "Specialized ultrasound studies"
                    ])
            
            # Remove duplicates from monitoring recommendations
            monitoring_recommendations = list(set(monitoring_recommendations))
            
            personalized_developments.append(PersonalizedKeyDevelopment(
                original_development=development,
                personalized_note=personalized_note,
                medical_consideration=medical_consideration,
                risk_level=risk_level,
                monitoring_recommendations=monitoring_recommendations
            ))
        
        return personalized_developments
    
    def _generate_medical_advisories(self, disease_history: List[PatientDiseaseHistory], week: int) -> List[str]:
        """Generate medical advisories based on disease history"""
        advisories = []
        
        for disease in disease_history:
            if "cancer" in disease.disease_name.lower():
                advisories.extend([
                    "Coordinate with oncology team for pregnancy monitoring",
                    "Consider genetic counseling due to cancer history",
                    "Monitor for cancer recurrence signs"
                ])
            
            elif "diabetes" in disease.disease_name.lower():
                advisories.extend([
                    "Maintain strict blood glucose control",
                    "Regular endocrinologist consultations",
                    "Monitor for gestational diabetes progression"
                ])
            
            elif "hypertension" in disease.disease_name.lower():
                advisories.extend([
                    "Monitor blood pressure closely",
                    "Watch for preeclampsia signs",
                    "Consider medication adjustments"
                ])
        
        # Week-specific advisories
        if week < 12:
            advisories.append("First trimester screening recommended")
        elif week >= 24:
            advisories.append("Third trimester monitoring protocols apply")
        
        return list(set(advisories))  # Remove duplicates
    
    def _get_monitoring_recommendations(self, disease_history: List[PatientDiseaseHistory]) -> List[str]:
        """Get monitoring recommendations based on disease history"""
        monitoring = []
        
        for disease in disease_history:
            if "cancer" in disease.disease_name.lower():
                monitoring.extend([
                    "Monthly oncologist visits",
                    "Quarterly tumor marker screening",
                    "Specialized imaging if needed"
                ])
            
            elif "diabetes" in disease.disease_name.lower():
                monitoring.extend([
                    "Weekly endocrinologist visits",
                    "Monthly HbA1c testing",
                    "Fetal growth ultrasounds every 4 weeks"
                ])
            
            elif "hypertension" in disease.disease_name.lower():
                monitoring.extend([
                    "Bi-weekly cardiologist visits",
                    "Weekly blood pressure logs",
                    "Preeclampsia screening"
                ])
        
        return list(set(monitoring))
    
    def _calculate_confidence_score(self, patient: PatientProfile, week_data: PregnancyWeek) -> float:
        """Calculate confidence score based on data completeness"""
        score = 0.8  # Base score
        
        # Increase confidence if we have disease history
        if patient.disease_history:
            score += 0.1
        
        # Increase confidence if we have complete patient data
        if patient.current_medications and patient.allergies is not None:
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    async def get_trimester_fruit_recommendations(
        self, 
        trimester: int, 
        patient_id: str = None,
        use_mock_data: bool = False
    ) -> Dict:
        """RAG-based fruit size recommendations for trimester"""
        
        try:
            # STEP 1: RETRIEVAL - Get weeks for this trimester
            if trimester == 1:
                weeks = list(range(1, 14))
                search_query = "first trimester early pregnancy weeks 1-13"
            elif trimester == 2:
                weeks = list(range(14, 27))
                search_query = "second trimester middle pregnancy weeks 14-26"
            elif trimester == 3:
                weeks = list(range(27, 41))
                search_query = "third trimester late pregnancy weeks 27-40"
            else:
                raise ValueError("Trimester must be 1, 2, or 3")
            
            # Get trimester-specific pregnancy data
            trimester_weeks = []
            for week in weeks:
                week_data = self.qdrant_service.get_week_by_number(week)
                if week_data:
                    trimester_weeks.append(week_data)
            
            # Get related trimester information
            related_info = self.qdrant_service.semantic_search(
                search_query, 
                limit=5
            )
            
            # STEP 2: RETRIEVAL - Get patient profile if provided
            patient_profile = None
            if patient_id:
                try:
                    if use_mock_data:
                        patient_profile = self.patient_service.get_mock_patient_profile(patient_id)
                    else:
                        patient_profile = await self.patient_service.get_patient_profile(patient_id)
                except Exception as e:
                    print(f"Backend not available, using mock data: {e}")
                    patient_profile = self.patient_service.get_mock_patient_profile(patient_id)
            
            # STEP 3: AUGMENTATION - Build fruit recommendation context
            fruit_recommendations = []
            
            # Key weeks for each trimester
            key_weeks = {
                1: [4, 8, 12],
                2: [16, 20, 24],
                3: [28, 32, 36, 40]
            }.get(trimester, [])
            
            for week in key_weeks:
                week_data = self.qdrant_service.get_week_by_number(week)
                if week_data:
                    # Generate fruit image for this week
                    try:
                        fruit_image = self.image_generator.generate_baby_size_image_with_real_fruit(week)
                        
                        recommendation = {
                            "week": week,
                            "fruit_size": week_data.size_comparison,
                            "baby_size": f"~{week_data.size_comparison.split()[-1]}" if week_data.size_comparison else "N/A",
                            "fruit_image": fruit_image,
                            "key_developments": [dev.description for dev in week_data.key_developments[:2]],
                            "trimester_phase": self._get_trimester_phase(week, trimester)
                        }
                        
                        # Add patient-specific notes if available
                        if patient_profile and patient_profile.disease_history:
                            recommendation["medical_notes"] = self._get_fruit_medical_notes(
                                week, patient_profile.disease_history
                            )
                        
                        fruit_recommendations.append(recommendation)
                        
                    except Exception as e:
                        print(f"Error generating fruit image for week {week}: {e}")
                        # Fallback without image
                        fruit_recommendations.append({
                            "week": week,
                            "fruit_size": week_data.size_comparison,
                            "baby_size": f"~{week_data.size_comparison.split()[-1]}" if week_data.size_comparison else "N/A",
                            "fruit_image": None,
                            "key_developments": [dev.description for dev in week_data.key_developments[:2]],
                            "trimester_phase": self._get_trimester_phase(week, trimester),
                            "error": f"Image generation failed: {str(e)}"
                        })
            
            # STEP 4: GENERATION - Create comprehensive response
            context_summary = f"Trimester {trimester} covers weeks {min(weeks)}-{max(weeks)}. "
            context_summary += f"Found {len(trimester_weeks)} weeks of data. "
            if related_info:
                context_summary += f"Retrieved {len(related_info)} related information items. "
            
            if patient_profile:
                context_summary += f"Patient {patient_id} has {len(patient_profile.disease_history)} medical conditions."
            
            return {
                "trimester": trimester,
                "weeks_covered": f"{min(weeks)}-{max(weeks)}",
                "fruit_recommendations": fruit_recommendations,
                "total_weeks": len(weeks),
                "key_weeks_highlighted": key_weeks,
                "rag_context": context_summary,
                "patient_personalized": patient_profile is not None,
                "patient_id": patient_id,
                "message": f"RAG-based fruit size recommendations for Trimester {trimester}",
                "recommendation_summary": self._generate_fruit_summary(trimester, fruit_recommendations)
            }
            
        except Exception as e:
            return {
                "error": f"Error generating trimester fruit recommendations: {str(e)}",
                "trimester": trimester,
                "fruit_recommendations": [],
                "message": "Failed to generate recommendations"
            }
    
    def _get_trimester_phase(self, week: int, trimester: int) -> str:
        """Get the specific phase within a trimester"""
        if trimester == 1:
            if week <= 4:
                return "Very Early"
            elif week <= 8:
                return "Early"
            else:
                return "Late First"
        elif trimester == 2:
            if week <= 18:
                return "Early Second"
            elif week <= 22:
                return "Mid Second"
            else:
                return "Late Second"
        else:  # trimester 3
            if week <= 32:
                return "Early Third"
            elif week <= 36:
                return "Mid Third"
            else:
                return "Late Third"
    
    def _get_fruit_medical_notes(self, week: int, disease_history: List[PatientDiseaseHistory]) -> List[str]:
        """Generate medical notes related to fruit size comparisons"""
        notes = []
        
        for disease in disease_history:
            if disease.disease_name.lower() in ["diabetes", "gestational diabetes"]:
                notes.append(f"Monitor blood sugar levels as baby grows to {self._get_week_fruit(week)} size")
            elif disease.disease_name.lower() in ["hypertension", "high blood pressure"]:
                notes.append(f"Regular blood pressure checks recommended during {self._get_week_fruit(week)} size phase")
            elif disease.disease_name.lower() in ["anemia"]:
                notes.append(f"Iron-rich diet important as baby reaches {self._get_week_fruit(week)} size")
        
        return notes
    
    def _get_week_fruit(self, week: int) -> str:
        """Get fruit name for a specific week"""
        week_data = self.qdrant_service.get_week_by_number(week)
        if week_data and week_data.size_comparison:
            return week_data.size_comparison
        return "current size"
    
    def _generate_fruit_summary(self, trimester: int, recommendations: List[Dict]) -> str:
        """Generate a summary of fruit recommendations for the trimester"""
        if not recommendations:
            return "No fruit recommendations available"
        
        fruits = [rec.get("fruit_size", "Unknown") for rec in recommendations if rec.get("fruit_size")]
        unique_fruits = list(set(fruits))
        
        if trimester == 1:
            return f"Trimester 1: Baby grows from tiny seed to {unique_fruits[-1] if unique_fruits else 'small fruit'} size. Key milestones: {', '.join(unique_fruits[:3]) if len(unique_fruits) >= 3 else ', '.join(unique_fruits)}"
        elif trimester == 2:
            return f"Trimester 2: Baby develops from {unique_fruits[0] if unique_fruits else 'small'} to {unique_fruits[-1] if unique_fruits else 'medium'} size. Major growth phase with fruits like {', '.join(unique_fruits[:3]) if len(unique_fruits) >= 3 else ', '.join(unique_fruits)}"
        else:
            return f"Trimester 3: Baby reaches {unique_fruits[-1] if unique_fruits else 'large'} size, preparing for birth. Final growth includes {', '.join(unique_fruits[:3]) if len(unique_fruits) >= 3 else ', '.join(unique_fruits)}"
