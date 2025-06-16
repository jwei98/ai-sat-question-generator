"""Configuration settings for SAT Question Generator"""

# Default model to use if not specified
DEFAULT_MODEL = "claude-3-7-sonnet-latest"

def get_default_model():
    """Get the default model"""
    return DEFAULT_MODEL