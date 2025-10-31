from .pregnancy_models import PregnancyWeek, KeyDevelopment, BabySize
from typing import Dict

class PregnancyDataService:
    def __init__(self):
        self.pregnancy_data = self._initialize_data()
    
    def _initialize_data(self) -> Dict[int, PregnancyWeek]:
        """Initialize pregnancy week data with key developments"""
        data = {}
        
        # Week 1-4 (Trimester 1)
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
                KeyDevelopment(
                    title="Cell Division Begins",
                    description="The fertilized egg starts dividing rapidly into multiple cells.",
                    icon="🔬",
                    category="development"
                )
            ],
            symptoms=["Implantation bleeding", "Mild cramping", "Fatigue"],
            tips=["Start taking prenatal vitamins", "Avoid alcohol and smoking", "Maintain healthy diet"]
        )
        
        data[2] = PregnancyWeek(
            week=2,
            trimester=1,
            days_remaining=273,
            baby_size=BabySize(size="Poppy seed", weight="0.1g", length="0.1cm"),
            key_developments=[
                KeyDevelopment(
                    title="Implantation",
                    description="The fertilized egg implants into the uterine wall.",
                    icon="🏠",
                    category="implantation"
                ),
                KeyDevelopment(
                    title="Hormone Production",
                    description="The body starts producing hCG hormone to support pregnancy.",
                    icon="⚗️",
                    category="hormones"
                )
            ],
            symptoms=["Spotting", "Mild cramping", "Breast tenderness"],
            tips=["Continue prenatal vitamins", "Stay hydrated", "Get adequate rest"]
        )
        
        data[3] = PregnancyWeek(
            week=3,
            trimester=1,
            days_remaining=266,
            baby_size=BabySize(size="Poppy seed", weight="0.1g", length="0.1cm"),
            key_developments=[
                KeyDevelopment(
                    title="Placenta Formation",
                    description="The placenta begins to form to nourish the developing baby.",
                    icon="🍃",
                    category="placenta"
                ),
                KeyDevelopment(
                    title="Neural Tube Development",
                    description="The foundation of the brain and spinal cord begins to form.",
                    icon="🧠",
                    category="neural"
                )
            ],
            symptoms=["Morning sickness", "Food aversions", "Mood swings"],
            tips=["Eat small, frequent meals", "Avoid strong odors", "Practice relaxation techniques"]
        )
        
        data[4] = PregnancyWeek(
            week=4,
            trimester=1,
            days_remaining=259,
            baby_size=BabySize(size="Poppy seed", weight="0.1g", length="0.1cm"),
            key_developments=[
                KeyDevelopment(
                    title="Heart Formation",
                    description="The primitive heart tube begins to form and beat.",
                    icon="❤️",
                    category="cardiovascular"
                ),
                KeyDevelopment(
                    title="Limb Buds Appear",
                    description="Small buds that will become arms and legs start to form.",
                    icon="🤲",
                    category="limbs"
                )
            ],
            symptoms=["Missed period", "Positive pregnancy test", "Increased urination"],
            tips=["Schedule first prenatal appointment", "Continue healthy lifestyle", "Avoid raw fish"]
        )
        
        # Week 5-8 (Trimester 1)
        data[5] = PregnancyWeek(
            week=5,
            trimester=1,
            days_remaining=252,
            baby_size=BabySize(size="Sesame seed", weight="0.1g", length="0.1cm"),
            key_developments=[
                KeyDevelopment(
                    title="Heart Beats",
                    description="The tiny heart starts beating for the first time.",
                    icon="💓",
                    category="cardiovascular"
                ),
                KeyDevelopment(
                    title="Brain Development",
                    description="The brain begins to form with distinct regions.",
                    icon="🧠",
                    category="neural"
                )
            ],
            symptoms=["Morning sickness", "Fatigue", "Breast changes"],
            tips=["Eat ginger for nausea", "Get plenty of sleep", "Stay hydrated"]
        )
        
        data[6] = PregnancyWeek(
            week=6,
            trimester=1,
            days_remaining=245,
            baby_size=BabySize(size="Lentil", weight="0.1g", length="0.2cm"),
            key_developments=[
                KeyDevelopment(
                    title="Facial Features",
                    description="Eyes, nose, and mouth begin to take shape.",
                    icon="👁️",
                    category="facial"
                ),
                KeyDevelopment(
                    title="Limb Development",
                    description="Arms and legs start to form with paddle-like hands and feet.",
                    icon="🦵",
                    category="limbs"
                )
            ],
            symptoms=["Morning sickness peaks", "Food cravings", "Mood swings"],
            tips=["Eat bland foods", "Avoid triggers", "Consider acupressure"]
        )
        
        data[7] = PregnancyWeek(
            week=7,
            trimester=1,
            days_remaining=238,
            baby_size=BabySize(size="Blueberry", weight="0.1g", length="0.3cm"),
            key_developments=[
                KeyDevelopment(
                    title="Internal Organs",
                    description="Liver, kidneys, and intestines begin to form.",
                    icon="🫀",
                    category="organs"
                ),
                KeyDevelopment(
                    title="Finger Development",
                    description="Fingers and toes start to separate and form.",
                    icon="✋",
                    category="limbs"
                )
            ],
            symptoms=["Morning sickness", "Breast tenderness", "Fatigue"],
            tips=["Eat small meals", "Wear comfortable bras", "Take naps"]
        )
        
        data[8] = PregnancyWeek(
            week=8,
            trimester=1,
            days_remaining=231,
            baby_size=BabySize(size="Raspberry", weight="0.1g", length="0.4cm"),
            key_developments=[
                KeyDevelopment(
                    title="Movement Begins",
                    description="The baby starts making small movements, though not yet felt.",
                    icon="🤸",
                    category="movement"
                ),
                KeyDevelopment(
                    title="Eyes Form",
                    description="Eyes begin to form with basic structure.",
                    icon="👀",
                    category="facial"
                )
            ],
            symptoms=["Morning sickness", "Constipation", "Mood changes"],
            tips=["Increase fiber intake", "Stay active", "Practice mindfulness"]
        )
        
        # Week 9-12 (Trimester 1)
        data[9] = PregnancyWeek(
            week=9,
            trimester=1,
            days_remaining=224,
            baby_size=BabySize(size="Grape", weight="0.1g", length="0.5cm"),
            key_developments=[
                KeyDevelopment(
                    title="Taste Buds",
                    description="Taste buds begin to form on the tongue.",
                    icon="👅",
                    category="sensory"
                ),
                KeyDevelopment(
                    title="Muscle Development",
                    description="Muscles start to form and develop.",
                    icon="💪",
                    category="muscular"
                )
            ],
            symptoms=["Morning sickness", "Breast changes", "Fatigue"],
            tips=["Eat protein-rich foods", "Wear supportive bras", "Get adequate rest"]
        )
        
        data[10] = PregnancyWeek(
            week=10,
            trimester=1,
            days_remaining=217,
            baby_size=BabySize(size="Coconut", weight="0.1g", length="0.6cm"),
            key_developments=[
                KeyDevelopment(
                    title="Healthy Organ Growth",
                    description="Vital organs are fully developed and functioning.",
                    icon="❤️",
                    category="organs"
                ),
                KeyDevelopment(
                    title="Finger & Toe Development",
                    description="Eyebrows and eyelids are now fully present.",
                    icon="👁️",
                    category="facial"
                ),
                KeyDevelopment(
                    title="Teeth Formation Begins",
                    description="Teeth are starting to form under the gums.",
                    icon="🦷",
                    category="dental"
                )
            ],
            symptoms=["Morning sickness easing", "Breast growth", "Mood stabilization"],
            tips=["Continue prenatal vitamins", "Eat balanced meals", "Stay active"]
        )
        
        # Add more weeks as needed...
        return data
    
    def get_week_data(self, week: int) -> PregnancyWeek:
        """Get pregnancy data for a specific week"""
        if week not in self.pregnancy_data:
            raise ValueError(f"Week {week} data not available. Please provide a week between 1-40.")
        return self.pregnancy_data[week]
    
    def get_all_weeks(self) -> Dict[int, PregnancyWeek]:
        """Get all available pregnancy week data"""
        return self.pregnancy_data
