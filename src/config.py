"""
Configuration management with validation.
"""
import os
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Central configuration class."""
    
    def __init__(self):
        self.llm_provider = os.getenv("LLM_PROVIDER", "mock")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.audit_secret_key = os.getenv("AUDIT_SECRET_KEY")
        self.flask_secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")
        self.selenium_headless = os.getenv("SELENIUM_HEADLESS", "false").lower() == "true"
        self.portal_login_url = os.getenv("PORTAL_LOGIN_URL", "https://internyet.vtu.ac.in/login")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
    def is_production(self) -> bool:
        return os.getenv("ENV", "development") == "production"


def validate_config() -> List[str]:
    """Validate configuration and return list of errors."""
    errors = []
    config = Config()
    
    # Check LLM provider
    if config.llm_provider not in ["mock", "gemini", "openai"]:
        errors.append(f"Invalid LLM_PROVIDER: {config.llm_provider}")
    
    if config.llm_provider == "gemini" and not config.gemini_api_key:
        errors.append("GEMINI_API_KEY is required when using Gemini provider")
    
    if config.llm_provider == "openai" and not config.openai_api_key:
        errors.append("OPENAI_API_KEY is required when using OpenAI provider")
    
    # Check audit encryption
    if not config.audit_secret_key:
        errors.append("AUDIT_SECRET_KEY is not set (audit log will use auto-generated key)")
    
    # Check Flask secret in production
    if config.is_production() and config.flask_secret_key == "dev-secret-change-me":
        errors.append("FLASK_SECRET_KEY must be changed in production")
    
    # Check .env file exists
    if not Path(".env").exists():
        errors.append(".env file not found (copy from .env.example)")
    
    return errors
