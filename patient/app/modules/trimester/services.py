"""
Trimester Services

This file contains the core business logic for the trimester module.
It includes services for pregnancy data, OpenAI integration, and image generation.
"""

import asyncio
import json
import base64
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta

from .schemas import (
    PregnancyWeek, KeyDevelopment, BabySize, PregnancyResponse,
    QuickActionResponse, SymptomInfo, ScreeningInfo, WellnessInfo, NutritionInfo
)
from .config import settings


class PregnancyDataService:
    """Service for managing pregnancy week data"""
    
    def __init__(self, use_qdrant: bool = None):
        """
        Initialize PregnancyDataService
        
        Args:
            use_qdrant: If True, use Qdrant for data storage. If None, auto-detect based on config.
        """
        # Auto-detect if Qdrant should be used
        if use_qdrant is None:
            use_qdrant = bool(settings.QDRANT_URL)
        
        self.use_qdrant = use_qdrant
        self.qdrant_service = None
        
        # Always initialize in-memory data as fallback
        self.pregnancy_data = self._initialize_data()
        
        if self.use_qdrant:
            try:
                from .rag.qdrant_service import QdrantService
                self.qdrant_service = QdrantService()
                print("✅ Using Qdrant for pregnancy data storage")
            except Exception as e:
                print(f"⚠️  Qdrant initialization failed: {e}")
                print("Falling back to in-memory data")
                self.use_qdrant = False
        else:
            print("ℹ️  Using in-memory data storage")
    
    def get_week_data(self, week: int) -> PregnancyWeek:
        """Get pregnancy data for a specific week"""
        if week < 1 or week > 40:
            raise ValueError(f"Week {week} is not valid. Week must be between 1 and 40.")
        
        if self.use_qdrant and self.qdrant_service:
            return self._get_week_data_from_qdrant(week)
        else:
            return self.pregnancy_data.get(week)
    
    def get_all_weeks(self) -> Dict[int, PregnancyWeek]:
        """Get all pregnancy week data"""
        if self.use_qdrant and self.qdrant_service:
            return self._get_all_weeks_from_qdrant()
        else:
            return self.pregnancy_data
    
    def get_weeks_by_trimester(self, trimester: int) -> List[PregnancyWeek]:
        """Get all weeks for a specific trimester"""
        weeks = []
        for week in range(1, 41):
            week_data = self.get_week_data(week)
            if week_data.trimester == trimester:
                weeks.append(week_data)
        return weeks
    
    def semantic_search(self, query: str, limit: int = 5) -> List[Dict]:
        """Perform semantic search on pregnancy data"""
        if not self.use_qdrant or not self.qdrant_service:
            raise ValueError("Semantic search requires Qdrant configuration")
        
        return self.qdrant_service.semantic_search(query, limit=limit)
    
    def _get_week_data_from_qdrant(self, week: int) -> PregnancyWeek:
        """Get week data from Qdrant"""
        # This would be implemented based on Qdrant service
        # For now, fallback to in-memory data
        return self.pregnancy_data.get(week)
    
    def _get_all_weeks_from_qdrant(self) -> Dict[int, PregnancyWeek]:
        """Get all weeks data from Qdrant"""
        # This would be implemented based on Qdrant service
        # For now, fallback to in-memory data
        return self.pregnancy_data
    
    def _initialize_data(self) -> Dict[int, PregnancyWeek]:
        """Initialize pregnancy week data with key developments - loads all 40 weeks"""
        try:
            # Try to import full pregnancy data from shared pregnancy_rag module
            from app.shared.pregnancy_rag.pregnancy_data_full import get_all_40_weeks_data
            return get_all_40_weeks_data()
        except Exception as e:
            print(f"⚠️ Could not load full pregnancy data: {e}")
            print("Using basic fallback data")
            
            # Fallback: Basic data for key weeks
            data = {}
            
            # Week 1
            data[1] = PregnancyWeek(
                week=1,
                trimester=1,
                days_remaining=280,
                baby_size=BabySize(size="Poppy seed", weight="0.1g", length="0.1cm"),
                key_developments=[
                    KeyDevelopment(
                        title="Fertilization",
                        description="The egg is fertilized by sperm, beginning the journey of pregnancy.",
                        icon="🌱",
                        category="conception"
                    ),
                ],
                symptoms=["Spotting", "Mild cramping"],
                tips=["Start taking prenatal vitamins", "Avoid alcohol and smoking"]
            )
            
            # Week 10
            data[10] = PregnancyWeek(
                week=10,
                trimester=1,
                days_remaining=210,
                baby_size=BabySize(size="Kumquat", weight="4g", length="3.1cm"),
                key_developments=[
                    KeyDevelopment(
                        title="Finger Development",
                        description="Tiny fingers and toes are forming with individual digits.",
                        icon="👶",
                        category="development"
                    ),
                ],
                symptoms=["Nausea", "Fatigue", "Breast tenderness"],
                tips=["Eat small, frequent meals", "Stay hydrated", "Get plenty of rest"]
            )
            
            return data


class OpenAIBabySizeService:
    """Service for OpenAI-powered baby size and development information"""
    
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key is required. Please set OPENAI_API_KEY in your environment variables.")
        
        try:
            import openai
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.OPENAI_MODEL
            self.max_tokens = settings.OPENAI_MAX_TOKENS
        except ImportError:
            raise ValueError("OpenAI package is required. Please install it with: pip install openai")
    
    async def get_baby_size_for_week(self, week: int) -> BabySize:
        """Get baby size information for a specific pregnancy week using OpenAI"""
        try:
            prompt = self._create_baby_size_prompt(week)
            response = await self._call_openai(prompt)
            baby_size_data = self._parse_baby_size_response(response, week)
            return baby_size_data
        except Exception as e:
            print(f"OpenAI baby size generation failed: {e}")
            return self._get_fallback_baby_size(week)
    
    async def get_early_symptoms(self, week: int) -> SymptomInfo:
        """Get AI-powered early symptoms information"""
        try:
            prompt = self._create_symptoms_prompt(week)
            response = await self._call_openai(prompt)
            return self._parse_symptoms_response(response)
        except Exception as e:
            print(f"OpenAI symptoms generation failed: {e}")
            return self._get_fallback_symptoms(week)
    
    async def get_prenatal_screening(self, week: int) -> ScreeningInfo:
        """Get AI-powered prenatal screening information"""
        try:
            prompt = self._create_screening_prompt(week)
            response = await self._call_openai(prompt)
            return self._parse_screening_response(response)
        except Exception as e:
            print(f"OpenAI screening generation failed: {e}")
            return self._get_fallback_screening(week)
    
    async def get_wellness_tips(self, week: int) -> WellnessInfo:
        """Get AI-powered wellness tips"""
        try:
            prompt = self._create_wellness_prompt(week)
            response = await self._call_openai(prompt)
            return self._parse_wellness_response(response)
        except Exception as e:
            print(f"OpenAI wellness generation failed: {e}")
            return self._get_fallback_wellness(week)
    
    async def get_nutrition_tips(self, week: int) -> NutritionInfo:
        """Get AI-powered nutrition tips"""
        try:
            prompt = self._create_nutrition_prompt(week)
            response = await self._call_openai(prompt)
            return self._parse_nutrition_response(response)
        except Exception as e:
            print(f"OpenAI nutrition generation failed: {e}")
            return self._get_fallback_nutrition(week)
    
    async def get_detailed_baby_info(self, week: int) -> dict:
        """
        Get detailed baby information including size, development milestones, and fun facts
        
        Args:
            week: Pregnancy week (1-40)
            
        Returns:
            Dictionary with detailed baby information
        """
        try:
            prompt = f"""
            Provide detailed information about a baby at pregnancy week {week}. 
            
            Please respond with a JSON object containing:
            - "size": A creative size comparison
            - "weight": Weight in grams
            - "length": Length in centimeters
            - "fun_fact": An interesting fact about development at this week
            - "comparison": A fun comparison (e.g., "size of a ping pong ball")
            - "development_highlight": Key development happening this week
            
            Make it engaging and informative for expectant parents.
            Respond only with valid JSON, no additional text.
            """
            
            response = await self._call_openai(prompt)
            
            # Try to parse JSON response
            try:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    json_str = response[json_start:json_end]
                    return json.loads(json_str)
            except:
                pass
            
            # Fallback response
            return {
                "size": f"Week {week} baby",
                "weight": "Unknown",
                "length": "Unknown",
                "fun_fact": "Your baby is growing every day!",
                "comparison": "Growing steadily",
                "development_highlight": "Continuous development"
            }
            
        except Exception as e:
            print(f"OpenAI detailed baby info generation failed: {e}")
            return {
                "size": f"Week {week} baby",
                "weight": "Unknown",
                "length": "Unknown",
                "fun_fact": "Your baby is growing every day!",
                "comparison": "Growing steadily",
                "development_highlight": "Continuous development"
            }
    
    async def _call_openai(self, prompt: str) -> str:
        """Make async call to OpenAI API"""
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            lambda: self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=0.7
            )
        )
        return response.choices[0].message.content
    
    def _create_baby_size_prompt(self, week: int) -> str:
        """Create a prompt for OpenAI to get baby size information"""
        return f"""
        Provide detailed baby size information for pregnancy week {week}. 
        
        Please respond with a JSON object containing:
        - "size": A relatable size comparison (e.g., "Lima bean", "Blueberry", "Coconut", "Avocado")
        - "weight": Weight in grams (e.g., "0.1g", "1.2g", "15g")
        - "length": Length in centimeters (e.g., "0.1cm", "0.5cm", "2.5cm")
        
        Make the size comparison relatable and easy to understand.
        """
    
    def _create_symptoms_prompt(self, week: int) -> str:
        """Create a prompt for symptoms information"""
        return f"""
        Provide comprehensive early pregnancy symptoms information for week {week}.
        
        Respond with a JSON object containing:
        - "common_symptoms": List of common symptoms for this week
        - "when_to_call_doctor": List of warning signs requiring medical attention
        - "relief_tips": List of practical relief suggestions
        - "severity_level": Overall severity level (mild, moderate, severe)
        """
    
    def _create_screening_prompt(self, week: int) -> str:
        """Create a prompt for screening information"""
        return f"""
        Provide prenatal screening information for pregnancy week {week}.
        
        Respond with a JSON object containing:
        - "recommended_tests": List of recommended screening tests
        - "test_descriptions": List of descriptions for each test
        - "timing": When these tests should be performed
        - "importance": Why these tests are important
        """
    
    def _create_wellness_prompt(self, week: int) -> str:
        """Create a prompt for wellness tips"""
        return f"""
        Provide wellness and lifestyle tips for pregnancy week {week}.
        
        Respond with a JSON object containing:
        - "exercise_tips": List of safe exercise recommendations
        - "sleep_advice": List of sleep and rest tips
        - "stress_management": List of stress management techniques
        - "general_wellness": List of general wellness practices
        """
    
    def _create_nutrition_prompt(self, week: int) -> str:
        """Create a prompt for nutrition tips"""
        return f"""
        Provide nutrition guidance for pregnancy week {week}.
        
        Respond with a JSON object containing:
        - "essential_nutrients": List of key nutrients needed
        - "foods_to_avoid": List of foods to avoid or limit
        - "meal_suggestions": List of meal and snack ideas
        - "hydration_tips": List of hydration recommendations
        """
    
    def _parse_baby_size_response(self, response: str, week: int) -> BabySize:
        """Parse OpenAI response for baby size data"""
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                return BabySize(
                    size=data.get('size', f'Week {week} baby'),
                    weight=data.get('weight', 'Unknown'),
                    length=data.get('length', 'Unknown')
                )
        except Exception as e:
            print(f"Failed to parse baby size response: {e}")
        
        return self._get_fallback_baby_size(week)
    
    def _parse_symptoms_response(self, response: str) -> SymptomInfo:
        """Parse OpenAI response for symptoms data"""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                return SymptomInfo(
                    common_symptoms=data.get('common_symptoms', []),
                    when_to_call_doctor=data.get('when_to_call_doctor', []),
                    relief_tips=data.get('relief_tips', []),
                    severity_level=data.get('severity_level', 'mild')
                )
        except Exception as e:
            print(f"Failed to parse symptoms response: {e}")
        
        return self._get_fallback_symptoms(1)
    
    def _parse_screening_response(self, response: str) -> ScreeningInfo:
        """Parse OpenAI response for screening data"""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                return ScreeningInfo(
                    recommended_tests=data.get('recommended_tests', []),
                    test_descriptions=data.get('test_descriptions', []),
                    timing=data.get('timing', 'As recommended by healthcare provider'),
                    importance=data.get('importance', 'Important for monitoring pregnancy health')
                )
        except Exception as e:
            print(f"Failed to parse screening response: {e}")
        
        return self._get_fallback_screening(1)
    
    def _parse_wellness_response(self, response: str) -> WellnessInfo:
        """Parse OpenAI response for wellness data"""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                return WellnessInfo(
                    exercise_tips=data.get('exercise_tips', []),
                    sleep_advice=data.get('sleep_advice', []),
                    stress_management=data.get('stress_management', []),
                    general_wellness=data.get('general_wellness', [])
                )
        except Exception as e:
            print(f"Failed to parse wellness response: {e}")
        
        return self._get_fallback_wellness(1)
    
    def _parse_nutrition_response(self, response: str) -> NutritionInfo:
        """Parse OpenAI response for nutrition data"""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                return NutritionInfo(
                    essential_nutrients=data.get('essential_nutrients', []),
                    foods_to_avoid=data.get('foods_to_avoid', []),
                    meal_suggestions=data.get('meal_suggestions', []),
                    hydration_tips=data.get('hydration_tips', [])
                )
        except Exception as e:
            print(f"Failed to parse nutrition response: {e}")
        
        return self._get_fallback_nutrition(1)
    
    def _get_fallback_baby_size(self, week: int) -> BabySize:
        """Fallback baby size data when OpenAI fails"""
        fallback_sizes = {
            1: BabySize(size="Poppy seed", weight="0.1g", length="0.1cm"),
            10: BabySize(size="Kumquat", weight="4g", length="3.1cm"),
            20: BabySize(size="Banana", weight="300g", length="16.4cm"),
            30: BabySize(size="Cabbage", weight="1.3kg", length="39.9cm"),
            40: BabySize(size="Watermelon", weight="3.4kg", length="51.2cm")
        }
        
        # Find closest week
        for w in sorted(fallback_sizes.keys()):
            if week <= w:
                return fallback_sizes[w]
        
        return fallback_sizes[40]
    
    def _get_fallback_symptoms(self, week: int) -> SymptomInfo:
        """Fallback symptoms data"""
        return SymptomInfo(
            common_symptoms=["Nausea", "Fatigue", "Breast tenderness"],
            when_to_call_doctor=["Severe nausea", "Heavy bleeding", "Severe pain"],
            relief_tips=["Eat small meals", "Stay hydrated", "Get plenty of rest"],
            severity_level="mild"
        )
    
    def _get_fallback_screening(self, week: int) -> ScreeningInfo:
        """Fallback screening data"""
        return ScreeningInfo(
            recommended_tests=["Blood work", "Ultrasound"],
            test_descriptions=["Basic blood tests", "First trimester screening"],
            timing="As recommended by healthcare provider",
            importance="Important for monitoring pregnancy health"
        )
    
    def _get_fallback_wellness(self, week: int) -> WellnessInfo:
        """Fallback wellness data"""
        return WellnessInfo(
            exercise_tips=["Walking", "Prenatal yoga", "Swimming"],
            sleep_advice=["Sleep on side", "Use pregnancy pillow", "Maintain regular schedule"],
            stress_management=["Meditation", "Deep breathing", "Gentle exercise"],
            general_wellness=["Stay hydrated", "Eat balanced meals", "Take prenatal vitamins"]
        )
    
    def _get_fallback_nutrition(self, week: int) -> NutritionInfo:
        """Fallback nutrition data"""
        return NutritionInfo(
            essential_nutrients=["Folic acid", "Iron", "Calcium", "Protein"],
            foods_to_avoid=["Raw fish", "Unpasteurized cheese", "Excessive caffeine"],
            meal_suggestions=["Balanced breakfast", "Protein-rich snacks", "Colorful vegetables"],
            hydration_tips=["Drink 8-10 glasses of water", "Limit caffeine", "Include hydrating foods"]
        )
