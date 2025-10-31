"""
LLM Service for symptom analysis and recommendations using OpenAI
"""
from app.core.config import (
    OPENAI_API_KEY,
    LLM_MODEL,
    DISCLAIMER_TEXT,
    FALLBACK_STATIC_TEXT,
    FALLBACK_SYSTEM_PROMPT,
    SUMMARY_SYSTEM_PROMPT
)

# Optional imports
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("[WARN] OpenAI not available")


class LLMService:
    """LLM service for symptom analysis and recommendations"""
    
    def __init__(self):
        self.client = None
        self.initialize_client()
    
    def initialize_client(self):
        """Initialize OpenAI client"""
        if OPENAI_AVAILABLE and OPENAI_API_KEY:
            try:
                self.client = OpenAI(api_key=OPENAI_API_KEY)
                print("[OK] OpenAI client initialized successfully")
            except Exception as e:
                print(f"[ERROR] OpenAI client initialization failed: {e}")
                self.client = None
        else:
            print("[WARN] OpenAI not available - using fallback responses")
    
    def detect_red_flags(self, text: str) -> list:
        """Detect red flag symptoms in text"""
        flags = []
        lower_text = text.lower()
        
        if any(k in lower_text for k in ["bleeding", "spotting", "blood"]):
            flags.append("vaginal bleeding")
        if any(k in lower_text for k in ["severe pain", "sharp pain", "worst pain"]):
            flags.append("severe pain")
        if any(k in lower_text for k in ["vision", "blurry", "flashing lights"]):
            flags.append("vision changes")
        if any(k in lower_text for k in ["fever", "temperature", "high temp"]):
            flags.append("fever")
        if any(k in lower_text for k in ["reduced movement", "less movement", "not moving"]):
            flags.append("reduced fetal movement")
        
        return flags
    
    def generate_llm_fallback(self, symptom_text: str, weeks_pregnant: int) -> dict:
        """Generate LLM-powered fallback response"""
        red_flags = self.detect_red_flags(symptom_text)
        
        if self.client:
            try:
                trimester = "first" if weeks_pregnant <= 13 else ("second" if weeks_pregnant <= 27 else "third")
                
                response = self.client.chat.completions.create(
                    model=LLM_MODEL,
                    messages=[
                        {"role": "system", "content": FALLBACK_SYSTEM_PROMPT},
                        {"role": "user", "content": f"User symptom text: '{symptom_text}'. Weeks pregnant: {weeks_pregnant} (trimester: {trimester}). If any red flags, state them and advise urgent care."}
                    ],
                    temperature=0.2,
                )
                content = response.choices[0].message.content.strip()
            except Exception as e:
                print(f"[WARN] LLM fallback failed: {e}")
                content = FALLBACK_STATIC_TEXT
        else:
            content = FALLBACK_STATIC_TEXT
        
        suggestions = [
            {
                "id": "fallback-1",
                "text": content,
                "metadata": {
                    "triage": "use clinical judgment; follow red-flag guidance",
                    "source": "LLM-fallback" if self.client else "static-fallback",
                },
                "score": None,
            }
        ]
        
        if red_flags:
            suggestions.insert(0, {
                "id": "fallback-urgent",
                "text": f"Your description suggests potential red flags ({', '.join(red_flags)}) — please seek urgent care or contact your provider immediately.",
                "metadata": {"triage": "urgent", "source": "safety-check"},
                "score": None,
            })
        
        return {
            "suggestions": suggestions,
            "disclaimers": DISCLAIMER_TEXT,
            "red_flags": red_flags
        }
    
    def summarize_retrieval(self, symptom_text: str, weeks_pregnant: int, suggestions: list) -> dict:
        """Summarize retrieved suggestions using LLM"""
        if not suggestions or not self.client:
            return None
        
        try:
            trimester = "first" if weeks_pregnant <= 13 else ("second" if weeks_pregnant <= 27 else "third")
            
            # Build evidence from top suggestions
            top_suggestions = suggestions[:3]
            evidence = "\n".join(
                f"- [triage: {s.get('metadata', {}).get('triage', 'unspecified')}] {s.get('text', '')}"
                for s in top_suggestions
            )
            
            response = self.client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
                    {"role": "user", "content": f"User symptom text: '{symptom_text}'. Weeks pregnant: {weeks_pregnant} (trimester: {trimester}). Evidence bullets (use ONLY these):\n{evidence}"}
                ],
                temperature=0.2,
            )
            content = response.choices[0].message.content.strip()
            
            return {
                "id": "synthesis-1",
                "text": content,
                "metadata": {
                    "source": "LLM-summary",
                    "evidence_ids": [s.get("id") for s in top_suggestions],
                    "triage": "summary",
                },
                "score": None,
            }
        except Exception as e:
            print(f"[WARN] LLM summarization failed: {e}")
            return None


# Global LLM service instance - import this for use across the app
llm_service = LLMService()

