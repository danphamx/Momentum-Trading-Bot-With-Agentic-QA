"""
Structured logging for Momentum Trading System
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

# Create logs directory if it doesn't exist
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

class MomentumLogger:
    """Centralized logger for all system components"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup_logger()
        return cls._instance
    
    def _setup_logger(self):
        """Configure logger with file and console handlers"""
        self.logger = logging.getLogger("momentum_system")
        self.logger.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # File handler
        log_file = LOG_DIR / f"momentum_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def get_logger(self, name):
        """Get named logger"""
        return logging.getLogger(f"momentum_system.{name}")


def get_logger(name):
    """Convenience function to get logger"""
    logger_manager = MomentumLogger()
    return logger_manager.get_logger(name)


# Test
if __name__ == "__main__":
    logger = get_logger("test")
    logger.info("✓ Logging initialized")
