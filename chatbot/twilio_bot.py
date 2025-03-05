"""
Twilio voice bot integration for the Real Estate Chatbot.
Allows voice calls to interact with the chatbot.
"""
import os
from typing import Dict, Optional, Any

from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather

# Local imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from my_config import config, prompt_template
from chatbot import bot, message_handler
import openai

# Initialize Twilio client
twilio_client = None

def initialize_twilio_client():
    """Initialize the Twilio client."""
    global twilio_client
    
    if twilio_client:
        return twilio_client
        
    try:
        account_sid = config.TWILIO_ACCOUNT_SID
        auth_token = config.TWILIO_AUTH_TOKEN
        
        if account_sid and auth_token:
            twilio_client = Client(account_sid, auth_token)
            return twilio_client
        else:
            print("Twilio credentials not found.")
            return None
    except Exception as e:
        print(f"Error initializing Twilio client: {e}")
        return None

def generate_voice_response(user_input: str, conversation_id: str) -> str:
    """
    Generate a voice response from the chatbot.
    
    Args:
        user_input: User's spoken input
        conversation_id: ID of the conversation
        
    Returns:
        Text for voice response
    """
    try:
        # Detect language
        detected_lang = message_handler.detect_language(user_input)
        
        # Process with OpenAI directly for voice responses (kept simpler)
        system_message = prompt_template.TWILIO_PROMPT
        
        response = openai.ChatCompletion.create(
            model=config.DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            max_tokens=150,  # Keep responses short for voice
        )
        
        # Get the response content
        ai_response = response.choices[0].message.content.strip()
        
        # Translate if needed
        if detected_lang != "en":
            ai_response = message_handler.translate_text(
                ai_response,
                source_lang="en",
                target_lang=detected_lang
            )
            
        return ai_response
    except Exception as e:
        print(f"Error generating voice response: {e}")
        return "I'm sorry, I couldn't process your request. Please try again."

def create_voice_response(spoken_text: Optional[str] = None, error: bool = False) -> VoiceResponse:
    """
    Create a TwiML response for voice calls.
    
    Args:
        spoken_text: Text to be spoken to the caller
        error: Whether an error occurred
        
    Returns:
        TwiML VoiceResponse object
    """
    response = VoiceResponse()
    
    if error:
        response.say(
            "I'm sorry, we're experiencing technical difficulties. Please try again later.",
            voice="alice"
        )
        response.hangup()
        return response
        
    if not spoken_text:
        # Initial greeting
        response.say(
            "Hello! I'm your real estate assistant. How can I help you with your property search today?",
            voice="alice"
        )
    else:
        # Respond to the caller
        response.say(spoken_text, voice="alice")
    
    # Gather the caller's input
    gather = Gather(
        input="speech",
        action="/twilio/continue",
        method="POST",
        speech_timeout="auto",
        language="en-IN",  # Default to English (India)
        timeout=5
    )
    
    # Add prompt after waiting
    response.say(
        "Is there anything else you'd like to know about real estate properties?",
        voice="alice"
    )
    
    # Add a final message if no response
    response.say(
        "Thank you for calling. Goodbye!",
        voice="alice"
    )
    
    response.hangup()
    return response

def handle_incoming_call():
    """
    Handle an incoming Twilio voice call.
    
    Returns:
        TwiML response for the initial greeting
    """
    # Create a new conversation ID for this call
    conversation_id = f"twilio_call_{os.urandom(4).hex()}"
    
    # Set up the initial TwiML response
    return create_voice_response()

def handle_continue_call(user_input: str, conversation_id: str):
    """
    Handle continuing conversation in a Twilio call.
    
    Args:
        user_input: Transcribed user speech
        conversation_id: ID of the conversation
        
    Returns:
        TwiML response with the chatbot's reply
    """
    try:
        # Generate a response
        chatbot_response = generate_voice_response(user_input, conversation_id)
        
        # Create TwiML with the response
        return create_voice_response(chatbot_response)
    except Exception as e:
        print(f"Error handling Twilio call continuation: {e}")
        return create_voice_response(error=True)

def make_outbound_call(to_number: str, from_number: Optional[str] = None) -> bool:
    """
    Make an outbound call using Twilio.
    
    Args:
        to_number: Phone number to call
        from_number: Phone number to call from (defaults to configured number)
        
    Returns:
        True if successful, False otherwise
    """
    client = initialize_twilio_client()
    if not client:
        return False
        
    try:
        # Use configured from number if not specified
        if not from_number:
            from_number = config.TWILIO_PHONE_NUMBER
            
        # Make the call
        call = client.calls.create(
            to=to_number,
            from_=from_number,
            url="https://your-webhook-url.com/twilio/outbound",  # Your webhook URL
            timeout=config.TWILIO_CALL_TIMEOUT
        )
        
        # Return success if call SID is returned
        return bool(call.sid)
    except Exception as e:
        print(f"Error making outbound call: {e}")
        return False