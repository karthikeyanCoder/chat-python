import openai
import json
import asyncio
import os
from typing import Dict, Optional
from .pregnancy_models import BabySize, SymptomInfo, ScreeningInfo, WellnessInfo, NutritionInfo

class OpenAIBabySizeService:
    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OpenAI API key is required. Please set OPENAI_API_KEY in your environment variables.")
        
        try:
            self.client = openai.OpenAI(api_key=openai_api_key)
            self.model = os.getenv("OPENAI_MODEL", "gpt-4")
            self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1500"))
        except Exception as e:
            print(f"[WARN] OpenAI client initialization failed: {e}")
            self.client = None
    
    async def get_baby_size_for_week(self, week: int) -> BabySize:
        """
        Get baby size information for a specific pregnancy week using OpenAI
        
        Args:
            week: Pregnancy week (1-40)
            
        Returns:
            BabySize object with size, weight, and length information
        """
        try:
            prompt = self._create_baby_size_prompt(week)
            
            response = await self._call_openai(prompt)
            baby_size_data = self._parse_baby_size_response(response, week)
            
            return baby_size_data
            
        except Exception as e:
            # Fallback to static data if OpenAI fails
            return self._get_fallback_baby_size(week)
    
    def _create_baby_size_prompt(self, week: int) -> str:
        """Create a prompt for OpenAI to get baby size information"""
        return f"""
        Provide detailed baby size information for pregnancy week {week}. 
        
        Please respond with a JSON object containing:
        - "size": A relatable size comparison (e.g., "Lima bean", "Blueberry", "Coconut", "Avocado")
        - "weight": Weight in grams (e.g., "0.1g", "1.2g", "15g")
        - "length": Length in centimeters (e.g., "0.1cm", "0.5cm", "2.5cm")
        
        Make the size comparison creative and memorable. For example:
        - Week 1-4: Very small seeds (poppy seed, sesame seed)
        - Week 5-8: Small fruits (blueberry, raspberry, grape)
        - Week 9-12: Medium fruits (strawberry, lime, plum)
        - Week 13-16: Larger fruits (lemon, avocado, orange)
        - Week 17-20: Small vegetables (potato, sweet potato)
        - Week 21-24: Medium vegetables (carrot, corn cob)
        - Week 25-28: Large fruits (coconut, cantaloupe)
        - Week 29-32: Small melons (honeydew, small watermelon)
        - Week 33-36: Medium melons (cantaloupe, large watermelon)
        - Week 37-40: Full-term baby size
        
        Respond only with valid JSON, no additional text.
        """
    
    async def _call_openai(self, prompt: str) -> str:
        """Make an async call to OpenAI API"""
        if not self.client:
            raise Exception("OpenAI client not initialized")
            
        loop = asyncio.get_event_loop()
        
        def _call():
            return self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a medical AI assistant specializing in pregnancy development. Provide accurate, helpful information about fetal development and baby sizes."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.7
            )
        
        response = await loop.run_in_executor(None, _call)
        return response.choices[0].message.content.strip()
    
    def _parse_baby_size_response(self, response: str, week: int) -> BabySize:
        """Parse OpenAI response into BabySize object"""
        try:
            # Clean the response to extract JSON
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            
            data = json.loads(response)
            
            return BabySize(
                size=data.get("size", f"Week {week} baby"),
                weight=data.get("weight", "Unknown"),
                length=data.get("length", "Unknown")
            )
            
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback if parsing fails
            return self._get_fallback_baby_size(week)
    
    def _get_fallback_baby_size(self, week: int) -> BabySize:
        """Fallback baby size data if OpenAI fails"""
        fallback_sizes = {
            1: BabySize(size="Poppy seed", weight="0.1g", length="0.1cm"),
            2: BabySize(size="Poppy seed", weight="0.1g", length="0.1cm"),
            3: BabySize(size="Poppy seed", weight="0.1g", length="0.1cm"),
            4: BabySize(size="Poppy seed", weight="0.1g", length="0.1cm"),
            5: BabySize(size="Sesame seed", weight="0.1g", length="0.1cm"),
            6: BabySize(size="Lentil", weight="0.1g", length="0.2cm"),
            7: BabySize(size="Blueberry", weight="0.1g", length="0.3cm"),
            8: BabySize(size="Raspberry", weight="0.1g", length="0.4cm"),
            9: BabySize(size="Grape", weight="0.1g", length="0.5cm"),
            10: BabySize(size="Coconut", weight="0.1g", length="0.6cm"),
            11: BabySize(size="Lime", weight="0.1g", length="0.7cm"),
            12: BabySize(size="Plum", weight="0.1g", length="0.8cm"),
            13: BabySize(size="Peach", weight="0.1g", length="0.9cm"),
            14: BabySize(size="Lemon", weight="0.1g", length="1.0cm"),
            15: BabySize(size="Apple", weight="0.1g", length="1.1cm"),
            16: BabySize(size="Avocado", weight="0.1g", length="1.2cm"),
            17: BabySize(size="Onion", weight="0.1g", length="1.3cm"),
            18: BabySize(size="Sweet potato", weight="0.1g", length="1.4cm"),
            19: BabySize(size="Mango", weight="0.1g", length="1.5cm"),
            20: BabySize(size="Banana", weight="0.1g", length="1.6cm"),
            21: BabySize(size="Carrot", weight="0.1g", length="1.7cm"),
            22: BabySize(size="Corn cob", weight="0.1g", length="1.8cm"),
            23: BabySize(size="Grapefruit", weight="0.1g", length="1.9cm"),
            24: BabySize(size="Cantaloupe", weight="0.1g", length="2.0cm"),
            25: BabySize(size="Cauliflower", weight="0.1g", length="2.1cm"),
            26: BabySize(size="Butternut squash", weight="0.1g", length="2.2cm"),
            27: BabySize(size="Head of lettuce", weight="0.1g", length="2.3cm"),
            28: BabySize(size="Eggplant", weight="0.1g", length="2.4cm"),
            29: BabySize(size="Butternut squash", weight="0.1g", length="2.5cm"),
            30: BabySize(size="Cabbage", weight="0.1g", length="2.6cm"),
            31: BabySize(size="Coconut", weight="0.1g", length="2.7cm"),
            32: BabySize(size="Jicama", weight="0.1g", length="2.8cm"),
            33: BabySize(size="Pineapple", weight="0.1g", length="2.9cm"),
            34: BabySize(size="Cantaloupe", weight="0.1g", length="3.0cm"),
            35: BabySize(size="Honeydew melon", weight="0.1g", length="3.1cm"),
            36: BabySize(size="Romaine lettuce", weight="0.1g", length="3.2cm"),
            37: BabySize(size="Swiss chard", weight="0.1g", length="3.3cm"),
            38: BabySize(size="Leek", weight="0.1g", length="3.4cm"),
            39: BabySize(size="Mini watermelon", weight="0.1g", length="3.5cm"),
            40: BabySize(size="Small pumpkin", weight="0.1g", length="3.6cm")
        }
        
        return fallback_sizes.get(week, BabySize(size=f"Week {week} baby", weight="Unknown", length="Unknown"))
    
    async def get_detailed_baby_info(self, week: int) -> Dict:
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
            return json.loads(response)
            
        except Exception as e:
            return {
                "size": f"Week {week} baby",
                "weight": "Unknown",
                "length": "Unknown",
                "fun_fact": "Your baby is growing every day!",
                "comparison": "Growing steadily",
                "development_highlight": "Continuous development"
            }
    
    async def get_early_symptoms(self, week: int) -> SymptomInfo:
        """
        Get AI-generated early symptoms information for a specific week
        
        Args:
            week: Pregnancy week (1-40)
            
        Returns:
            SymptomInfo with symptoms, relief tips, and when to call doctor
        """
        try:
            prompt = f"""
            Provide detailed early pregnancy symptoms information for week {week}.
            
            Please respond with a JSON object containing:
            - "common_symptoms": Array of 5-8 common symptoms for this week
            - "when_to_call_doctor": Array of 3-5 warning signs that require medical attention
            - "relief_tips": Array of 5-7 practical tips to manage symptoms
            - "severity_level": String describing typical severity (e.g., "Mild", "Moderate", "Severe")
            
            Make it specific to week {week} and trimester. Be helpful and reassuring.
            Respond only with valid JSON, no additional text.
            """
            
            response = await self._call_openai(prompt)
            data = json.loads(response)
            
            return SymptomInfo(
                common_symptoms=data.get("common_symptoms", []),
                when_to_call_doctor=data.get("when_to_call_doctor", []),
                relief_tips=data.get("relief_tips", []),
                severity_level=data.get("severity_level", "Mild")
            )
            
        except Exception as e:
            return self._get_fallback_symptoms(week)
    
    async def get_prenatal_screening(self, week: int) -> ScreeningInfo:
        """
        Get AI-generated prenatal screening information for a specific week
        
        Args:
            week: Pregnancy week (1-40)
            
        Returns:
            ScreeningInfo with recommended tests and timing
        """
        try:
            prompt = f"""
            Provide detailed prenatal screening information for pregnancy week {week}.
            
            Please respond with a JSON object containing:
            - "recommended_tests": Array of 3-6 tests recommended for this week
            - "test_descriptions": Array of brief descriptions for each test
            - "timing": String describing when these tests should be done
            - "importance": String explaining why these tests are important
            
            Focus on tests that are typically done around week {week}.
            Be informative and reassuring about the importance of prenatal care.
            Respond only with valid JSON, no additional text.
            """
            
            response = await self._call_openai(prompt)
            data = json.loads(response)
            
            return ScreeningInfo(
                recommended_tests=data.get("recommended_tests", []),
                test_descriptions=data.get("test_descriptions", []),
                timing=data.get("timing", "As recommended by your doctor"),
                importance=data.get("importance", "Important for monitoring baby's health")
            )
            
        except Exception as e:
            return self._get_fallback_screening(week)
    
    async def get_wellness_tips(self, week: int) -> WellnessInfo:
        """
        Get AI-generated wellness tips for a specific week
        
        Args:
            week: Pregnancy week (1-40)
            
        Returns:
            WellnessInfo with exercise, sleep, and stress management tips
        """
        try:
            prompt = f"""
            Provide detailed wellness tips for pregnancy week {week}.
            
            Please respond with a JSON object containing:
            - "exercise_tips": Array of 4-6 safe exercise recommendations for this week
            - "sleep_advice": Array of 3-5 sleep tips specific to this week
            - "stress_management": Array of 4-6 stress relief techniques
            - "general_wellness": Array of 4-6 general wellness practices
            
            Make it specific to week {week} and trimester. Focus on safety and comfort.
            Respond only with valid JSON, no additional text.
            """
            
            response = await self._call_openai(prompt)
            data = json.loads(response)
            
            return WellnessInfo(
                exercise_tips=data.get("exercise_tips", []),
                sleep_advice=data.get("sleep_advice", []),
                stress_management=data.get("stress_management", []),
                general_wellness=data.get("general_wellness", [])
            )
            
        except Exception as e:
            return self._get_fallback_wellness(week)
    
    async def get_nutrition_tips(self, week: int) -> NutritionInfo:
        """
        Get AI-generated nutrition tips for a specific week
        
        Args:
            week: Pregnancy week (1-40)
            
        Returns:
            NutritionInfo with nutrition advice and meal suggestions
        """
        try:
            prompt = f"""
            Provide detailed nutrition tips for pregnancy week {week}.
            
            Please respond with a JSON object containing:
            - "essential_nutrients": Array of 5-7 key nutrients needed this week
            - "foods_to_avoid": Array of 4-6 foods to avoid or limit
            - "meal_suggestions": Array of 4-6 meal ideas for this week
            - "hydration_tips": Array of 3-5 hydration recommendations
            
            Make it specific to week {week} and trimester. Focus on baby's development needs.
            Respond only with valid JSON, no additional text.
            """
            
            response = await self._call_openai(prompt)
            data = json.loads(response)
            
            return NutritionInfo(
                essential_nutrients=data.get("essential_nutrients", []),
                foods_to_avoid=data.get("foods_to_avoid", []),
                meal_suggestions=data.get("meal_suggestions", []),
                hydration_tips=data.get("hydration_tips", [])
            )
            
        except Exception as e:
            return self._get_fallback_nutrition(week)
    
    def _get_fallback_symptoms(self, week: int) -> SymptomInfo:
        """Fallback symptoms data if OpenAI fails"""
        return SymptomInfo(
            common_symptoms=["Morning sickness", "Fatigue", "Breast tenderness", "Mood swings"],
            when_to_call_doctor=["Severe nausea", "Bleeding", "Severe abdominal pain", "High fever"],
            relief_tips=["Eat small meals", "Stay hydrated", "Get plenty of rest", "Avoid triggers"],
            severity_level="Mild to Moderate"
        )
    
    def _get_fallback_screening(self, week: int) -> ScreeningInfo:
        """Fallback screening data if OpenAI fails"""
        return ScreeningInfo(
            recommended_tests=["Blood tests", "Urine tests", "Ultrasound"],
            test_descriptions=["Check hormone levels", "Monitor protein and glucose", "Visualize baby development"],
            timing="As recommended by your healthcare provider",
            importance="Essential for monitoring baby's health and development"
        )
    
    def _get_fallback_wellness(self, week: int) -> WellnessInfo:
        """Fallback wellness data if OpenAI fails"""
        return WellnessInfo(
            exercise_tips=["Walking", "Prenatal yoga", "Swimming", "Light stretching"],
            sleep_advice=["Sleep on your side", "Use pregnancy pillows", "Maintain regular sleep schedule"],
            stress_management=["Deep breathing", "Meditation", "Gentle exercise", "Talk to loved ones"],
            general_wellness=["Stay hydrated", "Eat balanced meals", "Take prenatal vitamins", "Attend appointments"]
        )
    
    def _get_fallback_nutrition(self, week: int) -> NutritionInfo:
        """Fallback nutrition data if OpenAI fails"""
        return NutritionInfo(
            essential_nutrients=["Folic acid", "Iron", "Calcium", "Protein", "Omega-3"],
            foods_to_avoid=["Raw fish", "Unpasteurized dairy", "Excess caffeine", "Alcohol"],
            meal_suggestions=["Balanced breakfast", "Colorful salads", "Lean proteins", "Whole grains"],
            hydration_tips=["Drink 8-10 glasses daily", "Include herbal teas", "Eat water-rich foods"]
        )
