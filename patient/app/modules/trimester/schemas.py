"""
Pydantic Models for Trimester Module

This file contains all data models used by the trimester module.
These models are used for data validation, serialization, and API responses.
"""

from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime


class KeyDevelopment(BaseModel):
    """Model for key pregnancy developments"""
    title: str
    description: str
    icon: Optional[str] = None
    category: str


class BabySize(BaseModel):
    """Model for baby size information"""
    size: str
    weight: Optional[str] = None
    length: Optional[str] = None


class PregnancyWeek(BaseModel):
    """Model for pregnancy week data"""
    week: int
    trimester: int
    days_remaining: int
    baby_size: BabySize
    key_developments: List[KeyDevelopment]
    symptoms: List[str]
    tips: List[str]


class PregnancyResponse(BaseModel):
    """Model for pregnancy API responses"""
    success: bool
    data: Optional[PregnancyWeek] = None
    message: Optional[str] = None


class QuickActionResponse(BaseModel):
    """Model for quick action API responses"""
    success: bool
    week: int
    trimester: int
    action_type: str
    data: Dict
    message: Optional[str] = None


class SymptomInfo(BaseModel):
    """Model for symptom information"""
    common_symptoms: List[str]
    when_to_call_doctor: List[str]
    relief_tips: List[str]
    severity_level: str


class ScreeningInfo(BaseModel):
    """Model for screening information"""
    recommended_tests: List[str]
    test_descriptions: List[str]
    timing: str
    importance: str


class WellnessInfo(BaseModel):
    """Model for wellness information"""
    exercise_tips: List[str]
    sleep_advice: List[str]
    stress_management: List[str]
    general_wellness: List[str]


class NutritionInfo(BaseModel):
    """Model for nutrition information"""
    essential_nutrients: List[str]
    foods_to_avoid: List[str]
    meal_suggestions: List[str]
    hydration_tips: List[str]


# RAG and Medical History Models
class PatientDiseaseHistory(BaseModel):
    """Model for patient disease history"""
    disease_name: str
    diagnosis_date: Optional[datetime] = None
    severity: str  # mild, moderate, severe
    treatment: List[str] = []
    current_status: str  # active, remission, resolved
    pregnancy_impact: Optional[str] = None


class PatientProfile(BaseModel):
    """Model for patient profile"""
    patient_id: str
    age: int
    blood_type: str
    lmp_date: datetime  # Last Menstrual Period
    expected_delivery: datetime
    disease_history: List[PatientDiseaseHistory] = []
    current_medications: List[str] = []
    allergies: List[str] = []
    previous_pregnancies: int = 0


class PersonalizedKeyDevelopment(BaseModel):
    """Model for personalized key developments"""
    original_development: KeyDevelopment
    personalized_note: str
    medical_consideration: str
    risk_level: str  # low, medium, high
    monitoring_recommendations: List[str] = []


class RAGPregnancyResponse(BaseModel):
    """Model for RAG-based pregnancy responses"""
    patient_id: str
    week: int
    trimester: int
    personalized_developments: List[PersonalizedKeyDevelopment]
    medical_advisories: List[str]
    special_monitoring: List[str]
    rag_context: str
    confidence_score: float
    message: Optional[str] = None
