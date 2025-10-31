import os
import json
from typing import List, Dict, Any
from datetime import datetime
import logging

class MedicalKnowledgeBase:
    """
    Medical knowledge base for pregnancy care and women's health.
    Provides structured medical knowledge chunks for RAG system.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.knowledge_chunks = []
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """Initialize the medical knowledge base with pregnancy care guidelines."""
        try:
            # Load existing knowledge if available
            self._load_knowledge_from_file()
            
            # If no knowledge loaded, initialize with default medical knowledge
            if not self.knowledge_chunks:
                self._create_default_knowledge_base()
                self._save_knowledge_to_file()
            
            self.logger.info(f"Medical knowledge base initialized with {len(self.knowledge_chunks)} chunks")
            
        except Exception as e:
            self.logger.error(f"Error initializing medical knowledge base: {str(e)}")
            self.knowledge_chunks = []
    
    def _create_default_knowledge_base(self):
        """Create default medical knowledge base with pregnancy care guidelines."""
        self.knowledge_chunks = [
            # First Trimester Knowledge
            {
                "content": "First trimester (weeks 1-12) is critical for fetal development. Key nutrients needed include folic acid (400-800 mcg daily), iron, calcium, and DHA. Common symptoms include nausea, fatigue, breast tenderness, and frequent urination. Avoid alcohol, smoking, and certain medications. Regular prenatal care is essential.",
                "metadata": {
                    "type": "pregnancy",
                    "trimester": "first",
                    "category": "general_care",
                    "source": "ACOG Guidelines",
                    "priority": "high"
                }
            },
            {
                "content": "Morning sickness in first trimester affects 70-80% of pregnant women. Management includes eating small, frequent meals, avoiding triggers, staying hydrated, and considering vitamin B6 or ginger supplements. Severe nausea and vomiting (hyperemesis gravidarum) requires medical attention.",
                "metadata": {
                    "type": "pregnancy",
                    "trimester": "first",
                    "category": "symptoms",
                    "source": "ACOG Guidelines",
                    "priority": "high"
                }
            },
            {
                "content": "Folic acid supplementation (400-800 mcg daily) is crucial in first trimester to prevent neural tube defects. Start taking folic acid at least one month before conception and continue through first trimester. Natural sources include leafy greens, citrus fruits, and fortified cereals.",
                "metadata": {
                    "type": "pregnancy",
                    "trimester": "first",
                    "category": "nutrition",
                    "source": "ACOG Guidelines",
                    "priority": "critical"
                }
            },
            
            # Second Trimester Knowledge
            {
                "content": "Second trimester (weeks 13-26) is often the most comfortable period. Energy levels typically improve, and morning sickness usually subsides. Fetal movement begins around 18-20 weeks. Weight gain should be gradual (1-2 pounds per week). Focus on balanced nutrition and regular exercise.",
                "metadata": {
                    "type": "pregnancy",
                    "trimester": "second",
                    "category": "general_care",
                    "source": "ACOG Guidelines",
                    "priority": "high"
                }
            },
            {
                "content": "Kick counting should begin around 28 weeks (late second trimester). Count fetal movements for one hour after meals. Normal is 10 movements in 2 hours. Decreased fetal movement requires immediate medical attention. Use kick counting apps or charts to track patterns.",
                "metadata": {
                    "type": "pregnancy",
                    "trimester": "second",
                    "category": "monitoring",
                    "source": "ACOG Guidelines",
                    "priority": "high"
                }
            },
            
            # Third Trimester Knowledge
            {
                "content": "Third trimester (weeks 27-40) brings increased discomfort including back pain, heartburn, and difficulty sleeping. Fetal growth accelerates, and weight gain should be monitored. Regular prenatal visits become more frequent. Prepare for labor and delivery.",
                "metadata": {
                    "type": "pregnancy",
                    "trimester": "third",
                    "category": "general_care",
                    "source": "ACOG Guidelines",
                    "priority": "high"
                }
            },
            {
                "content": "Braxton Hicks contractions are normal in third trimester. They are irregular, mild, and don't increase in intensity. True labor contractions are regular, increase in intensity, and don't stop with rest. Contact healthcare provider if contractions are regular and increasing.",
                "metadata": {
                    "type": "pregnancy",
                    "trimester": "third",
                    "category": "symptoms",
                    "source": "ACOG Guidelines",
                    "priority": "high"
                }
            },
            
            # Medication Safety
            {
                "content": "Medication safety in pregnancy follows FDA categories: Category A (safest), B (likely safe), C (unknown), D (risky), X (contraindicated). Always consult healthcare provider before taking any medication. Some safe options include acetaminophen for pain, certain antihistamines, and most prenatal vitamins.",
                "metadata": {
                    "type": "medications",
                    "category": "safety",
                    "source": "FDA Guidelines",
                    "priority": "critical"
                }
            },
            {
                "content": "Avoid NSAIDs (ibuprofen, aspirin) in third trimester as they can cause premature closure of fetal ductus arteriosus. Acetaminophen is generally safe for pain relief. Always discuss medication changes with healthcare provider, especially in first trimester.",
                "metadata": {
                    "type": "medications",
                    "category": "safety",
                    "source": "FDA Guidelines",
                    "priority": "high"
                }
            },
            
            # Nutrition Guidelines
            {
                "content": "Pregnancy nutrition requires 300-500 extra calories daily. Key nutrients: protein (71g daily), iron (27mg), calcium (1000mg), DHA (200-300mg), and folic acid. Eat variety of fruits, vegetables, whole grains, lean proteins, and dairy. Limit caffeine to 200mg daily.",
                "metadata": {
                    "type": "nutrition",
                    "category": "general",
                    "source": "ACOG Guidelines",
                    "priority": "high"
                }
            },
            {
                "content": "Food safety is crucial during pregnancy. Avoid raw fish, undercooked meat, unpasteurized dairy, deli meats, and high-mercury fish. Wash all fruits and vegetables thoroughly. Cook meat to proper temperatures. Avoid alcohol completely.",
                "metadata": {
                    "type": "nutrition",
                    "category": "safety",
                    "source": "CDC Guidelines",
                    "priority": "critical"
                }
            },
            
            # Warning Signs
            {
                "content": "Seek immediate medical attention for: severe abdominal pain, heavy bleeding, severe headaches with vision changes, persistent vomiting, high fever, decreased fetal movement, or signs of preterm labor. These symptoms may indicate serious complications requiring urgent care.",
                "metadata": {
                    "type": "emergency",
                    "category": "warning_signs",
                    "source": "ACOG Guidelines",
                    "priority": "critical"
                }
            },
            {
                "content": "Preterm labor warning signs include regular contractions before 37 weeks, pelvic pressure, low back pain, abdominal cramping, or changes in vaginal discharge. Contact healthcare provider immediately if experiencing these symptoms.",
                "metadata": {
                    "type": "emergency",
                    "category": "preterm_labor",
                    "source": "ACOG Guidelines",
                    "priority": "critical"
                }
            },
            
            # Mental Health
            {
                "content": "Pregnancy can affect mental health. Common concerns include anxiety, mood changes, and depression. Perinatal depression affects 10-15% of women. Seek support from healthcare providers, family, and mental health professionals. Treatment options include therapy and safe medications.",
                "metadata": {
                    "type": "mental_health",
                    "category": "general",
                    "source": "ACOG Guidelines",
                    "priority": "high"
                }
            },
            
            # Exercise Guidelines
            {
                "content": "Regular exercise during pregnancy is beneficial for most women. Recommended: 150 minutes of moderate-intensity exercise weekly. Safe activities include walking, swimming, prenatal yoga, and low-impact aerobics. Avoid contact sports, high-altitude activities, and exercises with fall risk.",
                "metadata": {
                    "type": "exercise",
                    "category": "general",
                    "source": "ACOG Guidelines",
                    "priority": "medium"
                }
            },
            
            # Sleep Guidelines
            {
                "content": "Sleep changes are common during pregnancy. First trimester: increased fatigue and need for sleep. Third trimester: difficulty sleeping due to discomfort, frequent urination, and anxiety. Sleep on left side to improve circulation. Use pregnancy pillows for comfort.",
                "metadata": {
                    "type": "sleep",
                    "category": "general",
                    "source": "ACOG Guidelines",
                    "priority": "medium"
                }
            }
        ]
    
    def get_knowledge_chunks(self, filter_type: str = None, trimester: str = None) -> List[Dict[str, Any]]:
        """
        Get medical knowledge chunks with optional filtering.
        
        Args:
            filter_type: Filter by knowledge type (pregnancy, medications, nutrition, etc.)
            trimester: Filter by trimester (first, second, third)
        
        Returns:
            List of filtered knowledge chunks
        """
        filtered_chunks = self.knowledge_chunks.copy()
        
        if filter_type:
            filtered_chunks = [
                chunk for chunk in filtered_chunks
                if chunk['metadata'].get('type', '').lower() == filter_type.lower()
            ]
        
        if trimester:
            filtered_chunks = [
                chunk for chunk in filtered_chunks
                if chunk['metadata'].get('trimester', '').lower() == trimester.lower()
            ]
        
        return filtered_chunks
    
    def add_knowledge_chunk(self, content: str, metadata: Dict[str, Any]) -> bool:
        """
        Add a new knowledge chunk to the base.
        
        Args:
            content: The knowledge content
            metadata: Metadata about the knowledge chunk
        
        Returns:
            True if successful, False otherwise
        """
        try:
            chunk = {
                "content": content,
                "metadata": {
                    **metadata,
                    "added_at": datetime.utcnow().isoformat(),
                    "source": metadata.get("source", "Custom")
                }
            }
            
            self.knowledge_chunks.append(chunk)
            self._save_knowledge_to_file()
            
            self.logger.info("Added new knowledge chunk successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding knowledge chunk: {str(e)}")
            return False
    
    def _save_knowledge_to_file(self):
        """Save knowledge chunks to file."""
        try:
            os.makedirs("data", exist_ok=True)
            with open("data/medical_knowledge.json", "w") as f:
                json.dump(self.knowledge_chunks, f, indent=2)
            
            self.logger.info("Medical knowledge base saved to file")
            
        except Exception as e:
            self.logger.error(f"Error saving knowledge base: {str(e)}")
    
    def _load_knowledge_from_file(self):
        """Load knowledge chunks from file."""
        try:
            if os.path.exists("data/medical_knowledge.json"):
                with open("data/medical_knowledge.json", "r") as f:
                    self.knowledge_chunks = json.load(f)
                
                self.logger.info(f"Loaded {len(self.knowledge_chunks)} knowledge chunks from file")
            else:
                self.logger.info("No existing knowledge base file found")
                
        except Exception as e:
            self.logger.error(f"Error loading knowledge base: {str(e)}")
            self.knowledge_chunks = []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base."""
        type_counts = {}
        trimester_counts = {}
        
        for chunk in self.knowledge_chunks:
            chunk_type = chunk['metadata'].get('type', 'unknown')
            type_counts[chunk_type] = type_counts.get(chunk_type, 0) + 1
            
            trimester = chunk['metadata'].get('trimester', 'unknown')
            if trimester != 'unknown':
                trimester_counts[trimester] = trimester_counts.get(trimester, 0) + 1
        
        return {
            "total_chunks": len(self.knowledge_chunks),
            "type_distribution": type_counts,
            "trimester_distribution": trimester_counts,
            "last_updated": datetime.utcnow().isoformat()
        }
