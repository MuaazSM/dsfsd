"""
Unit tests for the UI functionality.
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock, AsyncMock

# Create Mock classes that behave like the real ones
class MockAction:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class MockSelect:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

# Create chainlit mock
cl_mock = MagicMock()
cl_mock.Action = MockAction
cl_mock.Select = MockSelect
cl_mock.Message = MagicMock
sys.modules['chainlit'] = cl_mock

# Import the project modules directly
from chainlit_ui import utils
from my_config import config

class TestChainlitUtils(unittest.TestCase):
    """Test cases for Chainlit utility functions."""
    
    def test_create_language_selector(self):
        """Test creating language selector elements."""
        selector = utils.create_language_selector()
        
        # Verify selector structure
        self.assertIsInstance(selector, list)
        self.assertEqual(len(selector), 1)
        
        # Check selector properties
        self.assertEqual(selector[0].id, "language_selector")
        self.assertEqual(selector[0].label, "Select Language")
        
        # Check language options
        self.assertGreaterEqual(len(selector[0].values), 4)  # At least 4 languages
        
        # Verify language codes
        lang_values = [opt["value"] for opt in selector[0].values]
        self.assertIn("en", lang_values)
        self.assertIn("hi", lang_values)
        self.assertIn("mr", lang_values)
        self.assertIn("te", lang_values)
    
    def test_create_voice_button(self):
        """Test creating voice input button."""
        # Test with English
        button_en = utils.create_voice_button("en")
        
        # Verify button properties
        self.assertEqual(button_en.name, "voice_input")
        self.assertEqual(button_en.value, "en")
        self.assertEqual(button_en.label, "🎤 Voice Input")
        self.assertIn("English", button_en.description)
        
        # Test with Hindi
        button_hi = utils.create_voice_button("hi")
        self.assertEqual(button_hi.value, "hi")
        self.assertIn("Hindi", button_hi.description)
    
    def test_format_property_data(self):
        """Test formatting property data."""
        property_data = {
            "id": "prop123",
            "title": "Luxury Apartment",
            "location": "Mumbai, Maharashtra",
            "price": "₹1.2 Cr",
            "bedrooms": 3,
            "bathrooms": 2,
            "area": "1500 sq.ft."
        }
        
        formatted = utils.format_property_data(property_data)
        
        # Verify formatting - matching the exact format used
        self.assertIn("Luxury Apartment", formatted)
        self.assertIn("Mumbai", formatted)
        self.assertIn("**Bedrooms:** 3", formatted)  # Match markdown formatting
        self.assertIn("₹1.2 Cr", formatted)
    
    def test_format_extracted_details(self):
        """Test formatting extracted details."""
        details = {
            "budget": {"min": "80L", "max": "1.2Cr", "currency": "INR"},
            "property_type": ["2BHK", "Apartment"],
            "locations": ["Mumbai", "Thane"],
            "urgency": "3 months",
            "special_requirements": ["Sea view", "Parking"]
        }
        
        formatted = utils.format_extracted_details(details)
        
        # Verify formatting
        self.assertIn("Budget", formatted)
        self.assertIn("80L - 1.2Cr", formatted)
        self.assertIn("Mumbai", formatted)
        self.assertIn("2BHK", formatted)
        self.assertIn("3 months", formatted)
        self.assertIn("Sea view", formatted)
    
    def test_create_response_suggestions_buttons(self):
        """Test creating response suggestion buttons."""
        suggestions = [
            "I can help you find properties in Mumbai.",
            "What's your budget range?",
            "Are you looking for any specific amenities?"
        ]
        
        # Call the function
        buttons = utils.create_response_suggestions_buttons(suggestions)
        
        # Verify buttons
        self.assertEqual(len(buttons), 3)
        
        # Test button properties directly without comparing objects
        self.assertEqual(buttons[0].name, "suggestion_0")
        self.assertEqual(buttons[0].value, suggestions[0])
        self.assertEqual(buttons[1].name, "suggestion_1")
        self.assertEqual(buttons[2].name, "suggestion_2")
    
    def test_create_notification(self):
        """Test creating notification."""
        notification = utils.create_notification("Test message", "info")
        
        # Verify notification
        self.assertEqual(notification["title"], "Real Estate Assistant")
        self.assertEqual(notification["content"], "Test message")
        self.assertEqual(notification["type"], "info")

if __name__ == '__main__':
    unittest.main()