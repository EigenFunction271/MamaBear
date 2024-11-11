import streamlit as st
from contextlib import contextmanager
from threading import current_thread
import streamlit.runtime.scriptrunner as scriptrunner

@contextmanager
def maintain_streamlit_context():
    """Maintain Streamlit's script context across threads."""
    try:
        # Get the current context
        ctx = scriptrunner.get_script_run_ctx()
        if ctx:
            # Store the context for the current thread
            scriptrunner.add_script_run_ctx(ctx)
        yield
    finally:
        # Clean up is handled automatically by Streamlit
        pass

def with_streamlit_context(func):
    """Decorator to maintain Streamlit context in threaded functions."""
    def wrapper(*args, **kwargs):
        with maintain_streamlit_context():
            return func(*args, **kwargs)
    return wrapper