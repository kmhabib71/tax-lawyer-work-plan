"""
Logging utilities for AI Tax Lawyer Bangladesh application.
"""
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
import sys
from config.settings import settings

def setup_logging(
    log_level: str = None,
    log_file: str = None,
    enable_console: bool = True,
    enable_file: bool = True
) -> logging.Logger:
    """
    Setup comprehensive logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Log file path
        enable_console: Enable console logging
        enable_file: Enable file logging
    
    Returns:
        Configured logger instance
    """
    # Use settings defaults if not provided
    log_level = log_level or settings.log_level
    log_file = log_file or settings.log_file
    
    # Create logs directory
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s:%(lineno)-4d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
    
    # File handler with rotation
    if enable_file:
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
    
    # Error handler for critical issues
    error_log_path = log_path.parent / f"error_{log_path.name}"
    error_handler = logging.handlers.RotatingFileHandler(
        filename=error_log_path,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # Performance handler for agent metrics
    perf_log_path = log_path.parent / f"performance_{log_path.name}"
    perf_handler = logging.handlers.RotatingFileHandler(
        filename=perf_log_path,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    perf_handler.setLevel(logging.INFO)
    perf_handler.setFormatter(detailed_formatter)
    
    # Create performance logger
    perf_logger = logging.getLogger('performance')
    perf_logger.addHandler(perf_handler)
    perf_logger.setLevel(logging.INFO)
    perf_logger.propagate = False
    
    return root_logger

def get_agent_logger(agent_name: str) -> logging.Logger:
    """
    Get a specialized logger for agents.
    
    Args:
        agent_name: Name of the agent
    
    Returns:
        Configured agent logger
    """
    logger = logging.getLogger(f"agent.{agent_name}")
    return logger

def get_performance_logger() -> logging.Logger:
    """Get performance metrics logger."""
    return logging.getLogger('performance')

def log_agent_performance(
    agent_name: str,
    query: str,
    response_time_ms: int,
    tokens_used: int = 0,
    cache_hit: bool = False,
    success: bool = True,
    error_message: str = None
):
    """
    Log agent performance metrics.
    
    Args:
        agent_name: Name of the agent
        query: User query
        response_time_ms: Response time in milliseconds
        tokens_used: Number of tokens used
        cache_hit: Whether cache was hit
        success: Whether operation was successful
        error_message: Error message if failed
    """
    perf_logger = get_performance_logger()
    
    log_data = {
        'agent': agent_name,
        'response_time_ms': response_time_ms,
        'tokens_used': tokens_used,
        'cache_hit': cache_hit,
        'success': success,
        'query_length': len(query),
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if error_message:
        log_data['error'] = error_message
    
    if success:
        perf_logger.info(f"PERFORMANCE: {log_data}")
    else:
        perf_logger.error(f"PERFORMANCE_ERROR: {log_data}")

def log_database_operation(
    operation: str,
    collection: str,
    duration_ms: int,
    success: bool = True,
    error_message: str = None
):
    """
    Log database operation metrics.
    
    Args:
        operation: Type of operation (insert, update, find, etc.)
        collection: Database collection name
        duration_ms: Operation duration in milliseconds
        success: Whether operation was successful
        error_message: Error message if failed
    """
    db_logger = logging.getLogger('database')
    
    log_data = {
        'operation': operation,
        'collection': collection,
        'duration_ms': duration_ms,
        'success': success,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if error_message:
        log_data['error'] = error_message
    
    if success:
        db_logger.info(f"DB_OPERATION: {log_data}")
    else:
        db_logger.error(f"DB_ERROR: {log_data}")

def log_ragflow_operation(
    operation: str,
    collection: str,
    query: str,
    results_count: int,
    duration_ms: int,
    success: bool = True,
    error_message: str = None
):
    """
    Log RAGFlow operation metrics.
    
    Args:
        operation: Type of operation (search, embed, etc.)
        collection: RAGFlow collection name
        query: Search query
        results_count: Number of results returned
        duration_ms: Operation duration in milliseconds
        success: Whether operation was successful
        error_message: Error message if failed
    """
    ragflow_logger = logging.getLogger('ragflow')
    
    log_data = {
        'operation': operation,
        'collection': collection,
        'query_length': len(query),
        'results_count': results_count,
        'duration_ms': duration_ms,
        'success': success,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if error_message:
        log_data['error'] = error_message
    
    if success:
        ragflow_logger.info(f"RAGFLOW_OPERATION: {log_data}")
    else:
        ragflow_logger.error(f"RAGFLOW_ERROR: {log_data}")

def log_calculation_metrics(
    calculation_type: str,
    input_complexity: str,
    calculation_time_ms: int,
    rule_engine_time_ms: int,
    llm_time_ms: int,
    tokens_used: int,
    accuracy_score: float,
    success: bool = True
):
    """
    Log tax calculation metrics.
    
    Args:
        calculation_type: Type of calculation
        input_complexity: Simple, moderate, complex
        calculation_time_ms: Total calculation time
        rule_engine_time_ms: Rule engine time
        llm_time_ms: LLM processing time
        tokens_used: Tokens used by LLM
        accuracy_score: Confidence score
        success: Whether calculation succeeded
    """
    calc_logger = logging.getLogger('calculations')
    
    log_data = {
        'calculation_type': calculation_type,
        'input_complexity': input_complexity,
        'total_time_ms': calculation_time_ms,
        'rule_engine_time_ms': rule_engine_time_ms,
        'llm_time_ms': llm_time_ms,
        'tokens_used': tokens_used,
        'accuracy_score': accuracy_score,
        'success': success,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    calc_logger.info(f"CALCULATION_METRICS: {log_data}")

class ContextualLogger:
    """Logger with contextual information."""
    
    def __init__(self, name: str, context: dict = None):
        self.logger = logging.getLogger(name)
        self.context = context or {}
    
    def _format_message(self, message: str) -> str:
        """Format message with context."""
        if self.context:
            context_str = " | ".join([f"{k}={v}" for k, v in self.context.items()])
            return f"[{context_str}] {message}"
        return message
    
    def debug(self, message: str, **kwargs):
        self.logger.debug(self._format_message(message), **kwargs)
    
    def info(self, message: str, **kwargs):
        self.logger.info(self._format_message(message), **kwargs)
    
    def warning(self, message: str, **kwargs):
        self.logger.warning(self._format_message(message), **kwargs)
    
    def error(self, message: str, **kwargs):
        self.logger.error(self._format_message(message), **kwargs)
    
    def critical(self, message: str, **kwargs):
        self.logger.critical(self._format_message(message), **kwargs)
    
    def add_context(self, **kwargs):
        """Add context to logger."""
        self.context.update(kwargs)
    
    def remove_context(self, *keys):
        """Remove context keys."""
        for key in keys:
            self.context.pop(key, None)

# Initialize logging on module import
if not logging.getLogger().handlers:
    setup_logging()