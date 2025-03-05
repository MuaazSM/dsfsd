"""
Core chatbot functionality for the Real Estate Chatbot.
Includes conversation handling, OpenAI integration, and message processing.
"""
import json
import os
from typing import Dict, List, Optional, Tuple, Any
import openai

# Use the new import paths for LangChain
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.messages import SystemMessage, HumanMessage, AIMessage

# Local imports
import sys
from my_config import config
from config import prompt_template
from database import firestore
from chatbot import message_handler, summarizer

# Set up OpenAI API key
openai.api_key = config.OPENAI_API_KEY

class RealEstateChatbot:
    """Main chatbot class that handles conversations and AI interactions."""
    
    def __init__(self):
        """Initialize the chatbot with necessary components."""
        self.llm = ChatOpenAI(
            model_name=config.DEFAULT_MODEL,
            temperature=config.TEMPERATURE,
            openai_api_key=config.OPENAI_API_KEY
        )
        
        # Create prompt template for the chatbot
        self.system_message = SystemMessage(content=prompt_template.CHATBOT_SYSTEM_PROMPT)
    
    def get_ai_response(self, 
                         messages: List[Dict[str, str]], 
                         user_language: str = "en") -> str:
        """
        Get a response from the AI model.
        
        Args:
            messages: List of message dictionaries with role and content
            user_language: Language code of the user
            
        Returns:
            AI response text
        """
        # Convert dictionary messages to langchain message objects
        langchain_messages = [self.system_message]
        
        for msg in messages:
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=msg["content"]))
        
        try:
            # Get response from the model
            response = self.llm.generate([langchain_messages])
            ai_message = response.generations[0][0].text
            
            return ai_message
        except Exception as e:
            print(f"Error getting AI response: {e}")
            return "I'm sorry, I'm having trouble processing your request right now. Could you try again?"
    
    def process_message(self, 
                         user_message: str, 
                         conversation_id: str, 
                         user_id: str, 
                         conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Process a user message and generate a response.
        
        Args:
            user_message: The user's message text
            conversation_id: ID of the conversation
            user_id: ID of the user
            conversation_history: Optional list of previous messages
            
        Returns:
            Dict containing response and additional information
        """
        if conversation_history is None:
            conversation_history = []
            
        # Detect language
        detected_lang = message_handler.detect_language(user_message)
        
        # Translate to English if needed
        translated_message = user_message
        if detected_lang != "en":
            translated_message = message_handler.translate_text(
                user_message, 
                source_lang=detected_lang, 
                target_lang="en"
            )
        
        # Store user message in history
        conversation_history.append({
            "role": "user",
            "content": translated_message,
            "original_content": user_message,
            "language": detected_lang
        })
        
        # Store in database
        firestore.store_message(
            conversation_id,
            user_message,
            "user",
            detected_lang,
            translated_message if detected_lang != "en" else None
        )
        
        # Format history for AI
        ai_messages = []
        for msg in conversation_history:
            ai_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Get AI response in English
        ai_response_english = self.get_ai_response(ai_messages, "en")
        
        # Translate response if needed
        ai_response_final = ai_response_english
        if detected_lang != "en":
            ai_response_final = message_handler.translate_text(
                ai_response_english,
                source_lang="en",
                target_lang=detected_lang
            )
        
        # Store AI response in history
        conversation_history.append({
            "role": "assistant",
            "content": ai_response_english,
            "original_content": ai_response_final,
            "language": "en"
        })
        
        # Store in database
        firestore.store_message(
            conversation_id,
            ai_response_final,
            "assistant",
            detected_lang,
            ai_response_english if detected_lang != "en" else None
        )
        
        # Extract real estate details
        extracted_details = {}
        if len(conversation_history) >= 2:
            conversation_text = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in conversation_history
            ])
            
            extracted_details = message_handler.extract_details(conversation_text)
            firestore.store_extracted_details(conversation_id, extracted_details)
            
            # Generate summary if conversation is long enough
            summary = None
            if len(conversation_history) >= 4:
                summary = summarizer.generate_summary(conversation_text)
                firestore.update_conversation_summary(conversation_id, summary)
            
            # Generate response suggestions
            response_suggestions = message_handler.generate_response_suggestions(
                conversation_text,
                detected_lang
            )
        else:
            response_suggestions = []
        
        # Return comprehensive response data
        return {
            "response": ai_response_final,
            "language": detected_lang,
            "extracted_details": extracted_details,
            "suggestions": response_suggestions,
            "conversation_history": conversation_history
        }
    
    def start_new_conversation(self, user_id: str, title: Optional[str] = None) -> str:
        """
        Start a new conversation and store it in the database.
        
        Args:
            user_id: ID of the user
            title: Optional title for the conversation
            
        Returns:
            ID of the new conversation
        """
        conversation_id = firestore.store_conversation(
            str(user_id) + "_" + str(os.urandom(4).hex()),
            user_id,
            title
        )
        return conversation_id
    
    def get_conversation_data(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get all data for a conversation.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            Dict with conversation data
        """
        messages = firestore.get_conversation_history(conversation_id)
        summary = firestore.get_conversation_summary(conversation_id)
        details = firestore.get_extracted_details(conversation_id)
        
        return {
            "messages": messages,
            "summary": summary,
            "extracted_details": details
        }


# Singleton instance
chatbot = RealEstateChatbot()