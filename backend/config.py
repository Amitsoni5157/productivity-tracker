from ntpath import join
from pydantic_core.core_schema import missing_sentinel_schema
import os
from pathlib import Path
from dotenv import load_dotenv


# Load .env file from the same directory
env_path = Path(__file__).resolve().parent /".env"
load_dotenv(dotenv_path=env_path)

# Settings class to store environment variables
class Settings:
    # Project name
    PROJECT_NAME: str = "FocusAI - Productivity Analyzer"
    # Groq API key
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY","")
    # Supabase URL
    SUPABASE_URL: str = os.getenv("SUPABASE_URL","")
    # Supabase key
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    # Port number
    PORT: int = int(os.getenv("PORT",8000))

# Validate environment variables
    def validate(self):
        """validates that all critical settings are present."""
        missing= []
        if not self.GROQ_API_KEY:
            missing.append("GROQ_API_KEY:")
        if not self.SUPABASE_URL:
            missing.append("SUPABASE_URL")
        if not self.SUPABASE_KEY:
            missing.append("SUPABASE_KEY")

        if missing:
            raise ValueError(f"Missing required enviorment variables: {', '.join(missing)}")


# Create a single instance of settings to import elsewhere
settings = Settings()
