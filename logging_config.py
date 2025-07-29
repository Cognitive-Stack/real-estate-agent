"""
Logging configuration for Real Estate Chat Agent

This module provides advanced logging configuration options for the application.
"""

import logging
import logging.config
from datetime import datetime
import os


def get_detailed_logging_config(log_level: str = "INFO", enable_file_logging: bool = True) -> dict:
    """
    Get a detailed logging configuration dictionary.
    
    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR)
        enable_file_logging: Whether to enable file logging
        
    Returns:
        Dictionary containing logging configuration
    """
    
    # Create logs directory if it doesn't exist
    if enable_file_logging:
        os.makedirs("logs", exist_ok=True)
    
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'simple': {
                'format': '%(asctime)s - %(levelname)s - %(message)s',
                'datefmt': '%H:%M:%S'
            },
            'console': {
                'format': '🤖 %(levelname)s: %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': log_level,
                'formatter': 'console',
                'stream': 'ext://sys.stdout'
            }
        },
        'loggers': {
            '': {  # Root logger
                'handlers': ['console'],
                'level': log_level,
                'propagate': False
            },
            'autogen': {
                'handlers': ['console'],
                'level': log_level,
                'propagate': False
            },
            'openai': {
                'handlers': ['console'],
                'level': 'WARNING',  # Reduce OpenAI API noise
                'propagate': False
            },
            'httpx': {
                'handlers': ['console'],
                'level': 'WARNING',  # Reduce HTTP request noise
                'propagate': False
            },
            'pymongo': {
                'handlers': ['console'],
                'level': 'WARNING',  # Suppress MongoDB debug logs
                'propagate': False
            },
            'pymongo.command': {
                'handlers': ['console'],
                'level': 'WARNING',  # Suppress MongoDB command logs
                'propagate': False
            },
            'pymongo.connection': {
                'handlers': ['console'],
                'level': 'WARNING',  # Suppress MongoDB connection logs
                'propagate': False
            },
            'pymongo.topology': {
                'handlers': ['console'],
                'level': 'WARNING',  # Suppress MongoDB topology logs
                'propagate': False
            },
            'pymongo.serverSelection': {
                'handlers': ['console'],
                'level': 'WARNING',  # Suppress MongoDB server selection logs
                'propagate': False
            },
            'real_estate_agent': {
                'handlers': ['console'],
                'level': log_level,
                'propagate': False
            }
        }
    }
    
    # Add file handlers if file logging is enabled
    if enable_file_logging:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        config['handlers'].update({
            'file_detailed': {
                'class': 'logging.FileHandler',
                'level': 'DEBUG',
                'formatter': 'detailed',
                'filename': f'logs/real_estate_agent_{timestamp}.log',
                'mode': 'w'
            },
            'file_errors': {
                'class': 'logging.FileHandler',
                'level': 'ERROR',
                'formatter': 'detailed',
                'filename': f'logs/errors_{timestamp}.log',
                'mode': 'w'
            }
        })
        
        # Add file handlers to all loggers
        for logger_name in config['loggers']:
            config['loggers'][logger_name]['handlers'].extend(['file_detailed', 'file_errors'])
    
    return config


def setup_advanced_logging(log_level: str = "INFO", enable_file_logging: bool = True) -> None:
    """
    Setup advanced logging configuration.
    
    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR)
        enable_file_logging: Whether to enable file logging
    """
    config = get_detailed_logging_config(log_level, enable_file_logging)
    logging.config.dictConfig(config)
    
    # Explicitly suppress MongoDB logs
    suppress_mongodb_logs()
    
    # Log the configuration
    logger = logging.getLogger(__name__)
    logger.info(f"Advanced logging configured with level: {log_level}")
    if enable_file_logging:
        logger.info("File logging enabled in 'logs/' directory")


class AutoGenLogFilter(logging.Filter):
    """Custom filter for AutoGen logs to highlight important events."""
    
    def filter(self, record):
        # Highlight function calls and important AutoGen events
        if hasattr(record, 'msg'):
            msg = str(record.msg)
            if any(keyword in msg.lower() for keyword in ['function_call', 'tool_use', 'agent_response']):
                record.levelname = f"🔧 {record.levelname}"
            elif 'error' in msg.lower():
                record.levelname = f"❌ {record.levelname}"
            elif any(keyword in msg.lower() for keyword in ['response', 'completion']):
                record.levelname = f"✅ {record.levelname}"
        
        return True


def add_autogen_highlights():
    """Add custom filters to highlight AutoGen events."""
    autogen_logger = logging.getLogger('autogen')
    autogen_logger.addFilter(AutoGenLogFilter())
    
    app_logger = logging.getLogger('real_estate_agent')
    app_logger.addFilter(AutoGenLogFilter())


def suppress_mongodb_logs():
    """Explicitly suppress MongoDB debug and info logs."""
    # Set all MongoDB-related loggers to WARNING level
    mongodb_loggers = [
        'pymongo',
        'pymongo.command',
        'pymongo.connection', 
        'pymongo.topology',
        'pymongo.serverSelection',
        'pymongo.pool',
        'pymongo.network',
        'pymongo.server',
        'pymongo.monitor',
        'pymongo.heartbeat'
    ]
    
    for logger_name in mongodb_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.WARNING)
        logger.propagate = False
