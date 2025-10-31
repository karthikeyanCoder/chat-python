#!/usr/bin/env python3
"""
Mental Health Service for Patient Alert System
Direct integration of Mental Health module
"""

import os
import random
import json
import requests
import io
from datetime import datetime
from typing import List, Dict, Any, Optional
import openai
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

class MentalHealthService:
    """Mental Health Service for story generation and assessment"""
    
    def __init__(self):
        """Initialize the Mental Health Service"""
        self.openai_client = None
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        
        # Initialize database connection (use same as main app)
        try:
            mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
            db_name = os.getenv("DB_NAME", "patients_db")
            self.mongo_client = MongoClient(mongo_uri)
            self.db = self.mongo_client[db_name]
            self.mental_health_collection = self.db.mental_health_assessments
            print(f"[OK] Mental Health Service: Database connected successfully to {mongo_uri}/{db_name}")
            print(f"[OK] Mental Health Service: Collection: mental_health_assessments")
        except Exception as e:
            print(f"[ERROR] Mental Health Service: Database connection failed: {e}")
            self.mongo_client = None
            self.db = None
            self.mental_health_collection = None
        
        # Initialize OpenAI client
        try:
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if openai_api_key and openai_api_key != "your_openai_api_key_here":
                self.openai_client = openai.OpenAI(api_key=openai_api_key)
                print("[OK] Mental Health OpenAI client initialized")
            else:
                print("[WARN] OpenAI API key not found, using fallback mode")
        except Exception as e:
            print(f"[WARN] OpenAI initialization failed: {e}")
        
        # Story templates for different scenarios
        self.story_templates = {
            "pregnancy": [
                "ஒரு சிறிய கிராமத்தில் வாழும் பெண் சமூக பிரச்சினைகளை சமாளிக்கும் கதை",
                "ஒரு பெண் தனது குடும்பத்துடன் ஒற்றுமையை வளர்க்கும் கதை",
                "ஒரு பெண் தனது பயத்தை வென்று தைரியம் பெறும் கதை",
                "ஒரு பெண் சமூகத்தில் மாற்றத்தை கொண்டு வரும் கதை",
                "ஒரு பெண் தனது கனவுகளை நிறைவேற்றும் கதை",
                "ஒரு பெண் குடும்பத்தின் ஆதரவுடன் சவால்களை சமாளிக்கும் கதை",
                "ஒரு பெண் சமூக ஒற்றுமையை வளர்க்கும் கதை"
            ],
            "postpartum": [
                "புதிய தாய் தூக்கம் இழப்பு மற்றும் அதிகமான பொறுப்புகளை சமாளிக்கும் கதை",
                "புதிய தாய் குழந்தையுடனான தொடர்பு இழப்பு மற்றும் திறமை கேள்விகள் பற்றிய கதை",
                "புதிய தாய் சமூக தனிமை மற்றும் அடையாள இழப்பு பற்றிய கதை",
                "புதிய தாய் குழந்தை ஆரோக்கியம் மற்றும் வளர்ச்சி பற்றிய கவலை பற்றிய கதை",
                "புதிய தாய் கணவர் உறவு மாற்றங்கள் மற்றும் ஆதரவு தேவைகள் பற்றிய கதை"
            ],
            "general": [
                "வேலை-வாழ்க்கை சமநிலை மற்றும் அழுத்த மேலாண்மை பற்றிய கதை",
                "சமூக பயம் மற்றும் உறவு கட்டமைத்தல் பற்றிய கதை",
                "துயரம் மற்றும் இழப்பு அனுபவிக்கும் கதை",
                "நிதி அழுத்தம் மற்றும் எதிர்கால நிச்சயமற்ற தன்மை பற்றிய கதை",
                "சுய மதிப்பு மற்றும் தனிப்பட்ட வளர்ச்சி பற்றிய கதை"
            ]
        }
        
        # Complete story templates for pregnancy mental health
        self.complete_stories = [
            {
                "title": "ஒற்றுமையின் வலிமை",
                "content": "மீனா ஒரு சிறிய கிராமத்தில் வாழ்ந்தாள். அவளுக்கு மிகவும் கவலை மற்றும் பயம். \"நான் எப்படி இந்த சவால்களை சமாளிப்பேன்?\" என்று எப்போதும் சிந்திக்கிறாள். ஒரு நாள், அவளது கிராமத்தில் பெரிய பிரச்சினை வந்தது. அனைவரும் தனித்தனியாக சமாளிக்க முயற்சித்தனர், ஆனால் எதுவும் நடக்கவில்லை. அப்போது மீனா உணர்ந்தாள் - தனிமையில் பயம், ஆனால் ஒற்றுமையில் வலிமை! அவள் அனைவரையும் ஒன்றாக சேர்த்தாள். \"நாம் ஒன்றாக இருந்தால் எந்த பிரச்சினையையும் தீர்க்க முடியும்\" என்று கூறினாள். கிராமத்தார் அனைவரும் ஒன்றாக சேர்ந்து பிரச்சினையை தீர்த்தனர். அப்போது மீனா உணர்ந்தாள் - குடும்பம் மற்றும் சமூகத்தின் ஆதரவு எந்த பிரச்சினையையும் தீர்க்க முடியும். ஒற்றுமையில் மிகப்பெரிய வலிமை இருக்கிறது. இதிலிருந்து நாம் கற்றுக்கொள்ளும் பாடம்: \"ஒற்றுமை வலிமை\" - நாம் ஒன்றாக இருந்தால் எந்த சவாலையும் சமாளிக்க முடியும்."
            },
            {
                "title": "பொறுமையின் வலிமை",
                "content": "கல்யாணி ஒரு சிறிய கிராமத்தில் வாழ்ந்தாள். அவளுக்கு மிகவும் கோபம் மற்றும் எரிச்சல். \"எல்லாம் எனக்கு எதிராகவே இருக்கிறது\" என்று எப்போதும் சிந்திக்கிறாள். ஒரு நாள், அவளது கிராமத்தில் பெரிய பிரச்சினை வந்தது. அனைவரும் கோபமாகவும் எரிச்சலாகவும் இருந்தனர். அப்போது கல்யாணி உணர்ந்தாள் - கோபத்தில் பிரச்சினை, ஆனால் பொறுமையில் தீர்வு! அவள் அனைவரையும் அமைதியாக இருக்கச் செய்தாள். \"பொறுமையுடன் சிந்தித்தால் எந்த பிரச்சினையையும் தீர்க்க முடியும்\" என்று கூறினாள். கிராமத்தார் அனைவரும் பொறுமையுடன் சிந்தித்து பிரச்சினையை தீர்த்தனர். அப்போது கல்யாணி உணர்ந்தாள் - பொறுமை எந்த பிரச்சினையையும் தீர்க்க முடியும். பொறுமையில் மிகப்பெரிய வலிமை இருக்கிறது. இதிலிருந்து நாம் கற்றுக்கொள்ளும் பாடம்: \"பொறுமை அமைதி தரும்\" - பொறுமையுடன் சிந்தித்தால் எந்த சவாலையும் சமாளிக்க முடியும்."
            },
            {
                "title": "குடும்ப ஆதரவின் வலிமை",
                "content": "பிரியா ஒரு சிறிய கிராமத்தில் வாழ்ந்தாள். அவளுக்கு மிகவும் தனிமை மற்றும் கவலை. \"நான் யாருக்கும் தேவையில்லை\" என்று எப்போதும் சிந்திக்கிறாள். ஒரு நாள், அவளது கிராமத்தில் பெரிய பிரச்சினை வந்தது. அனைவரும் தனித்தனியாக சமாளிக்க முயற்சித்தனர், ஆனால் எதுவும் நடக்கவில்லை. அப்போது பிரியா உணர்ந்தாள் - தனிமையில் பயம், ஆனால் குடும்ப ஆதரவில் வலிமை! அவள் தனது குடும்பத்திடம் ஆதரவு கேட்டாள். \"நாம் ஒன்றாக இருந்தால் எந்த பிரச்சினையையும் தீர்க்க முடியும்\" என்று கூறினாள். குடும்பம் அனைவரும் ஒன்றாக சேர்ந்து பிரச்சினையை தீர்த்தனர். அப்போது பிரியா உணர்ந்தாள் - குடும்ப ஆதரவு எந்த பிரச்சினையையும் தீர்க்க முடியும். குடும்ப ஆதரவில் மிகப்பெரிய வலிமை இருக்கிறது. இதிலிருந்து நாம் கற்றுக்கொள்ளும் பாடம்: \"குடும்ப ஆதரவு எல்லாம்\" - குடும்பம் ஒன்றாக இருந்தால் எந்த சவாலையும் சமாளிக்க முடியும்."
            },
            {
                "title": "நம்பிக்கையின் வலிமை",
                "content": "ரேகா ஒரு சிறிய கிராமத்தில் வாழ்ந்தாள். அவளுக்கு மிகவும் பயம் மற்றும் நம்பிக்கை இழப்பு. \"எதுவும் நடக்காது\" என்று எப்போதும் சிந்திக்கிறாள். ஒரு நாள், அவளது கிராமத்தில் பெரிய பிரச்சினை வந்தது. அனைவரும் பயமாகவும் நம்பிக்கை இழந்தவர்களாகவும் இருந்தனர். அப்போது ரேகா உணர்ந்தாள் - பயத்தில் தோல்வி, ஆனால் நம்பிக்கையில் வெற்றி! அவள் அனைவருக்கும் நம்பிக்கை அளித்தாள். \"நம்பிக்கையுடன் முயற்சித்தால் எந்த பிரச்சினையையும் தீர்க்க முடியும்\" என்று கூறினாள். கிராமத்தார் அனைவரும் நம்பிக்கையுடன் முயற்சித்து பிரச்சினையை தீர்த்தனர். அப்போது ரேகா உணர்ந்தாள் - நம்பிக்கை எந்த பிரச்சினையையும் தீர்க்க முடியும். நம்பிக்கையில் மிகப்பெரிய வலிமை இருக்கிறது. இதிலிருந்து நாம் கற்றுக்கொள்ளும் பாடம்: \"நம்பிக்கை பயத்தை வெல்கிறது\" - நம்பிக்கையுடன் முயற்சித்தால் எந்த சவாலையும் சமாளிக்க முடியும்."
            },
            {
                "title": "தைரியத்தின் வலிமை",
                "content": "சுமதி ஒரு சிறிய கிராமத்தில் வாழ்ந்தாள். அவளுக்கு மிகவும் பயம் மற்றும் தைரியம் இழப்பு. \"நான் எதுவும் செய்ய முடியாது\" என்று எப்போதும் சிந்திக்கிறாள். ஒரு நாள், அவளது கிராமத்தில் பெரிய பிரச்சினை வந்தது. அனைவரும் பயமாகவும் தைரியம் இழந்தவர்களாகவும் இருந்தனர். அப்போது சுமதி உணர்ந்தாள் - பயத்தில் தோல்வி, ஆனால் தைரியத்தில் வெற்றி! அவள் அனைவருக்கும் தைரியம் அளித்தாள். \"தைரியத்துடன் முயற்சித்தால் எந்த பிரச்சினையையும் தீர்க்க முடியும்\" என்று கூறினாள். கிராமத்தார் அனைவரும் தைரியத்துடன் முயற்சித்து பிரச்சினையை தீர்த்தனர். அப்போது சுமதி உணர்ந்தாள் - தைரியம் எந்த பிரச்சினையையும் தீர்க்க முடியும். தைரியத்தில் மிகப்பெரிய வலிமை இருக்கிறது. இதிலிருந்து நாம் கற்றுக்கொள்ளும் பாடம்: \"தைரியம் சவால்களில் வளர்கிறது\" - தைரியத்துடன் முயற்சித்தால் எந்த சவாலையும் சமாளிக்க முடியும்."
            }
        ]
        
        # Question templates in Tamil
        self.question_templates = [
            {
                "question": "{character_name} இப்போது எப்படி உணருகிறார் என்று நினைக்கிறீர்கள்?",
                "options": [
                    "மிகவும் அழுத்தமாகவும் கவலையாகவும்",
                    "வருத்தமாகவும் மனச்சோர்வாகவும்",
                    "இந்த சூழ்நிலைக்கு சாதாரண உணர்வுகள்",
                    "உற்சாகமாகவும் நம்பிக்கையாகவும்"
                ]
            },
            {
                "question": "நீங்கள் {character_name} நிலையில் இருந்தால் என்ன செய்வீர்கள்?",
                "options": [
                    "தொழில்முறை உதவி அல்லது ஆலோசனை தேடுவேன்",
                    "தனியாக சமாளிக்க முயற்சிப்பேன்",
                    "குடும்பம் மற்றும் நண்பர்களிடம் ஆதரவு கேட்பேன்",
                    "ஓய்வு எடுத்து சுய பராமரிப்பில் கவனம் செலுத்துவேன்"
                ]
            },
            {
                "question": "{character_name} உணர்வுகள் சாதாரணமானவை என்று நினைக்கிறீர்களா?",
                "options": [
                    "ஆம், முற்றிலும் சாதாரணம்",
                    "ஓரளவு சாதாரணம்",
                    "மிகவும் சாதாரணமல்ல",
                    "சாதாரணமல்ல"
                ]
            },
            {
                "question": "{character_name}க்கு என்ன ஆலோசனை தருவீர்கள்?",
                "options": [
                    "தொழில்முறை மன ஆரோக்கிய ஆதரவு தேடுங்கள்",
                    "ஓய்வு மற்றும் மனநிலை நுட்பங்களை முயற்சிக்கவும்",
                    "நம்பகமான நண்பர்கள் அல்லது குடும்பத்துடன் பேசுங்கள்",
                    "காத்திருங்கள், இயற்கையாக கடந்துவிடும்"
                ]
            },
            {
                "question": "உங்கள் வாழ்க்கையில் இதேபோன்ற உணர்வுகளை அனுபவித்திருக்கிறீர்களா?",
                "options": [
                    "ஆம், மிகவும் ஒத்த அனுபவங்கள்",
                    "ஓரளவு ஒத்த அனுபவங்கள்",
                    "கொஞ்சம் ஒத்தவை",
                    "ஒத்தவை இல்லை"
                ]
            }
        ]
        
        print("[OK] Mental Health Service initialized successfully")
    
    def generate_story(self, story_type: str = "pregnancy", scenario: str = "pregnancy_mental_health") -> Dict[str, Any]:
        """Generate a mental health assessment story"""
        try:
            if scenario == "pregnancy_mental_health":
                # Use complete story templates
                selected_story = random.choice(self.complete_stories)
                
                # Generate questions based on the story
                questions = [
                    {
                        "question": f"{selected_story['title']} கதையில் முக்கிய பாத்திரம் யார்?",
                        "options": ["மீனா", "கல்யாணி", "பிரியா", "ரேகா", "சுமதி"],
                        "correct_answer": 0
                    },
                    {
                        "question": "கதையில் முக்கிய பிரச்சினை என்ன?",
                        "options": [
                            "கிராமத்தில் பெரிய பிரச்சினை", 
                            "தனிமை மற்றும் கவலை", 
                            "கோபம் மற்றும் எரிச்சல்", 
                            "பயம் மற்றும் நம்பிக்கை இழப்பு"
                        ],
                        "correct_answer": 0
                    },
                    {
                        "question": "கதையின் முக்கிய பாடம் என்ன?",
                        "options": [
                            "ஒற்றுமை வலிமை", 
                            "பொறுமை அமைதி தரும்", 
                            "குடும்ப ஆதரவு எல்லாம்", 
                            "நம்பிக்கை பயத்தை வெல்கிறது"
                        ],
                        "correct_answer": 0
                    },
                    {
                        "question": "கதையில் பிரச்சினை எப்படி தீர்ந்தது?",
                        "options": [
                            "ஒன்றாக சேர்ந்து தீர்த்தனர்", 
                            "தனித்தனியாக சமாளித்தனர்", 
                            "மருத்துவரின் உதவியுடன்", 
                            "அரசாங்க உதவியுடன்"
                        ],
                        "correct_answer": 0
                    },
                    {
                        "question": "நீங்கள் இதே நிலையில் இருந்தால் என்ன செய்வீர்கள்?",
                        "options": [
                            "குடும்பத்திடம் ஆதரவு கேட்பேன்", 
                            "தனியாக சமாளிக்க முயற்சிப்பேன்", 
                            "மருத்துவரை அணுகுவேன்", 
                            "ஓய்வு எடுத்து சிந்திப்பேன்"
                        ],
                        "correct_answer": 0
                    }
                ]
                
                return {
                    "story_id": f"story_{random.randint(1000, 9999)}",
                    "title": selected_story['title'],
                    "content": selected_story['content'],
                    "questions": questions,
                    "character_name": "மீனா",
                    "scenario": scenario,
                    "success": True
                }
            else:
                # Use OpenAI for other scenarios
                if not self.openai_client:
                    return self._get_fallback_story()
                
                scenarios = self.story_templates.get(story_type, self.story_templates["general"])
                selected_scenario = random.choice(scenarios)
                
                prompt = f"""
                Create a complete, meaningful story in Tamil about: {selected_scenario}
                
                Story Structure:
                1. BEGINNING: Introduce a pregnant woman character facing challenges
                2. MIDDLE: Show her struggles, emotions, and family dynamics
                3. END: Resolve with support and teach a moral lesson
                
                Requirements:
                - Write in Tamil language (தமிழில் எழுதுங்கள்)
                - Character name: Use a Tamil name like மீனா, கல்யாணி, பிரியா, etc.
                - Keep it between 200-300 words (detailed but focused)
                - Use warm, understanding tone
                - Include specific pregnancy concerns (fear, family pressure, body changes, future worries)
                - Show character's emotional journey and growth
                - Include family support, community help, or personal strength
                - End with clear moral lesson using phrase "இதிலிருந்து நாம் கற்றுக்கொள்ளும் பாடம்: [lesson]"
                
                Moral Lesson Examples:
                - "ஒற்றுமை வலிமை" (Unity is Strength)
                - "பொறுமை அமைதி தரும்" (Patience brings Peace)
                - "குடும்ப ஆதரவு எல்லாம்" (Family Support is Everything)
                - "நம்பிக்கை பயத்தை வெல்கிறது" (Hope conquers Fear)
                - "காதல் எல்லாவற்றையும் வெல்கிறது" (Love overcomes All)
                - "தைரியம் சவால்களில் வளர்கிறது" (Courage grows with Challenges)
                
                Make it a complete story that teaches a valuable life lesson while helping assess mental health.
                """
                
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a compassionate mental health counselor who creates engaging stories for assessment purposes."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=300,
                    temperature=0.8
                )
                
                story_content = response.choices[0].message.content.strip()
                
                # Generate character name (Tamil names)
                character_names = ["பிரியா", "கவிதா", "மாலதி", "ரேகா", "சுமதி", "விஜயா", "லட்சுமி", "காந்தி", "சரோஜா", "ராஜேஸ்வரி"]
                character_name = random.choice(character_names)
                
                # Generate story ID
                story_id = f"story_{random.randint(1000, 9999)}"
                
                # Generate title in Tamil
                title_prompt = f"Create a short, engaging title in Tamil (3-5 words) for this pregnancy story: {story_content[:100]}..."
                title_response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": title_prompt}
                    ],
                    max_tokens=20,
                    temperature=0.7
                )
                title = title_response.choices[0].message.content.strip().replace('"', '')
                
                # Prepare questions with character name
                questions = []
                for template in self.question_templates:
                    question = {
                        "question": template["question"].format(character_name=character_name),
                        "options": template["options"]
                    }
                    questions.append(question)
                
                return {
                    "story_id": story_id,
                    "title": title,
                    "content": story_content,
                    "questions": questions,
                    "character_name": character_name,
                    "scenario": selected_scenario,
                    "success": True
                }
                
        except Exception as e:
            print(f"Error generating story: {e}")
            return self._get_fallback_story()
    
    def _get_fallback_story(self) -> Dict[str, Any]:
        """Get fallback story when OpenAI is not available"""
        selected_story = random.choice(self.complete_stories)
        
        questions = [
            {
                "question": f"{selected_story['title']} கதையில் முக்கிய பாத்திரம் யார்?",
                "options": ["மீனா", "கல்யாணி", "பிரியா", "ரேகா", "சுமதி"],
                "correct_answer": 0
            },
            {
                "question": "கதையில் முக்கிய பிரச்சினை என்ன?",
                "options": [
                    "கிராமத்தில் பெரிய பிரச்சினை", 
                    "தனிமை மற்றும் கவலை", 
                    "கோபம் மற்றும் எரிச்சல்", 
                    "பயம் மற்றும் நம்பிக்கை இழப்பு"
                ],
                "correct_answer": 0
            },
            {
                "question": "கதையின் முக்கிய பாடம் என்ன?",
                "options": [
                    "ஒற்றுமை வலிமை", 
                    "பொறுமை அமைதி தரும்", 
                    "குடும்ப ஆதரவு எல்லாம்", 
                    "நம்பிக்கை பயத்தை வெல்கிறது"
                ],
                "correct_answer": 0
            },
            {
                "question": "கதையில் பிரச்சினை எப்படி தீர்ந்தது?",
                "options": [
                    "ஒன்றாக சேர்ந்து தீர்த்தனர்", 
                    "தனித்தனியாக சமாளித்தனர்", 
                    "மருத்துவரின் உதவியுடன்", 
                    "அரசாங்க உதவியுடன்"
                ],
                "correct_answer": 0
            },
            {
                "question": "நீங்கள் இதே நிலையில் இருந்தால் என்ன செய்வீர்கள்?",
                "options": [
                    "குடும்பத்திடம் ஆதரவு கேட்பேன்", 
                    "தனியாக சமாளிக்க முயற்சிப்பேன்", 
                    "மருத்துவரை அணுகுவேன்", 
                    "ஓய்வு எடுத்து சிந்திப்பேன்"
                ],
                "correct_answer": 0
            }
        ]
        
        return {
            "story_id": f"story_{random.randint(1000, 9999)}",
            "title": selected_story['title'],
            "content": selected_story['content'],
            "questions": questions,
            "character_name": "மீனா",
            "scenario": "pregnancy_mental_health",
            "success": True
        }
    
    def assess_mental_health(self, answers: List[str], story_id: str, patient_id: str = None) -> Dict[str, Any]:
        """Analyze the assessment answers and provide mental health insights"""
        try:
            print(f"[*] Mental Health Assessment - Received answers: {answers}")
            print(f"[*] Mental Health Assessment - Story ID: {story_id}")
            
            # Validate answers
            if not answers or len(answers) == 0:
                return {
                    "success": False,
                    "error": "No answers provided"
                }
            
            # Convert string answers to numeric scores
            # Map answer options to scores (0-4 scale)
            answer_scores = []
            for answer in answers:
                if answer in ['Very positive', 'Very well', 'Very high', 'Not at all', 'Very confident']:
                    answer_scores.append(4)
                elif answer in ['Positive', 'Well', 'High', 'Slightly', 'Confident']:
                    answer_scores.append(3)
                elif answer in ['Neutral', 'Okay', 'Moderate', 'Moderately', 'Somewhat confident']:
                    answer_scores.append(2)
                elif answer in ['Negative', 'Poorly', 'Low', 'Very', 'Not very confident']:
                    answer_scores.append(1)
                elif answer in ['Very negative', 'Very poorly', 'Very low', 'Extremely', 'Not confident at all']:
                    answer_scores.append(0)
                else:
                    # Default to neutral score for unknown answers
                    answer_scores.append(2)
            
            # Calculate basic score
            total_score = sum(answer_scores)
            max_score = len(answer_scores) * 4
            percentage = (total_score / max_score) * 100
            
            print(f"[*] Mental Health Assessment - Answer scores: {answer_scores}")
            print(f"[*] Mental Health Assessment - Total score: {total_score}, Max score: {max_score}, Percentage: {percentage}")
            
            # Determine risk level with more nuanced scoring
            if percentage <= 25:
                risk_level = "Low Risk"
                risk_class = "risk-low"
                color = "#28a745"
                confidence = 85
            elif percentage <= 50:
                risk_level = "Mild Risk"
                risk_class = "risk-mild"
                color = "#17a2b8"
                confidence = 80
            elif percentage <= 70:
                risk_level = "Medium Risk"
                risk_class = "risk-medium"
                color = "#ffc107"
                confidence = 75
            elif percentage <= 85:
                risk_level = "High Risk"
                risk_class = "risk-high"
                color = "#fd7e14"
                confidence = 80
            else:
                risk_level = "Very High Risk"
                risk_class = "risk-very-high"
                color = "#dc3545"
                confidence = 85
            
            # Generate comprehensive analysis using OpenAI
            detailed_analysis = self._generate_analysis(risk_level, percentage, answer_scores)
            
            # Generate specific recommendations
            recommendations = self._generate_recommendations(risk_level, percentage, answer_scores)
            
            # Generate action plan
            action_plan = self._generate_action_plan(risk_level, percentage)
            
            # Prepare assessment data
            assessment_data = {
                "success": True,
                "story_id": story_id,
                "total_score": total_score,
                "max_score": max_score,
                "percentage": round(percentage, 1),
                "risk_level": risk_level,
                "risk_class": risk_class,
                "color": color,
                "confidence": confidence,
                "detailed_analysis": detailed_analysis,
                "recommendations": recommendations,
                "action_plan": action_plan,
                "answers": answers,
                "timestamp": datetime.now().isoformat()
            }
            
            # Save to database if available
            try:
                if self.mental_health_collection is not None:
                    assessment_record = {
                        "patient_id": patient_id or "unknown_patient",
                        "type": "mental_health_assessment",
                        "story_id": story_id,
                        "answers": answers,
                        "assessment_result": assessment_data,
                        "created_at": datetime.now(),
                        "status": "completed"
                    }
                    result = self.mental_health_collection.insert_one(assessment_record)
                    print(f"[OK] Mental health assessment saved to database with ID: {result.inserted_id}")
                    print(f"[OK] Database: {self.db.name}, Collection: {self.mental_health_collection.name}")
                    print(f"[OK] Patient ID: {patient_id or 'unknown_patient'}")
                    
                    # Verify the data was saved by counting documents
                    count = self.mental_health_collection.count_documents({"patient_id": patient_id or "unknown_patient"})
                    print(f"[OK] Total assessments for this patient: {count}")
                else:
                    print("[WARN] Database not available, assessment not saved")
            except Exception as db_error:
                print(f"[ERROR] Database save error: {db_error}")
                # Don't fail the assessment if database save fails
            
            return assessment_data
            
        except Exception as e:
            print(f"Assessment error: {e}")
            return {
                "success": False,
                "error": f"Error assessing mental health: {str(e)}"
            }
    
    def _generate_analysis(self, risk_level: str, percentage: float, answers: List[int]) -> str:
        """Generate detailed analysis using OpenAI or fallback"""
        try:
            if not self.openai_client:
                return self._get_fallback_analysis(risk_level)
            
            analysis_prompt = f"""
            You are a specialized mental health counselor for pregnant women. Analyze these assessment responses:
            
            Answers: {answers}
            Total Score: {sum(answers)}/{len(answers) * 4} ({percentage:.1f}%)
            Risk Level: {risk_level}
            
            Provide a comprehensive analysis in Tamil language including:
            
            1. DETAILED ANALYSIS (2-3 sentences):
               - What these responses indicate about mental health during pregnancy
               - Specific concerns or strengths identified
               - Cultural context for Tamil-speaking pregnant women
            
            2. PERSONALIZED RECOMMENDATIONS (3-4 specific points):
               - Immediate coping strategies
               - When to seek professional help
               - Self-care practices for pregnancy
               - Family support suggestions
               - Cultural considerations
            
            3. PROFESSIONAL GUIDANCE (1-2 sentences):
               - Specific next steps for mental health support
               - Resources available in Tamil community
            
            Be warm, encouraging, culturally sensitive, and practical. Write in clear Tamil.
            Focus on pregnancy-specific mental health needs.
            """
            
            analysis_response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a compassionate, culturally-sensitive mental health counselor specializing in pregnancy mental health for Tamil-speaking women. Provide detailed, practical, and encouraging guidance."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return analysis_response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI analysis failed: {e}")
            return self._get_fallback_analysis(risk_level)
    
    def _get_fallback_analysis(self, risk_level: str) -> str:
        """Fallback analysis if OpenAI is unavailable"""
        if risk_level == "Low Risk":
            return """
            மிகவும் நன்று! உங்கள் பதில்கள் நல்ல மன ஆரோக்கிய விழிப்புணர்வு மற்றும் சமாளிப்பு உத்திகளைக் காட்டுகின்றன. 
            ஆரோக்கியமான பழக்கங்களைத் தொடர்ந்து பராமரிக்கவும், உங்கள் ஆதரவு வலையமைப்புடன் இணைந்திருங்கள், 
            மற்றும் வழக்கமான சுகாதார பராமரிப்பு நடைமுறைகளைத் தொடர்ந்து செய்யவும்.
            """
        elif risk_level == "Medium Risk":
            return """
            கூடுதல் ஆதரவைக் கருத்தில் கொள்ளுங்கள். உங்கள் உணர்வுகளைப் பற்றி உங்கள் சுகாதார பராமரிப்பாளருடன் பேசுங்கள், 
            ஆதரவு குழுவில் சேருவதைக் கருத்தில் கொள்ளுங்கள், அழுத்தம் குறைப்பு நுட்பங்களைப் பயிற்சி செய்யுங்கள், 
            மற்றும் வழக்கமான தூக்கம் மற்றும் உடற்பயிற்சி வழக்கங்களைப் பராமரிக்கவும்.
            """
        else:
            return """
            தயவுசெய்து ஆதரவைத் தேடுங்கள். உடனடியாக உங்கள் சுகாதார பராமரிப்பாளரைத் தொடர்பு கொள்ளுங்கள், 
            மன ஆரோக்கிய நிபுணருடன் பேசுவதைக் கருத்தில் கொள்ளுங்கள், நம்பகமான குடும்பம் மற்றும் நண்பர்களிடம் அணுகுங்கள், 
            மற்றும் தேவைப்பட்டால் நெருக்கடி ஆதரவு வளங்களைக் கருத்தில் கொள்ளுங்கள்.
            """
    
    def _generate_recommendations(self, risk_level: str, percentage: float, answers: List[int]) -> List[str]:
        """Generate specific recommendations based on risk level"""
        if risk_level == "Low Risk":
            return [
                "உங்கள் நேர்மறையான மனநிலையைத் தொடர்ந்து பராமரிக்கவும்",
                "வழக்கமான உடற்பயிற்சி மற்றும் சமநிலையான உணவு வழக்கத்தைத் தொடர்ந்து செய்யவும்",
                "குடும்பம் மற்றும் நண்பர்களுடன் நேர்மறையான உறவுகளை வளர்த்துக் கொள்ளுங்கள்",
                "மன அழுத்தத்தைக் குறைக்கும் நடவடிக்கைகளில் ஈடுபடுங்கள்"
            ]
        elif risk_level == "Mild Risk":
            return [
                "உங்கள் உணர்வுகளைப் பற்றி நம்பகமான நபருடன் பேசுங்கள்",
                "ஆழ்ந்த சுவாசம் மற்றும் தியானம் போன்ற அழுத்தம் குறைப்பு நுட்பங்களைப் பயிற்சி செய்யுங்கள்",
                "வழக்கமான சுகாதார பராமரிப்பு நடைமுறைகளைத் தொடர்ந்து செய்யவும்",
                "உங்கள் சுகாதார பராமரிப்பாளருடன் உங்கள் மனநிலையைப் பற்றி பேசுங்கள்"
            ]
        elif risk_level == "Medium Risk":
            return [
                "உடனடியாக உங்கள் சுகாதார பராமரிப்பாளரைத் தொடர்பு கொள்ளுங்கள்",
                "மன ஆரோக்கிய நிபுணருடன் ஆலோசனை பெறுவதைக் கருத்தில் கொள்ளுங்கள்",
                "குடும்ப உறுப்பினர்களிடம் உங்கள் உணர்வுகளைப் பகிர்ந்து கொள்ளுங்கள்",
                "ஆதரவு குழுவில் சேருவதைக் கருத்தில் கொள்ளுங்கள்"
            ]
        elif risk_level == "High Risk":
            return [
                "உடனடியாக மருத்துவ ஆலோசனை பெறுங்கள்",
                "மன ஆரோக்கிய நிபுணருடன் அவசரமாக பேசுங்கள்",
                "குடும்ப உறுப்பினர்களிடம் உதவி கேளுங்கள்",
                "நெருக்கடி ஆதரவு வளங்களைத் தொடர்பு கொள்ளுங்கள்"
            ]
        else:  # Very High Risk
            return [
                "உடனடியாக அவசர மருத்துவ சேவைகளைத் தொடர்பு கொள்ளுங்கள்",
                "மன ஆரோக்கிய நிபுணருடன் அவசரமாக பேசுங்கள்",
                "நெருக்கடி ஆதரவு வரியைத் தொடர்பு கொள்ளுங்கள்",
                "குடும்ப உறுப்பினர்களிடம் உடனடி உதவி கேளுங்கள்"
            ]
    
    def _generate_action_plan(self, risk_level: str, percentage: float) -> Dict[str, str]:
        """Generate specific action plan based on risk level"""
        if risk_level == "Low Risk":
            return {
                "immediate": "உங்கள் நேர்மறையான மனநிலையைத் தொடர்ந்து பராமரிக்கவும்",
                "short_term": "வழக்கமான சுகாதார பராமரிப்பு நடைமுறைகளைத் தொடர்ந்து செய்யவும்",
                "long_term": "ஆரோக்கியமான வாழ்க்கை முறையைத் தொடர்ந்து பராமரிக்கவும்"
            }
        elif risk_level == "Mild Risk":
            return {
                "immediate": "உங்கள் சுகாதார பராமரிப்பாளருடன் உங்கள் மனநிலையைப் பற்றி பேசுங்கள்",
                "short_term": "அழுத்தம் குறைப்பு நுட்பங்களைப் பயிற்சி செய்யுங்கள்",
                "long_term": "வழக்கமான மன ஆரோக்கிய ஆலோசனை பெறுங்கள்"
            }
        elif risk_level == "Medium Risk":
            return {
                "immediate": "உடனடியாக மருத்துவ ஆலோசனை பெறுங்கள்",
                "short_term": "மன ஆரோக்கிய நிபுணருடன் ஆலோசனை பெறுங்கள்",
                "long_term": "வழக்கமான மன ஆரோக்கிய பராமரிப்பு திட்டத்தைத் தொடங்குங்கள்"
            }
        elif risk_level == "High Risk":
            return {
                "immediate": "உடனடியாக மன ஆரோக்கிய நிபுணருடன் பேசுங்கள்",
                "short_term": "வழக்கமான மன ஆரோக்கிய பராமரிப்பு திட்டத்தைத் தொடங்குங்கள்",
                "long_term": "நீண்ட கால மன ஆரோக்கிய ஆதரவு பெறுங்கள்"
            }
        else:  # Very High Risk
            return {
                "immediate": "உடனடியாக அவசர மருத்துவ சேவைகளைத் தொடர்பு கொள்ளுங்கள்",
                "short_term": "நெருக்கடி ஆதரவு வளங்களைப் பயன்படுத்துங்கள்",
                "long_term": "விரிவான மன ஆரோக்கிய பராமரிப்பு திட்டத்தைத் தொடங்குங்கள்"
            }
    
    def generate_audio(self, text: str) -> Dict[str, Any]:
        """Generate Tamil audio using ElevenLabs"""
        try:
            if not text or not text.strip():
                return {
                    "success": False,
                    "error": "Text is required and cannot be empty"
                }
            
            # Limit text length to prevent API abuse
            if len(text) > 5000:
                return {
                    "success": False,
                    "error": "Text is too long. Maximum 5000 characters allowed."
                }
            
            if not self.elevenlabs_api_key or self.elevenlabs_api_key == "your_elevenlabs_api_key_here":
                return {
                    "success": False,
                    "error": "ElevenLabs API key not configured",
                    "fallback": True
                }
            
            # Use a Tamil voice (Adam voice - good for Tamil)
            voice_id = "pNInz6obpgDQGcFmaJgB"
            
            # ElevenLabs API call
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",  # Better for Tamil
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5,
                    "style": 0.0,
                    "use_speaker_boost": True
                }
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=15)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": "ElevenLabs API error",
                    "fallback": True
                }
            
            if not response.content or len(response.content) < 1000:
                return {
                    "success": False,
                    "error": "Audio response too small",
                    "fallback": True
                }
            
            # Return audio data as base64
            import base64
            audio_base64 = base64.b64encode(response.content).decode('utf-8')
            
            return {
                "success": True,
                "audio_data": audio_base64,
                "audio_type": "audio/mpeg",
                "size": len(response.content)
            }
            
        except Exception as e:
            print(f"Audio generation error: {e}")
            return {
                "success": False,
                "error": f"Error generating audio: {str(e)}",
                "fallback": True
            }

    def generate_chat_response(self, message: str, patient_id: str, context: str = None, 
                             mood: str = None, session_id: str = None, 
                             user_profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate AI chat response for mental health support"""
        try:
            if not self.openai_client:
                return self._generate_fallback_chat_response(message, mood)
            
            # Build context-aware prompt
            system_prompt = self._build_chat_system_prompt(mood, user_profile)
            
            # Create conversation context
            conversation_context = self._build_conversation_context(context, session_id)
            
            # Generate response using OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"{conversation_context}\n\nUser: {message}"}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Generate suggestions based on the response
            suggestions = self._generate_suggestions(message, ai_response, mood)
            
            return {
                "success": True,
                "message": ai_response,
                "message_type": "supportive",
                "suggestions": suggestions,
                "metadata": {
                    "mood": mood,
                    "context": context,
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat()
                },
                "session_id": session_id,
                "requires_follow_up": self._requires_follow_up(message, ai_response)
            }
            
        except Exception as e:
            print(f"Chat response generation error: {e}")
            return self._generate_fallback_chat_response(message, mood)
    
    def _build_chat_system_prompt(self, mood: str = None, user_profile: Dict[str, Any] = None) -> str:
        """Build system prompt for mental health chat"""
        base_prompt = """You are a compassionate AI mental health support assistant for pregnant women. 
        Your role is to provide emotional support, guidance, and encouragement while being mindful of 
        pregnancy-related mental health concerns.
        
        Guidelines:
        - Be empathetic, non-judgmental, and supportive
        - Focus on pregnancy-safe mental health advice
        - Encourage professional help when appropriate
        - Provide practical coping strategies
        - Use warm, understanding language
        - Avoid medical advice - refer to healthcare providers for medical concerns
        - Be culturally sensitive and inclusive"""
        
        if mood:
            mood_context = f"\n\nCurrent mood context: The user is feeling {mood}. Adjust your response accordingly."
            base_prompt += mood_context
        
        if user_profile and user_profile.get('pregnancy_stage'):
            stage = user_profile['pregnancy_stage']
            base_prompt += f"\n\nPregnancy stage: {stage}. Consider stage-specific mental health concerns."
        
        return base_prompt
    
    def _build_conversation_context(self, context: str = None, session_id: str = None) -> str:
        """Build conversation context for better responses"""
        context_parts = []
        
        if context:
            context_parts.append(f"Previous context: {context}")
        
        if session_id:
            context_parts.append(f"Session ID: {session_id}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def _generate_suggestions(self, user_message: str, ai_response: str, mood: str = None) -> List[str]:
        """Generate helpful suggestions based on the conversation"""
        suggestions = []
        
        # Mood-based suggestions
        if mood and mood.lower() in ['sad', 'anxious', 'stressed']:
            suggestions.extend([
                "Try deep breathing exercises",
                "Consider talking to your healthcare provider",
                "Practice gentle pregnancy-safe exercises"
            ])
        elif mood and mood.lower() in ['happy', 'excited', 'positive']:
            suggestions.extend([
                "Keep up the positive mindset!",
                "Share your joy with loved ones",
                "Document these happy moments"
            ])
        
        # General helpful suggestions
        suggestions.extend([
            "Practice mindfulness or meditation",
            "Connect with other expecting mothers",
            "Maintain a healthy sleep routine"
        ])
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def _requires_follow_up(self, user_message: str, ai_response: str) -> bool:
        """Determine if the conversation requires follow-up"""
        concerning_keywords = [
            'harm', 'hurt', 'suicide', 'self-harm', 'end it all',
            'hopeless', 'worthless', 'can\'t go on', 'give up'
        ]
        
        user_lower = user_message.lower()
        return any(keyword in user_lower for keyword in concerning_keywords)
    
    def _generate_fallback_chat_response(self, message: str, mood: str = None) -> Dict[str, Any]:
        """Generate fallback response when OpenAI is not available"""
        fallback_responses = [
            "I'm here to listen and support you. How are you feeling today?",
            "It's completely normal to have mixed emotions during pregnancy. You're doing great!",
            "Remember, it's okay to not be okay sometimes. You're not alone in this journey.",
            "Pregnancy can bring many emotions. Take things one day at a time.",
            "Your feelings are valid. Would you like to talk about what's on your mind?"
        ]
        
        # Select response based on mood if available
        if mood and mood.lower() in ['sad', 'anxious', 'stressed']:
            response = "I can sense you're going through a tough time. Remember, it's okay to feel this way during pregnancy. You're stronger than you know, and there are people who care about you."
        else:
            response = random.choice(fallback_responses)
        
        return {
            "success": True,
            "message": response,
            "message_type": "supportive",
            "suggestions": [
                "Consider talking to your healthcare provider",
                "Practice deep breathing exercises",
                "Connect with supportive friends or family"
            ],
            "metadata": {
                "mood": mood,
                "fallback": True,
                "timestamp": datetime.now().isoformat()
            },
            "requires_follow_up": False
        }


# Global mental health service instance - import this for use across the app
mental_health_service = MentalHealthService()