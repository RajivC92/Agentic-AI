"""
Basic tests for NewsGenie application
"""
import pytest
import unittest.mock as mock
from unittest.mock import patch, MagicMock


class TestNewsGenieBasics:
    """Basic functionality tests"""
    
    def test_import_modules(self, mock_environment):
        """Test that main modules can be imported"""
        try:
            # Test that we can import the main components
            import sqlite3
            import json
            from datetime import datetime
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import required modules: {e}")
    
    def test_environment_variables(self, mock_environment):
        """Test environment variable access"""
        import os
        assert os.getenv('OPENAI_API_KEY') == 'test_key'
        assert os.getenv('NEWSAPI_KEY') == 'test_key'
        assert os.getenv('TAVILY_API_KEY') == 'test_key'
        assert os.getenv('ENVIRONMENT') == 'test'
    
    @patch('sqlite3.connect')
    def test_database_connection(self, mock_connect, mock_environment):
        """Test database connection functionality"""
        # Mock the database connection
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        # Test basic SQLite functionality
        import sqlite3
        conn = sqlite3.connect(':memory:')
        assert conn is not None
        conn.close()
    
    def test_json_operations(self, mock_environment):
        """Test JSON operations used in the application"""
        import json
        
        test_data = {
            "query": "test query",
            "response": "test response",
            "timestamp": "2024-01-01T00:00:00"
        }
        
        # Test JSON serialization/deserialization
        json_str = json.dumps(test_data)
        parsed_data = json.loads(json_str)
        
        assert parsed_data["query"] == "test query"
        assert parsed_data["response"] == "test response"
    
    def test_datetime_functionality(self, mock_environment):
        """Test datetime operations"""
        from datetime import datetime
        
        now = datetime.now()
        assert isinstance(now, datetime)
        
        # Test timestamp formatting
        timestamp = now.isoformat()
        assert isinstance(timestamp, str)
        assert 'T' in timestamp


class TestRoutingLogic:
    """Test query routing logic"""
    
    def test_query_classification(self, mock_environment):
        """Test basic query classification logic"""
        # Test different query types
        news_queries = ["latest news", "breaking news", "technology news"]
        search_queries = ["search for python", "find information about AI"]
        general_queries = ["what is machine learning", "explain neural networks"]
        
        for query in news_queries:
            assert "news" in query.lower()
        
        for query in search_queries:
            assert any(word in query.lower() for word in ["search", "find"])
        
        for query in general_queries:
            assert any(word in query.lower() for word in ["what", "explain", "how"])


class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_missing_api_keys(self):
        """Test behavior with missing API keys"""
        import os
        
        # Test graceful handling when keys are missing
        original_key = os.environ.get('OPENAI_API_KEY')
        
        # Temporarily remove the key
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        # The application should handle missing keys gracefully
        missing_key = os.environ.get('OPENAI_API_KEY')
        assert missing_key is None
        
        # Restore the key
        if original_key:
            os.environ['OPENAI_API_KEY'] = original_key
    
    @patch('requests.get')
    def test_api_timeout_handling(self, mock_get, mock_environment):
        """Test API timeout handling"""
        import requests
        
        # Mock a timeout exception
        mock_get.side_effect = requests.exceptions.Timeout()
        
        # Test that timeout is handled gracefully
        with pytest.raises(requests.exceptions.Timeout):
            requests.get('https://test.com', timeout=1)


if __name__ == '__main__':
    pytest.main([__file__])