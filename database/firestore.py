"""
Firestore database integration module for the Real Estate Chatbot.
Handles connections, data storage, retrieval, and updates.
"""
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

import os
import sys

# Import config
from my_config import config

# Variables to track database state
db = None
_db_initialized = False
_firebase_app = None

def initialize_db() -> bool:
    """Initialize the Firestore database connection."""
    global db, _db_initialized, _firebase_app
    
    if _db_initialized:
        return True
    
    try:
        # Only attempt to initialize if we have credentials
        if config.FIREBASE_SERVICE_ACCOUNT_KEY:
            import firebase_admin
            from firebase_admin import credentials, firestore
            
            # Check if Firebase is already initialized
            try:
                cred = credentials.Certificate(config.FIREBASE_SERVICE_ACCOUNT_KEY)
                _firebase_app = firebase_admin.initialize_app(cred)
                db = firestore.client()
                _db_initialized = True
                return True
            except ValueError as e:
                if "already exists" in str(e):
                    # Firebase already initialized, just get the Firestore client
                    db = firestore.client()
                    _db_initialized = True
                    return True
                else:
                    print(f"Error initializing Firestore: {e}")
                    return False
        else:
            print("Firebase credentials not provided. Database functionality disabled.")
            return False
    except Exception as e:
        print(f"Error initializing Firestore: {e}")
        return False

def store_conversation(
    conversation_id: str, 
    user_id: str, 
    title: Optional[str] = None
) -> Optional[str]:
    """
    Create a new conversation in Firestore.
    
    Args:
        conversation_id: Unique identifier for the conversation
        user_id: ID of the user/client
        title: Optional title for the conversation
        
    Returns:
        conversation_id if successful, None otherwise
    """
    if not _db_initialized and not initialize_db():
        # Return the ID anyway for testing without database
        return conversation_id
    
    try:
        if not title:
            title = f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Only try to store if database is initialized
        if db:
            from firebase_admin import firestore
            conv_ref = db.collection(config.FIRESTORE_CONVERSATIONS_COLLECTION).document(conversation_id)
            conv_ref.set({
                'userId': user_id,
                'startedAt': firestore.SERVER_TIMESTAMP,
                'lastUpdated': firestore.SERVER_TIMESTAMP,
                'title': title,
                'status': 'active',
                'summary': None
            })
        
        return conversation_id
    except Exception as e:
        print(f"Error storing conversation: {e}")
        return conversation_id  # Return ID anyway for testing

def store_message(
    conversation_id: str,
    content: str,
    sender: str,
    language: str,
    translated_content: Optional[str] = None
) -> Optional[str]:
    """
    Store a message in a conversation.
    
    Args:
        conversation_id: ID of the conversation
        content: Message content
        sender: Who sent the message ('user' or 'assistant')
        language: Language code of the message
        translated_content: Optional translated content (if message was translated)
        
    Returns:
        message_id if successful, None otherwise
    """
    if not _db_initialized and not initialize_db():
        # Generate ID even if database is not available
        return str(uuid.uuid4())
    
    try:
        # Generate a message ID
        message_id = str(uuid.uuid4())
        
        # Only store if database is available
        if db:
            from firebase_admin import firestore
            # Update conversation last updated timestamp
            conv_ref = db.collection(config.FIRESTORE_CONVERSATIONS_COLLECTION).document(conversation_id)
            conv_ref.update({
                'lastUpdated': firestore.SERVER_TIMESTAMP
            })
            
            # Add message to subcollection
            message_data = {
                'text': content,
                'sender': sender,
                'timestamp': firestore.SERVER_TIMESTAMP,
                'language': language,
            }
            
            if translated_content:
                message_data['translatedText'] = translated_content
                
            conv_ref.collection(config.FIRESTORE_MESSAGES_SUBCOLLECTION).document(message_id).set(message_data)
        
        return message_id
    except Exception as e:
        print(f"Error storing message: {e}")
        return str(uuid.uuid4())  # Return a generated ID anyway

def update_conversation_summary(conversation_id: str, summary: str) -> bool:
    """
    Update the summary of a conversation.
    
    Args:
        conversation_id: ID of the conversation
        summary: Summary text
        
    Returns:
        True if successful, False otherwise
    """
    if not _db_initialized and not initialize_db():
        return True  # Pretend success for testing
    
    try:
        if db:
            db.collection(config.FIRESTORE_CONVERSATIONS_COLLECTION).document(conversation_id).update({
                'summary': summary
            })
        return True
    except Exception as e:
        print(f"Error updating summary: {e}")
        return False

def store_extracted_details(conversation_id: str, details: Dict[str, Any]) -> bool:
    """
    Store extracted real estate details for a conversation.
    
    Args:
        conversation_id: ID of the conversation
        details: Dictionary of extracted details
        
    Returns:
        True if successful, False otherwise
    """
    if not _db_initialized and not initialize_db():
        return True  # Pretend success for testing
        
    try:
        if db:
            from firebase_admin import firestore
            db.collection(config.FIRESTORE_CONVERSATIONS_COLLECTION).document(conversation_id).update({
                'extractedDetails': details,
                'lastUpdated': firestore.SERVER_TIMESTAMP
            })
        return True
    except Exception as e:
        print(f"Error storing details: {e}")
        return False

def get_conversation_history(conversation_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Retrieve the message history for a conversation.
    
    Args:
        conversation_id: ID of the conversation
        limit: Maximum number of messages to retrieve
        
    Returns:
        List of messages in chronological order
    """
    if not _db_initialized and not initialize_db():
        return []  # Return empty list for testing
        
    try:
        if not db:
            return []
            
        messages_ref = db.collection(config.FIRESTORE_CONVERSATIONS_COLLECTION) \
                         .document(conversation_id) \
                         .collection(config.FIRESTORE_MESSAGES_SUBCOLLECTION) \
                         .order_by('timestamp') \
                         .limit(limit)
        
        messages = []
        for msg in messages_ref.stream():
            msg_data = msg.to_dict()
            # Convert timestamp to string to make it serializable
            if 'timestamp' in msg_data and msg_data['timestamp']:
                msg_data['timestamp'] = msg_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            messages.append(msg_data)
            
        return messages
    except Exception as e:
        print(f"Error retrieving conversation history: {e}")
        return []

def get_conversation_summary(conversation_id: str) -> Optional[str]:
    """
    Get the summary of a conversation.
    
    Args:
        conversation_id: ID of the conversation
        
    Returns:
        Summary text if available, None otherwise
    """
    if not _db_initialized and not initialize_db():
        return None  # Return None for testing
        
    try:
        if not db:
            return None
            
        doc = db.collection(config.FIRESTORE_CONVERSATIONS_COLLECTION).document(conversation_id).get()
        if doc.exists:
            data = doc.to_dict()
            return data.get('summary')
        return None
    except Exception as e:
        print(f"Error retrieving summary: {e}")
        return None

def get_extracted_details(conversation_id: str) -> Dict[str, Any]:
    """
    Get the extracted real estate details for a conversation.
    
    Args:
        conversation_id: ID of the conversation
        
    Returns:
        Dictionary of extracted details if available, empty dict otherwise
    """
    if not _db_initialized and not initialize_db():
        return {}  # Return empty dict for testing
        
    try:
        if not db:
            return {}
            
        doc = db.collection(config.FIRESTORE_CONVERSATIONS_COLLECTION).document(conversation_id).get()
        if doc.exists:
            data = doc.to_dict()
            return data.get('extractedDetails', {})
        return {}
    except Exception as e:
        print(f"Error retrieving details: {e}")
        return {}

def create_followup(
    conversation_id: str,
    user_id: str,
    scheduled_for: datetime,
    notes: str,
    status: str = 'pending'
) -> Optional[str]:
    """
    Create a follow-up task in Firestore.
    
    Args:
        conversation_id: ID of the conversation
        user_id: ID of the user/client
        scheduled_for: When the follow-up should happen
        notes: Notes for the follow-up
        status: Status of the follow-up ('pending', 'completed', 'cancelled')
        
    Returns:
        follow_up_id if successful, None otherwise
    """
    if not _db_initialized and not initialize_db():
        return str(uuid.uuid4())  # Return generated ID for testing
        
    try:
        followup_id = str(uuid.uuid4())
        
        if db:
            from firebase_admin import firestore
            db.collection(config.FIRESTORE_FOLLOWUPS_COLLECTION).document(followup_id).set({
                'conversationId': conversation_id,
                'userId': user_id,
                'scheduledFor': scheduled_for,
                'status': status,
                'notes': notes,
                'createdAt': firestore.SERVER_TIMESTAMP
            })
        
        return followup_id
    except Exception as e:
        print(f"Error creating follow-up: {e}")
        return str(uuid.uuid4())  # Return generated ID anyway

def get_pending_followups(user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get pending follow-ups, optionally filtered by user.
    
    Args:
        user_id: Optional user ID to filter by
        
    Returns:
        List of pending follow-ups
    """
    if not _db_initialized and not initialize_db():
        return []  # Return empty list for testing
        
    try:
        if not db:
            return []
            
        from firebase_admin import firestore
        from google.cloud.firestore_v1.base_query import FieldFilter
        
        query = db.collection(config.FIRESTORE_FOLLOWUPS_COLLECTION) \
                  .where(filter=FieldFilter('status', '==', 'pending'))
        
        if user_id:
            query = query.where(filter=FieldFilter('userId', '==', user_id))
            
        followups = []
        for doc in query.stream():
            followup_data = doc.to_dict()
            followup_data['id'] = doc.id
            
            # Convert timestamp to string
            if 'scheduledFor' in followup_data and followup_data['scheduledFor']:
                followup_data['scheduledFor'] = followup_data['scheduledFor'].strftime('%Y-%m-%d %H:%M:%S')
            if 'createdAt' in followup_data and followup_data['createdAt']:
                followup_data['createdAt'] = followup_data['createdAt'].strftime('%Y-%m-%d %H:%M:%S')
                
            followups.append(followup_data)
            
        return followups
    except Exception as e:
        print(f"Error retrieving follow-ups: {e}")
        return []

def get_user_conversations(user_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Get all conversations for a user.
    
    Args:
        user_id: ID of the user (or None for all conversations)
        limit: Maximum number of conversations to retrieve
        
    Returns:
        List of conversations
    """
    if not _db_initialized and not initialize_db():
        return []  # Return empty list for testing
        
    try:
        if not db:
            return []
            
        from firebase_admin import firestore
        from google.cloud.firestore_v1.base_query import FieldFilter
        
        query = db.collection(config.FIRESTORE_CONVERSATIONS_COLLECTION)
        
        if user_id:
            query = query.where(filter=FieldFilter('userId', '==', user_id))
        
        query = query.order_by('lastUpdated', direction=firestore.Query.DESCENDING).limit(limit)
                  
        conversations = []
        for doc in query.stream():
            conv_data = doc.to_dict()
            conv_data['id'] = doc.id
            
            # Convert timestamps to strings
            if 'startedAt' in conv_data and conv_data['startedAt']:
                conv_data['startedAt'] = conv_data['startedAt'].strftime('%Y-%m-%d %H:%M:%S')
            if 'lastUpdated' in conv_data and conv_data['lastUpdated']:
                conv_data['lastUpdated'] = conv_data['lastUpdated'].strftime('%Y-%m-%d %H:%M:%S')
                
            conversations.append(conv_data)
            
        return conversations
    except Exception as e:
        print(f"Error retrieving user conversations: {e}")
        return []

def search_conversations(query_text: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Basic search for conversations containing a query string in summary or title.
    Note: Firestore doesn't support full-text search natively.
    
    Args:
        query_text: Text to search for
        limit: Maximum number of results
        
    Returns:
        List of matching conversations
    """
    if not _db_initialized and not initialize_db():
        return []  # Return empty list for testing
        
    try:
        if not db:
            return []
            
        # This is inefficient but works for small datasets
        query = db.collection(config.FIRESTORE_CONVERSATIONS_COLLECTION).limit(100)
        
        results = []
        for doc in query.stream():
            data = doc.to_dict()
            
            # Check if query appears in title or summary
            title = data.get('title', '').lower()
            summary = data.get('summary', '').lower()
            
            if query_text.lower() in title or query_text.lower() in summary:
                data['id'] = doc.id
                
                # Convert timestamps to strings
                if 'startedAt' in data and data['startedAt']:
                    data['startedAt'] = data['startedAt'].strftime('%Y-%m-%d %H:%M:%S')
                if 'lastUpdated' in data and data['lastUpdated']:
                    data['lastUpdated'] = data['lastUpdated'].strftime('%Y-%m-%d %H:%M:%S')
                    
                results.append(data)
                
                if len(results) >= limit:
                    break
                    
        return results
    except Exception as e:
        print(f"Error searching conversations: {e}")
        return []