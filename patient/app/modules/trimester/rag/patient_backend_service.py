"""
Patient Backend Service for Trimester Module

This service handles communication with the patient backend system
to fetch patient profiles and medical history for RAG personalization.
"""

import httpx
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ..schemas import PatientProfile, PatientDiseaseHistory
from ..config import settings


class PatientBackendService:
    """Service for communicating with the patient backend system"""
    
    def __init__(self, backend_url: str = None):
        self.backend_url = backend_url or settings.PATIENT_BACKEND_URL
        self.api_key = settings.PATIENT_BACKEND_API_KEY
    
    async def get_patient_profile(self, patient_id: str) -> PatientProfile:
        """Fetch patient profile from backend database"""
        try:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.backend_url}/patients/{patient_id}",
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return PatientProfile(**response.json())
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Patient {patient_id} not found in backend system")
            raise Exception(f"Backend API error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise Exception(f"Failed to connect to patient backend: {str(e)}")
        except Exception as e:
            raise Exception(f"Error fetching patient profile: {str(e)}")
    
    async def get_disease_history(self, patient_id: str) -> List[PatientDiseaseHistory]:
        """Get patient's disease history"""
        profile = await self.get_patient_profile(patient_id)
        return profile.disease_history
    
    async def get_patient_by_conditions(self, conditions: List[str]) -> List[PatientProfile]:
        """Get patients with specific medical conditions"""
        try:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.backend_url}/patients/search",
                    params={"conditions": ",".join(conditions)},
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                
                patients_data = response.json()
                return [PatientProfile(**patient) for patient in patients_data]
        
        except httpx.HTTPStatusError as e:
            raise Exception(f"Backend API error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise Exception(f"Failed to connect to patient backend: {str(e)}")
        except Exception as e:
            raise Exception(f"Error fetching patients by conditions: {str(e)}")
    
    def get_mock_patient_profile(self, patient_id: str) -> PatientProfile:
        """Generate mock patient profile for testing"""
        # Create mock disease history based on patient_id patterns
        disease_history = []
        
        # Add some mock conditions based on patient_id
        if "diabetes" in patient_id.lower():
            disease_history.append(PatientDiseaseHistory(
                disease_name="Type 2 Diabetes",
                diagnosis_date=datetime.now() - timedelta(days=365),
                severity="moderate",
                treatment=["Metformin", "Diet management"],
                current_status="active",
                pregnancy_impact="Requires blood sugar monitoring and potential medication adjustments"
            ))
        
        if "hypertension" in patient_id.lower():
            disease_history.append(PatientDiseaseHistory(
                disease_name="Hypertension",
                diagnosis_date=datetime.now() - timedelta(days=180),
                severity="mild",
                treatment=["Lisinopril"],
                current_status="active",
                pregnancy_impact="Increased risk of preeclampsia, requires blood pressure monitoring"
            ))
        
        if "cancer" in patient_id.lower():
            disease_history.append(PatientDiseaseHistory(
                disease_name="Breast Cancer",
                diagnosis_date=datetime.now() - timedelta(days=730),
                severity="moderate",
                treatment=["Chemotherapy", "Radiation therapy"],
                current_status="remission",
                pregnancy_impact="Previous cancer treatment may affect fertility and pregnancy risks"
            ))
        
        # Default mock profile
        if not disease_history:
            disease_history.append(PatientDiseaseHistory(
                disease_name="None",
                severity="none",
                treatment=[],
                current_status="healthy",
                pregnancy_impact="No significant medical history affecting pregnancy"
            ))
        
        return PatientProfile(
            patient_id=patient_id,
            age=28,
            blood_type="O+",
            lmp_date=datetime.now() - timedelta(days=70),  # 10 weeks ago
            expected_delivery=datetime.now() + timedelta(days=210),
            disease_history=disease_history,
            current_medications=["Prenatal vitamins"],
            allergies=["None known"],
            previous_pregnancies=0
        )
    
    def get_mock_disease_history(self, patient_id: str) -> List[PatientDiseaseHistory]:
        """Get mock disease history for testing"""
        profile = self.get_mock_patient_profile(patient_id)
        return profile.disease_history
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if the patient backend service is healthy"""
        try:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.backend_url}/health",
                    headers=headers,
                    timeout=10.0
                )
                response.raise_for_status()
                
                return {
                    "status": "healthy",
                    "backend_url": self.backend_url,
                    "response_time": response.elapsed.total_seconds()
                }
        
        except Exception as e:
            return {
                "status": "unhealthy",
                "backend_url": self.backend_url,
                "error": str(e)
            }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get the current status of the patient backend service"""
        return {
            "backend_url": self.backend_url,
            "api_key_configured": bool(self.api_key),
            "service_type": "patient_backend"
        }
