import os
from typing import Optional
from dotenv import load_dotenv

# Load .env if present (project root)
load_dotenv()

# Ensure ADK/google-genai picks up the API key from the expected env var
# ADK expects GOOGLE_API_KEY for Google AI (Gemini) backend
if not os.getenv("GOOGLE_API_KEY") and os.getenv("GOOGLE_AI_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_AI_API_KEY")
    # Also set the google-genai legacy alias if present in some environments
    os.environ.setdefault("GOOGLE_GENAI_API_KEY", os.getenv("GOOGLE_AI_API_KEY"))

class Config:
    """Configuration for Travel Agent Prototype"""
    
    # SerpApi Configuration
    SERPAPI_KEY: Optional[str] = os.getenv("SERPAPI_KEY")
    
    # Google AI Configuration (for LLM)
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    GOOGLE_AI_API_KEY: Optional[str] = os.getenv("GOOGLE_AI_API_KEY")
    
    # Optional: OpenAI API Key (alternative LLM)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Default LLM Model
    DEFAULT_MODEL: str = "gemini-2.5-flash"
    
    # Application Settings
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        missing = []
        
        if not cls.SERPAPI_KEY:
            missing.append("SERPAPI_KEY")
        
        if not cls.GOOGLE_API_KEY and not cls.OPENAI_API_KEY:
            missing.append("GOOGLE_API_KEY or OPENAI_API_KEY")
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return True
