import logging
import os
from datetime import datetime

def setup_logger(log_dir: str = "logs", level=logging.INFO):
    """
    Set up logging configuration
    
    Args:
        log_dir: Directory to store log files
        level: Logging level
        
    Returns:
        Configured logger
    """
    # Create log directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Generate log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"ordertools_{timestamp}.log")
    
    # Configure logging
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Clear existing handlers if any
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger