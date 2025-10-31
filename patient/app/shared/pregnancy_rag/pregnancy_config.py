import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # OpenAPI Configuration
    OPENAPI_BASE_URL: str = os.getenv("OPENAPI_BASE_URL", "https://api.pregnancy.com/v1")
    OPENAPI_API_KEY: str = os.getenv("OPENAPI_API_KEY", "")
    OPENAPI_TIMEOUT: int = int(os.getenv("OPENAPI_TIMEOUT", "30"))
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "500"))
    
    # FastAPI Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Qdrant Configuration
    QDRANT_URL: str = os.getenv("QDRANT_URL", "")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "pregnancy_weeks")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Patient Backend Configuration
    PATIENT_BACKEND_URL: str = os.getenv("PATIENT_BACKEND_URL", "http://localhost:3000")
    PATIENT_BACKEND_API_KEY: str = os.getenv("PATIENT_BACKEND_API_KEY", "")

settings = Settings()
