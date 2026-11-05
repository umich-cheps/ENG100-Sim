import logging
import traceback
import cProfile
import pstats
import io
import functools

logger = logging.getLogger(__name__)


def log_errors(func):
    """Decorator to log errors and re-raise exceptions."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            file_name = tb[-1].filename
            line_number = tb[-1].lineno
            error = type(e).__name__
            message = e.args[0]
            logger.error("%s in %s on line %d: %s", error, file_name, line_number, message)
            raise e
    return wrapper


def profile(top_n=10, sort_by='cumulative'):
    """Decorator to profile a function using cProfile.

    Parameters:
        top_n: Number of top entries to display in the profile report.
        sort_by: The attribute to sort the profile stats by 
            (e.g., 'cumulative', 'time', 'calls').

    Notes:
        This decorator must be chained properly after log_errors(), 
            i.e., @log_errors should be the first decorator and @profile 
            should be the second in the list of decorators.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            pr = cProfile.Profile()
            pr.enable()
            result = func(*args, **kwargs)
            pr.disable()
            s = io.StringIO()
            # Use the sort_by argument dynamically
            sort_key = getattr(pstats.SortKey, sort_by.upper(), pstats.SortKey.CUMULATIVE)
            ps = pstats.Stats(pr, stream=s).sort_stats(sort_key)
            ps.print_stats(top_n)
            print(f"Profiling result for {func.__name__}:\n{s.getvalue()}")
            return result
        return wrapper
    return decorator