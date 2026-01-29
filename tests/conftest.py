# Basic test configuration
import pytest
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def mock_environment():
    """Mock environment variables for testing"""
    os.environ.update({
        'OPENAI_API_KEY': 'test_key',
        'NEWSAPI_KEY': 'test_key', 
        'TAVILY_API_KEY': 'test_key',
        'ENVIRONMENT': 'test'
    })
    yield
    # Cleanup if needed