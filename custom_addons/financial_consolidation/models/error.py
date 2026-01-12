import logging
from functools import wraps

_logger = logging.getLogger(__name__)


def log_error_decorator(module_name):
    """Decorator to log errors with module context."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                _logger.error(f"[{module_name}] Error in {func.__name__}: {str(e)}", exc_info=True)
                raise
        return wrapper
    return decorator


class ErrorHandler:
    """Centralized error handling for consolidation module.

    This class exposes methods used across the module. Several places in the
    codebase call error.handler.handle_exception(module, function, exception) so
    we keep a compatible signature while also providing an object-oriented
    interface for model-based handlers.
    """

    @staticmethod
    def log_error(module_name, function_name, error_message, exc_info=False):
        """Log an error message."""
        _logger.error(f"[{module_name}] Error in {function_name}: {error_message}", exc_info=exc_info)

    @staticmethod
    def log_warning(module_name, function_name, warning_message):
        """Log a warning message."""
        _logger.warning(f"[{module_name}] Warning in {function_name}: {warning_message}")

    @staticmethod
    def log_info(module_name, function_name, info_message):
        """Log an info message."""
        _logger.info(f"[{module_name}] {function_name}: {info_message}")

    @staticmethod
    def handle_exception(module_name, function_name, exception, context=None, reraise=True):
        """Handle an exception with context.

        This signature keeps backward compatibility with multiple call sites
        that pass (module_name, function_name, exception). It returns a dict
        with details about the error so callers can inspect recommendations.
        """
        import traceback
        from datetime import datetime

        error_data = {
            'module': module_name,
            'function': function_name,
            'exception_type': type(exception).__name__,
            'message': str(exception),
            'context': context or {},
            'traceback': traceback.format_exc(),
            'timestamp': str(datetime.utcnow()),
        }

        _logger.error(f"Exception in {module_name}.{function_name}: {str(exception)}", exc_info=True)

        # Provide a minimal set of recommendations based on keywords
        recommendations = []
        msg = str(exception).lower()
        if 'timeout' in msg or 'connection' in msg:
            recommendations.append('Check network/connectivity or increase timeouts')
        if 'accesserror' in msg.lower() or 'permission' in msg.lower():
            recommendations.append('Verify user permissions and run operation with appropriate rights')
        if 'validation' in msg.lower() or 'unbalanced' in msg.lower():
            recommendations.append('Run data validation and review mapping configuration')

        error_data['recommendations'] = recommendations

        if reraise:
            raise exception

        return error_data


# Create an instance for backward compatibility with existing imports
handler = ErrorHandler()


# Also expose a lightweight decorator for modules that import error.log_error_decorator
# (keeps prior behavior and avoids breaking existing decorators)
