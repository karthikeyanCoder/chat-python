from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class KeyDevelopment(BaseModel):
    title: str
    description: str
    icon: Optional[str] = None
    category: str

class BabySize(BaseModel):
    size: str
    weight: Optional[str] = None
    length: Optional[str] = None

class PregnancyWeek(BaseModel):
    week: int
    trimester: int
    days_remaining: int
    baby_size: BabySize
    key_developments: List[KeyDevelopment]
    symptoms: List[str]
    tips: List[str]

class PregnancyResponse(BaseModel):
    success: bool
    data: Optional[PregnancyWeek] = None
    message: Optional[str] = None

class QuickActionResponse(BaseModel):
    success: bool
    week: int
    trimester: int
    action_type: str
    data: Dict
    message: Optional[str] = None

class SymptomInfo(BaseModel):
    common_symptoms: List[str]
    when_to_call_doctor: List[str]
    relief_tips: List[str]
    severity_level: str

class ScreeningInfo(BaseModel):
    recommended_tests: List[str]
    test_descriptions: List[str]
    timing: str
    importance: str

class WellnessInfo(BaseModel):
    exercise_tips: List[str]
    sleep_advice: List[str]
    stress_management: List[str]
    general_wellness: List[str]

class NutritionInfo(BaseModel):
    essential_nutrients: List[str]
    foods_to_avoid: List[str]
    meal_suggestions: List[str]
    hydration_tips: List[str]

class PregnancyProgress(BaseModel):
    current_week: int
    trimester: int
    days_remaining: int
    progress_percentage: float
    next_milestone: str
    milestone_date: Optional[datetime] = None
    weeks_completed: int

