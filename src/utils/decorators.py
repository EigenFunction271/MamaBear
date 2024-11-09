from functools import wraps
import threading
import queue

def timeout(seconds):
    """Timeout decorator for functions."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result_queue = queue.Queue()
            
            def worker():
                try:
                    result = func(*args, **kwargs)
                    result_queue.put(('success', result))
                except Exception as e:
                    result_queue.put(('error', e))
            
            thread = threading.Thread(target=worker)
            thread.daemon = True
            thread.start()
            
            try:
                status, result = result_queue.get(timeout=seconds)
                if status == 'error':
                    raise result
                return result
            except queue.Empty:
                raise TimeoutError(f"Function timed out after {seconds} seconds")
            
        return wrapper
    return decorator