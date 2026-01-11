import logging
import logging.config
import os
import json
from datetime import datetime


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, "extra_data"):
            log_obj["data"] = record.extra_data
            
        return json.dumps(log_obj)


class Logger:
    _initialized = False
    
    @staticmethod
    def setup_logging():
        """Configure application logging to file and console"""
        
        if Logger._initialized:
            return logging.getLogger("llm_gateway")
        
        # Ensure logs directory exists
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Get log level from environment (default: INFO)
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        
        # Logging configuration
        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": JsonFormatter,
                },
                "standard": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "stream": "ext://sys.stdout",
                    "level": log_level,
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "json",
                    "filename": f"{log_dir}/app.log",
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5,
                    "encoding": "utf8",
                    "level": "DEBUG",  # File captures everything for debugging
                },
            },
            "loggers": {
                "llm_gateway": {
                    "handlers": ["console", "file"],
                    "level": log_level,
                    "propagate": False,
                },
                # Suppress noisy third-party loggers
                "httpx": {"level": "WARNING"},
                "httpcore": {"level": "WARNING"},
                "chromadb": {"level": "WARNING"},
            },
            "root": {
                "handlers": ["console", "file"],
                "level": "WARNING",
            },
        }

        logging.config.dictConfig(logging_config)
        Logger._initialized = True
        
        logger = logging.getLogger("llm_gateway")
        logger.info(f"Logging configured successfully (level: {log_level})")
        return logger


def get_logger(name: str = None) -> logging.Logger:
    """Get a logger instance for a module.
    
    Usage:
        from app.utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Hello world")
    
    Args:
        name: Module name (use __name__). If None, returns root llm_gateway logger.
    
    Returns:
        Configured logger instance
    """
    if name:
        return logging.getLogger(f"llm_gateway.{name}")
    return logging.getLogger("llm_gateway")


# Create a global logger instance for easy import if needed, 
# though getting via get_logger(__name__) is preferred in modules.
setup_logging = Logger.setup_logging
