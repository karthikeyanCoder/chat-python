import asyncio
import httpx
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from .pregnancy_models import *
from .pregnancy_data_service import PregnancyDataService
from .pregnancy_openai_service import OpenAIBabySizeService as PregnancyOpenAIService
from .pregnancy_image_generator import BabySizeImageGenerator
import json

class PregnancyService:
    def __init__(self):
        self.data_service = PregnancyDataService()
        self.image_generator = BabySizeImageGenerator()
        self.openai_service = None
        
        # Initialize OpenAI service if available
        try:
            self.openai_service = PregnancyOpenAIService()
            print("[OK] Pregnancy OpenAI service initialized")
        except ValueError as e:
            print(f"[WARN] Pregnancy OpenAI service not available: {e}")
            print("[INFO] AI features will use fallback data")
    
    def get_pregnancy_week_data(self, week: int) -> PregnancyResponse:
        """Get pregnancy week data"""
        try:
            if week < 1 or week > 40:
                return PregnancyResponse(
                    success=False,
                    message="Week must be between 1 and 40"
                )
            
            week_data = self.data_service.get_week_data(week)
            return PregnancyResponse(
                success=True,
                data=week_data,
                message=f"Successfully retrieved data for week {week}"
            )
        except Exception as e:
            return PregnancyResponse(
                success=False,
                message=f"Error retrieving week data: {str(e)}"
            )
    
    def get_all_pregnancy_weeks(self) -> Dict[int, PregnancyWeek]:
        """Get all pregnancy weeks data"""
        return self.data_service.get_all_weeks()
    
    def get_trimester_weeks(self, trimester: int) -> Dict[int, PregnancyWeek]:
        """Get weeks for a specific trimester"""
        if trimester not in [1, 2, 3]:
            return {}
        return self.data_service.get_trimester_weeks(trimester)
    
    def get_baby_size_image(self, week: int, style: str = "matplotlib") -> Dict:
        """Get baby size visualization image"""
        try:
            if week < 1 or week > 40:
                return {
                    "success": False,
                    "message": "Week must be between 1 and 40"
                }
            
            if style == "simple":
                image_data = self.image_generator.generate_simple_baby_image(week)
            else:
                image_data = self.image_generator.generate_baby_size_image(week)
            
            return {
                "success": True,
                "week": week,
                "image_data": image_data,
                "style": style,
                "message": f"Successfully generated baby size image for week {week}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error generating image: {str(e)}"
            }
    
    async def get_ai_baby_size(self, week: int) -> Dict:
        """Get AI-powered baby size information"""
        try:
            if week < 1 or week > 40:
                return {
                    "success": False,
                    "message": "Week must be between 1 and 40"
                }
            
            if not self.openai_service:
                return {
                    "success": False,
                    "message": "OpenAI service not available"
                }
            
            baby_size = await self.openai_service.get_baby_size_for_week(week)
            detailed_info = await self.openai_service.get_detailed_baby_info(week)
            
            return {
                "success": True,
                "week": week,
                "baby_size": baby_size.dict(),
                "detailed_info": detailed_info,
                "message": f"Successfully generated AI-powered baby size for week {week}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error generating AI baby size: {str(e)}"
            }
    
    async def get_early_symptoms(self, week: int) -> QuickActionResponse:
        """Get AI-powered early symptoms information"""
        try:
            if week < 1 or week > 40:
                return QuickActionResponse(
                    success=False,
                    week=week,
                    trimester=0,
                    action_type="early_symptoms",
                    data={},
                    message="Week must be between 1 and 40"
                )
            
            week_data = self.data_service.get_week_data(week)
            
            if not self.openai_service:
                # Use fallback data
                symptoms_info = SymptomInfo(
                    common_symptoms=week_data.symptoms,
                    when_to_call_doctor=["Contact your healthcare provider if concerned"],
                    relief_tips=week_data.tips,
                    severity_level="moderate"
                )
            else:
                symptoms_info = await self.openai_service.get_early_symptoms(week)
            
            return QuickActionResponse(
                success=True,
                week=week,
                trimester=week_data.trimester,
                action_type="early_symptoms",
                data=symptoms_info.dict(),
                message=f"Successfully generated early symptoms information for week {week}"
            )
        except Exception as e:
            return QuickActionResponse(
                success=False,
                week=week,
                trimester=0,
                action_type="early_symptoms",
                data={},
                message=f"Error generating symptoms: {str(e)}"
            )
    
    async def get_prenatal_screening(self, week: int) -> QuickActionResponse:
        """Get AI-powered prenatal screening information"""
        try:
            if week < 1 or week > 40:
                return QuickActionResponse(
                    success=False,
                    week=week,
                    trimester=0,
                    action_type="prenatal_screening",
                    data={},
                    message="Week must be between 1 and 40"
                )
            
            week_data = self.data_service.get_week_data(week)
            
            if not self.openai_service:
                # Use fallback data
                screening_info = ScreeningInfo(
                    recommended_tests=["Regular prenatal checkups"],
                    test_descriptions=["Monitor baby development"],
                    timing="As recommended by your doctor",
                    importance="Essential for healthy pregnancy"
                )
            else:
                screening_info = await self.openai_service.get_prenatal_screening(week)
            
            return QuickActionResponse(
                success=True,
                week=week,
                trimester=week_data.trimester,
                action_type="prenatal_screening",
                data=screening_info.dict(),
                message=f"Successfully generated prenatal screening information for week {week}"
            )
        except Exception as e:
            return QuickActionResponse(
                success=False,
                week=week,
                trimester=0,
                action_type="prenatal_screening",
                data={},
                message=f"Error generating screening info: {str(e)}"
            )
    
    async def get_wellness_tips(self, week: int) -> QuickActionResponse:
        """Get AI-powered wellness tips"""
        try:
            if week < 1 or week > 40:
                return QuickActionResponse(
                    success=False,
                    week=week,
                    trimester=0,
                    action_type="wellness_tips",
                    data={},
                    message="Week must be between 1 and 40"
                )
            
            week_data = self.data_service.get_week_data(week)
            
            if not self.openai_service:
                # Use fallback data
                wellness_info = WellnessInfo(
                    exercise_tips=["Stay active with safe exercises"],
                    sleep_advice=["Get plenty of rest"],
                    stress_management=["Practice relaxation techniques"],
                    general_wellness=["Maintain healthy lifestyle"]
                )
            else:
                wellness_info = await self.openai_service.get_wellness_tips(week)
            
            return QuickActionResponse(
                success=True,
                week=week,
                trimester=week_data.trimester,
                action_type="wellness_tips",
                data=wellness_info.dict(),
                message=f"Successfully generated wellness tips for week {week}"
            )
        except Exception as e:
            return QuickActionResponse(
                success=False,
                week=week,
                trimester=0,
                action_type="wellness_tips",
                data={},
                message=f"Error generating wellness tips: {str(e)}"
            )
    
    async def get_nutrition_tips(self, week: int) -> QuickActionResponse:
        """Get AI-powered nutrition tips"""
        try:
            if week < 1 or week > 40:
                return QuickActionResponse(
                    success=False,
                    week=week,
                    trimester=0,
                    action_type="nutrition_tips",
                    data={},
                    message="Week must be between 1 and 40"
                )
            
            week_data = self.data_service.get_week_data(week)
            
            if not self.openai_service:
                # Use fallback data
                nutrition_info = NutritionInfo(
                    essential_nutrients=["Folic acid", "Iron", "Calcium"],
                    foods_to_avoid=["Raw fish", "Unpasteurized dairy"],
                    meal_suggestions=["Balanced meals with fruits and vegetables"],
                    hydration_tips=["Drink plenty of water"]
                )
            else:
                nutrition_info = await self.openai_service.get_nutrition_tips(week)
            
            return QuickActionResponse(
                success=True,
                week=week,
                trimester=week_data.trimester,
                action_type="nutrition_tips",
                data=nutrition_info.dict(),
                message=f"Successfully generated nutrition tips for week {week}"
            )
        except Exception as e:
            return QuickActionResponse(
                success=False,
                week=week,
                trimester=0,
                action_type="nutrition_tips",
                data={},
                message=f"Error generating nutrition tips: {str(e)}"
            )
    
    def get_openai_status(self) -> Dict:
        """Get OpenAI service status"""
        return {
            "success": True,
            "openai_available": self.openai_service is not None,
            "message": "OpenAI service status retrieved successfully"
        }
    
    def save_pregnancy_tracking(self, patient_id: str, tracking_data: Dict) -> Dict:
        """Save pregnancy tracking data"""
        try:
            # This would integrate with your MongoDB
            # For now, return success
            return {
                "success": True,
                "message": "Pregnancy tracking data saved successfully",
                "patient_id": patient_id,
                "data": tracking_data
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error saving tracking data: {str(e)}"
            }
    
    def get_pregnancy_tracking_history(self, patient_id: str) -> Dict:
        """Get pregnancy tracking history"""
        try:
            # This would query your MongoDB
            # For now, return empty history
            return {
                "success": True,
                "patient_id": patient_id,
                "history": [],
                "message": "Pregnancy tracking history retrieved successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error retrieving tracking history: {str(e)}"
            }
    
    def calculate_pregnancy_progress(self, patient_id: str, current_week: int) -> PregnancyProgress:
        """Calculate pregnancy progress"""
        try:
            if current_week < 1 or current_week > 40:
                current_week = 1
            
            if current_week <= 12:
                trimester = 1
            elif current_week <= 28:
                trimester = 2
            else:
                trimester = 3
            
            days_remaining = 280 - (current_week - 1) * 7
            progress_percentage = (current_week / 40) * 100
            
            # Determine next milestone
            if current_week < 12:
                next_milestone = "End of First Trimester"
                milestone_week = 12
            elif current_week < 20:
                next_milestone = "Halfway Point"
                milestone_week = 20
            elif current_week < 28:
                next_milestone = "Third Trimester"
                milestone_week = 28
            elif current_week < 37:
                next_milestone = "Full Term"
                milestone_week = 37
            else:
                next_milestone = "Due Date"
                milestone_week = 40
            
            milestone_date = datetime.now() + timedelta(days=(milestone_week - current_week) * 7)
            
            return PregnancyProgress(
                current_week=current_week,
                trimester=trimester,
                days_remaining=days_remaining,
                progress_percentage=progress_percentage,
                next_milestone=next_milestone,
                milestone_date=milestone_date,
                weeks_completed=current_week - 1
            )
        except Exception as e:
            return PregnancyProgress(
                current_week=1,
                trimester=1,
                days_remaining=280,
                progress_percentage=0,
                next_milestone="First Trimester",
                weeks_completed=0
            )
