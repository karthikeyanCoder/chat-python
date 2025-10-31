import httpx
from typing import List, Optional
from app.shared.pregnancy_rag.pregnancy_models import PatientProfile, PatientDiseaseHistory
from app.shared.pregnancy_rag.pregnancy_config import settings
import json


class PatientBackendService:
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
                    headers=headers,
                    params={"conditions": ",".join(conditions)},
                    timeout=30.0
                )
                response.raise_for_status()
                
                patients_data = response.json()
                return [PatientProfile(**patient) for patient in patients_data]
        
        except Exception as e:
            raise Exception(f"Error searching patients by conditions: {str(e)}")
    
    def get_mock_patient_profile(self, patient_id: str) -> PatientProfile:
        """Get mock patient profile for testing when backend is not available"""
        from datetime import datetime, timedelta
        
        # Mock data based on patient ID patterns
        if "cancer" in patient_id.lower():
            return PatientProfile(
                patient_id=patient_id,
                age=32,
                blood_type="O+",
                lmp_date=datetime.now() - timedelta(days=70),  # 10 weeks ago
                expected_delivery=datetime.now() + timedelta(days=210),
                disease_history=[
                    PatientDiseaseHistory(
                        disease_name="Breast Cancer",
                        diagnosis_date=datetime(2022, 6, 15),
                        severity="moderate",
                        treatment=["Chemotherapy", "Radiation"],
                        current_status="remission",
                        pregnancy_impact="Increased monitoring required"
                    )
                ],
                current_medications=["Tamoxifen", "Folic Acid"],
                allergies=["Penicillin"],
                previous_pregnancies=0
            )
        
        elif "diabetes" in patient_id.lower():
            return PatientProfile(
                patient_id=patient_id,
                age=28,
                blood_type="A+",
                lmp_date=datetime.now() - timedelta(days=105),  # 15 weeks ago
                expected_delivery=datetime.now() + timedelta(days=175),
                disease_history=[
                    PatientDiseaseHistory(
                        disease_name="Type 2 Diabetes",
                        diagnosis_date=datetime(2021, 3, 10),
                        severity="moderate",
                        treatment=["Metformin", "Diet Control"],
                        current_status="active",
                        pregnancy_impact="Blood sugar monitoring essential"
                    )
                ],
                current_medications=["Metformin", "Insulin"],
                allergies=["Sulfa drugs"],
                previous_pregnancies=1
            )
        
        elif "hypertension" in patient_id.lower():
            return PatientProfile(
                patient_id=patient_id,
                age=35,
                blood_type="B+",
                lmp_date=datetime.now() - timedelta(days=140),  # 20 weeks ago
                expected_delivery=datetime.now() + timedelta(days=140),
                disease_history=[
                    PatientDiseaseHistory(
                        disease_name="Chronic Hypertension",
                        diagnosis_date=datetime(2020, 8, 20),
                        severity="mild",
                        treatment=["Lisinopril", "Lifestyle modifications"],
                        current_status="active",
                        pregnancy_impact="Increased risk of preeclampsia"
                    )
                ],
                current_medications=["Lisinopril", "Prenatal vitamins"],
                allergies=["ACE inhibitors"],
                previous_pregnancies=0
            )
        
        else:
            # Default healthy patient
            return PatientProfile(
                patient_id=patient_id,
                age=30,
                blood_type="O+",
                lmp_date=datetime.now() - timedelta(days=70),  # 10 weeks ago
                expected_delivery=datetime.now() + timedelta(days=210),
                disease_history=[],
                current_medications=["Prenatal vitamins"],
                allergies=[],
                previous_pregnancies=0
            )
