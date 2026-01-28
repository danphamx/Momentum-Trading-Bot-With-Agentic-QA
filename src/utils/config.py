"""
Configuration loader for Momentum Trading System
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:
    """Central configuration management"""
    
    # API Keys & Credentials
    SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
    
    # Google API
    GOOGLE_SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID", "")
    GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    
    # Email
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
    
    # System
    DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Trading Parameters
    PORTFOLIO_SIZE_USD = float(os.getenv("PORTFOLIO_SIZE_USD", "100000"))
    MAX_DRAWDOWN_TOLERANCE_PCT = float(os.getenv("MAX_DRAWDOWN_TOLERANCE_PCT", "15"))
    
    @classmethod
    def validate(cls):
        """Validate critical config values"""
        if not cls.PORTFOLIO_SIZE_USD > 0:
            raise ValueError("PORTFOLIO_SIZE_USD must be > 0")
        if not 0 < cls.MAX_DRAWDOWN_TOLERANCE_PCT <= 100:
            raise ValueError("MAX_DRAWDOWN_TOLERANCE_PCT must be between 0-100")
        print("✓ Configuration validated")

# Validate on import
Config.validate()
