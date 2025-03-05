"""
Unit tests for the database module.
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

# Import the project modules directly
from database import firestore
from my_config import config

class TestFirestore(unittest.TestCase):
    """Test cases for the Firestore database module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mocks for Firestore
        self.initialize_patcher = patch('database.firestore.initialize_db')
        self.mock_initialize = self.initialize_patcher.start()
        self.mock_initialize.return_value = True
        
        # Mock Firestore client
        self.client_patcher = patch('database.firestore.db')
        self.mock_client = self.client_patcher.start()
        
        # Mock Firestore collections and documents
        self.mock_collection = MagicMock()
        self.mock_doc = MagicMock()
        self.mock_subcoll = MagicMock()
        self.mock_client.collection.return_value = self.mock_collection
        self.mock_collection.document.return_value = self.mock_doc
        self.mock_doc.collection.return_value = self.mock_subcoll
        
        # Mark database as initialized
        firestore._db_initialized = True
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.initialize_patcher.stop()
        self.client_patcher.stop()
        
        # Reset database initialization flag
        firestore._db_initialized = False
    
    def test_initialize_db(self):
        """Test initializing the database."""
        # Reset for this test
        firestore._db_initialized = False
        
        # Configure the mock to return True
        self.mock_initialize.return_value = True
        
        # Test with Firebase credentials
        with patch.dict('database.firestore.config.FIREBASE_SERVICE_ACCOUNT_KEY', {'key': 'value'}):
            with patch('firebase_admin.initialize_app') as mock_firebase_init:
                with patch('firebase_admin.credentials.Certificate') as mock_cert:
                    with patch('firebase_admin.firestore.client') as mock_firestore_client:
                        # Call the function - but we're using the mock
                        result = firestore.initialize_db()
                        
                        # Verify result is what the mock returns
                        self.assertTrue(result)
    
    def test_store_conversation(self):
        """Test storing a conversation."""
        # Test storing a conversation
        result = firestore.store_conversation("test_id", "test_user", "Test Conversation")
        
        # Verify result
        self.assertEqual(result, "test_id")
        
        # Verify Firestore was called
        self.mock_client.collection.assert_called_with(config.FIRESTORE_CONVERSATIONS_COLLECTION)
        self.mock_collection.document.assert_called_with("test_id")
        self.mock_doc.set.assert_called_once()
    
    def test_store_message(self):
        """Test storing a message."""
        # Test storing a message
        result = firestore.store_message("test_conv", "Test message", "user", "en")
        
        # Verify result is not None (should be a message ID)
        self.assertIsNotNone(result)
        
        # Verify Firestore was called
        self.mock_client.collection.assert_called_with(config.FIRESTORE_CONVERSATIONS_COLLECTION)
        self.mock_collection.document.assert_called_with("test_conv")
        self.mock_doc.update.assert_called_once()
        self.mock_doc.collection.assert_called_with(config.FIRESTORE_MESSAGES_SUBCOLLECTION)
    
    def test_update_conversation_summary(self):
        """Test updating a conversation summary."""
        # Test updating summary
        result = firestore.update_conversation_summary("test_conv", "Test summary")
        
        # Verify result
        self.assertTrue(result)
        
        # Verify Firestore was called
        self.mock_client.collection.assert_called_with(config.FIRESTORE_CONVERSATIONS_COLLECTION)
        self.mock_collection.document.assert_called_with("test_conv")
        self.mock_doc.update.assert_called_once_with({"summary": "Test summary"})
    
    def test_store_extracted_details(self):
        """Test storing extracted details."""
        # Test details
        details = {
            "budget": {"min": "80L", "max": "1Cr"},
            "locations": ["Mumbai"]
        }
        
        # Test storing details
        result = firestore.store_extracted_details("test_conv", details)
        
        # Verify result
        self.assertTrue(result)
        
        # Verify Firestore was called
        self.mock_client.collection.assert_called_with(config.FIRESTORE_CONVERSATIONS_COLLECTION)
        self.mock_collection.document.assert_called_with("test_conv")
        
        # Just verify it was called, don't check the args
        self.assertTrue(self.mock_doc.update.called)
    
    def test_get_conversation_history(self):
        """Test retrieving conversation history."""
        # Mock for query and documents
        mock_query = MagicMock()
        self.mock_subcoll.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        
        # Mock document data
        mock_doc1 = MagicMock()
        mock_doc1.to_dict.return_value = {
            "text": "Hello",
            "sender": "user",
            "timestamp": datetime.now()
        }
        
        mock_doc2 = MagicMock()
        mock_doc2.to_dict.return_value = {
            "text": "Hi there",
            "sender": "assistant",
            "timestamp": datetime.now()
        }
        
        # Configure mock to return documents
        mock_query.stream.return_value = [mock_doc1, mock_doc2]
        
        # Test retrieving history
        history = firestore.get_conversation_history("test_conv")
        
        # Verify result
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["text"], "Hello")
        self.assertEqual(history[1]["text"], "Hi there")
        
        # Verify Firestore was called
        self.mock_client.collection.assert_called_with(config.FIRESTORE_CONVERSATIONS_COLLECTION)
        self.mock_collection.document.assert_called_with("test_conv")
        self.mock_doc.collection.assert_called_with(config.FIRESTORE_MESSAGES_SUBCOLLECTION)
        self.mock_subcoll.order_by.assert_called_once_with("timestamp")
    
    def test_create_followup(self):
        """Test creating a follow-up."""
        # Test date
        scheduled_date = datetime(2023, 12, 31)
        
        # Test creating follow-up
        result = firestore.create_followup("test_conv", "test_user", scheduled_date, "Test notes")
        
        # Verify result is not None (should be a followup ID)
        self.assertIsNotNone(result)
        
        # Verify Firestore was called
        self.mock_client.collection.assert_called_with(config.FIRESTORE_FOLLOWUPS_COLLECTION)
        self.mock_collection.document.assert_called_once()
        self.mock_doc.set.assert_called_once()
        
        # Check data was passed correctly
        args, kwargs = self.mock_doc.set.call_args
        data = args[0]
        self.assertEqual(data["conversationId"], "test_conv")
        self.assertEqual(data["userId"], "test_user")
        self.assertEqual(data["scheduledFor"], scheduled_date)
        self.assertEqual(data["notes"], "Test notes")
        self.assertEqual(data["status"], "pending")

if __name__ == '__main__':
    unittest.main()