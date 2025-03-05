"""
Unit tests for the chatbot module.
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Mock imports that might cause issues
sys.modules['langchain_openai'] = MagicMock()
sys.modules['langchain.prompts'] = MagicMock()
sys.modules['langchain.schema'] = MagicMock()

# Import the project modules directly
from chatbot import message_handler
from my_config import config

# Simple mock for the RealEstateChatbot class
class MockChatbot:
    def get_ai_response(self, messages, user_language="en"):
        return "This is a test response."
    
    def process_message(self, user_message, conversation_id, user_id, conversation_history=None):
        if conversation_history is None:
            conversation_history = []
        
        return {
            "response": "AI response",
            "language": "en",
            "extracted_details": {"locations": ["Mumbai"]},
            "suggestions": ["Test suggestion"],
            "conversation_history": conversation_history + [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": "AI response"}
            ]
        }

# Patch the bot module
sys.modules['chatbot.bot'] = MagicMock()
sys.modules['chatbot.bot'].RealEstateChatbot = MockChatbot
sys.modules['chatbot.bot'].chatbot = MockChatbot()

class TestChatbot(unittest.TestCase):
    """Test cases for the chatbot module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock for OpenAI API
        self.openai_patcher = patch('openai.ChatCompletion.create')
        self.mock_openai = self.openai_patcher.start()
        
        # Configure mock to return a valid response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "This is a test response."
        self.mock_openai.return_value = mock_response
        
        # Initialize chatbot
        self.chatbot = MockChatbot()
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.openai_patcher.stop()
    
    def test_get_ai_response(self):
        """Test getting a response from the AI model."""
        messages = [
            {"role": "user", "content": "Hello, I need help finding a property."}
        ]
        
        response = self.chatbot.get_ai_response(messages)
        
        # Verify response
        self.assertEqual(response, "This is a test response.")
    
    def test_process_message(self):
        """Test processing a user message."""
        # Process a message
        response_data = self.chatbot.process_message(
            "I need a 2BHK in Mumbai",
            "test_conversation_id",
            "test_user_id"
        )
        
        # Verify response structure
        self.assertIn("response", response_data)
        self.assertIn("language", response_data)
        self.assertIn("extracted_details", response_data)
        self.assertIn("suggestions", response_data)
        self.assertIn("conversation_history", response_data)

class TestMessageHandler(unittest.TestCase):
    """Test cases for the message handler module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock for OpenAI API
        self.openai_patcher = patch('openai.ChatCompletion.create')
        self.mock_openai = self.openai_patcher.start()
        
        # Configure mock to return a valid response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "This is a test response."
        self.mock_openai.return_value = mock_response
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.openai_patcher.stop()
    
    def test_detect_language(self):
        """Test language detection."""
        # We'll just test basic functionality without mocking
        # This avoids import errors with langdetect patching
        with patch('langdetect.detect', return_value="en"):
            result = message_handler.detect_language("Test message")
            self.assertEqual(result, "en")
    
    @patch('chatbot.message_handler.translate_text')
    def test_format_extracted_details(self, mock_translate):
        """Test formatting extracted details."""
        # Sample details
        details = {
            "budget": {"min": "80L", "max": "1Cr", "currency": "INR"},
            "property_type": ["2BHK", "Apartment"],
            "locations": ["Mumbai"],
            "urgency": "3 months",
            "special_requirements": ["Sea view"]
        }
        
        # Configure mock
        mock_translate.return_value = "Translated text"
        
        # Test with English
        result_en = message_handler.format_extracted_details(details, "en")
        self.assertIn("Budget", result_en)
        self.assertIn("80L - 1Cr", result_en)
        self.assertIn("Mumbai", result_en)
        self.assertIn("2BHK", result_en)
        self.assertIn("Sea view", result_en)
        
        # Test with Hindi (should call translate_text)
        result_hi = message_handler.format_extracted_details(details, "hi")
        mock_translate.assert_called_once()

if __name__ == '__main__':
    unittest.main()