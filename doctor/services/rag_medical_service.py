import os
import json
import openai
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from .vector_database import VectorDatabase
from .medical_knowledge_base import MedicalKnowledgeBase

class RAGMedicalService:
    """
    RAG (Retrieval-Augmented Generation) service for medical AI summaries.
    Combines patient data with medical knowledge base for enhanced analysis.
    """
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.vector_db = VectorDatabase()
        self.knowledge_base = MedicalKnowledgeBase()
        self.logger = logging.getLogger(__name__)
        
        if not self.openai_api_key:
            self.logger.warning("OpenAI API key not found. RAG features will be limited.")
    
    def get_medical_context(self, patient_data: Dict[str, Any], query_type: str = "general") -> List[Dict[str, Any]]:
        """
        Retrieve relevant medical context based on patient data and query type.
        
        Args:
            patient_data: Patient's health data
            query_type: Type of medical query (general, pregnancy, symptoms, etc.)
        
        Returns:
            List of relevant medical knowledge chunks
        """
        try:
            # Extract key medical concepts from patient data
            medical_concepts = self._extract_medical_concepts(patient_data)
            
            # Build search query
            search_query = self._build_search_query(patient_data, query_type, medical_concepts)
            
            # Retrieve relevant knowledge chunks
            context_chunks = self.vector_db.search_similar_chunks(
                query=search_query,
                top_k=5,
                filter_type=query_type
            )
            
            return context_chunks
            
        except Exception as e:
            self.logger.error(f"Error retrieving medical context: {str(e)}")
            return []
    
    def generate_enhanced_summary(
        self, 
        patient_data: Dict[str, Any], 
        medical_context: List[Dict[str, Any]],
        query_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Generate enhanced AI summary using RAG with medical context.
        
        Args:
            patient_data: Patient's health data
            medical_context: Retrieved medical knowledge chunks
            query_type: Type of medical query
        
        Returns:
            Enhanced AI summary with medical context
        """
        try:
            if not self.openai_api_key:
                return self._generate_fallback_summary(patient_data)
            
            # Prepare context for OpenAI
            context_text = self._prepare_context_text(medical_context)
            
            # Build enhanced prompt with medical context
            enhanced_prompt = self._build_enhanced_prompt(
                patient_data, 
                context_text, 
                query_type
            )
            
            # Generate AI summary with OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(query_type)
                    },
                    {
                        "role": "user",
                        "content": enhanced_prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            ai_summary = response.choices[0].message.content
            
            # Parse and structure the response
            return self._parse_ai_response(ai_summary, patient_data, medical_context)
            
        except Exception as e:
            self.logger.error(f"Error generating enhanced summary: {str(e)}")
            return self._generate_fallback_summary(patient_data)
    
    def _extract_medical_concepts(self, patient_data: Dict[str, Any]) -> List[str]:
        """Extract key medical concepts from patient data."""
        concepts = []
        
        # Extract from symptoms
        if 'symptom_analysis_reports' in patient_data:
            for report in patient_data['symptom_analysis_reports']:
                if 'symptom_text' in report:
                    concepts.append(report['symptom_text'])
                if 'severity' in report:
                    concepts.append(f"severity: {report['severity']}")
        
        # Extract from medications
        if 'medication_logs' in patient_data:
            for med in patient_data['medication_logs']:
                if 'medication_name' in med:
                    concepts.append(f"medication: {med['medication_name']}")
        
        # Extract from pregnancy data
        if 'pregnancy_week' in patient_data:
            concepts.append(f"pregnancy week: {patient_data['pregnancy_week']}")
        
        if 'trimester' in patient_data:
            concepts.append(f"trimester: {patient_data['trimester']}")
        
        # Extract from vital signs
        if 'vital_signs' in patient_data:
            for vital in patient_data['vital_signs']:
                if 'type' in vital and 'value' in vital:
                    concepts.append(f"{vital['type']}: {vital['value']}")
        
        return concepts
    
    def _build_search_query(
        self, 
        patient_data: Dict[str, Any], 
        query_type: str, 
        medical_concepts: List[str]
    ) -> str:
        """Build search query for vector database."""
        query_parts = []
        
        # Add query type
        query_parts.append(f"medical query type: {query_type}")
        
        # Add pregnancy context
        if 'pregnancy_week' in patient_data:
            query_parts.append(f"pregnancy week {patient_data['pregnancy_week']}")
        
        if 'trimester' in patient_data:
            query_parts.append(f"{patient_data['trimester']} trimester")
        
        # Add medical concepts
        query_parts.extend(medical_concepts[:10])  # Limit to top 10 concepts
        
        # Add specific conditions
        if 'blood_type' in patient_data:
            query_parts.append(f"blood type {patient_data['blood_type']}")
        
        if 'age' in patient_data:
            query_parts.append(f"age {patient_data['age']}")
        
        return " ".join(query_parts)
    
    def _prepare_context_text(self, medical_context: List[Dict[str, Any]]) -> str:
        """Prepare medical context text for OpenAI prompt."""
        if not medical_context:
            return "No specific medical context available."
        
        context_parts = []
        for chunk in medical_context:
            if 'content' in chunk:
                context_parts.append(f"- {chunk['content']}")
            elif 'text' in chunk:
                context_parts.append(f"- {chunk['text']}")
        
        return "\n".join(context_parts)
    
    def _build_enhanced_prompt(
        self, 
        patient_data: Dict[str, Any], 
        context_text: str, 
        query_type: str
    ) -> str:
        """Build enhanced prompt with medical context."""
        prompt = f"""
        You are a medical AI assistant analyzing a pregnant patient's health data. 
        Use the provided medical context to enhance your analysis.

        MEDICAL CONTEXT:
        {context_text}

        PATIENT DATA:
        {json.dumps(patient_data, indent=2, default=str)}

        Please provide a comprehensive medical summary including:
        1. Overall health assessment
        2. Pregnancy-specific insights
        3. Risk factors and recommendations
        4. Medication safety analysis
        5. Symptom pattern analysis
        6. Personalized care suggestions

        Focus on evidence-based medical recommendations and consider the patient's 
        pregnancy stage and specific health conditions.
        """
        return prompt
    
    def _get_system_prompt(self, query_type: str) -> str:
        """Get system prompt based on query type."""
        base_prompt = """
        You are an expert medical AI assistant specializing in pregnancy care and women's health.
        You have access to a comprehensive medical knowledge base and should provide:
        - Evidence-based medical recommendations
        - Pregnancy-specific health insights
        - Risk assessment and safety considerations
        - Personalized care suggestions
        - Clear, actionable medical advice
        """
        
        if query_type == "pregnancy":
            return base_prompt + "\n\nFocus specifically on pregnancy-related health concerns and recommendations."
        elif query_type == "symptoms":
            return base_prompt + "\n\nFocus on symptom analysis and appropriate medical responses."
        elif query_type == "medications":
            return base_prompt + "\n\nFocus on medication safety and pregnancy considerations."
        else:
            return base_prompt
    
    def _parse_ai_response(
        self, 
        ai_summary: str, 
        patient_data: Dict[str, Any], 
        medical_context: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Parse and structure AI response."""
        return {
            "ai_summary": ai_summary,
            "medical_context_used": len(medical_context),
            "context_sources": [chunk.get('source', 'unknown') for chunk in medical_context],
            "generated_at": datetime.utcnow().isoformat(),
            "rag_enhanced": True,
            "patient_data_summary": {
                "pregnancy_week": patient_data.get('pregnancy_week', 'N/A'),
                "age": patient_data.get('age', 'N/A'),
                "blood_type": patient_data.get('blood_type', 'N/A'),
                "last_period_date": patient_data.get('last_period_date', 'N/A')
            }
        }
    
    def _generate_fallback_summary(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback summary when OpenAI is unavailable."""
        return {
            "ai_summary": "AI analysis temporarily unavailable. Please consult with your healthcare provider for medical advice.",
            "medical_context_used": 0,
            "context_sources": [],
            "generated_at": datetime.utcnow().isoformat(),
            "rag_enhanced": False,
            "patient_data_summary": {
                "pregnancy_week": patient_data.get('pregnancy_week', 'N/A'),
                "age": patient_data.get('age', 'N/A'),
                "blood_type": patient_data.get('blood_type', 'N/A'),
                "last_period_date": patient_data.get('last_period_date', 'N/A')
            }
        }
    
    def add_medical_knowledge(self, knowledge_chunks: List[Dict[str, Any]]) -> bool:
        """Add new medical knowledge chunks to the vector database."""
        try:
            return self.vector_db.add_chunks(knowledge_chunks)
        except Exception as e:
            self.logger.error(f"Error adding medical knowledge: {str(e)}")
            return False
    
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """Get statistics about the medical knowledge base."""
        try:
            return self.vector_db.get_stats()
        except Exception as e:
            self.logger.error(f"Error getting knowledge base stats: {str(e)}")
            return {"error": str(e)}
