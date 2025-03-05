"""
Speech-to-Text functionality for the Real Estate Chatbot.
Uses Google Cloud Speech-to-Text API for multilingual transcription.
"""
import os
import io
import base64
from typing import Optional

from google.cloud import speech
from google.cloud.speech import RecognitionConfig, RecognitionAudio
from google.oauth2 import service_account

# Local imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from my_config import config
from chatbot import message_handler

# Map of language codes for Google Speech-to-Text
LANGUAGE_CODE_MAP = {
    "en": "en-IN",  # English (India)
    "hi": "hi-IN",  # Hindi
    "mr": "mr-IN",  # Marathi
    "te": "te-IN",  # Telugu
}

# Initialize Google Cloud Speech client
speech_client = None

def initialize_speech_client():
    """Initialize the Google Cloud Speech-to-Text client."""
    global speech_client
    
    if speech_client:
        return speech_client
        
    try:
        if config.FIREBASE_SERVICE_ACCOUNT_KEY:
            credentials = service_account.Credentials.from_service_account_info(
                config.FIREBASE_SERVICE_ACCOUNT_KEY,
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            speech_client = speech.SpeechClient(credentials=credentials)
        else:
            speech_client = speech.SpeechClient()
            
        return speech_client
    except Exception as e:
        print(f"Error initializing Speech-to-Text client: {e}")
        return None

def transcribe_audio(audio_content: bytes, language_hint: Optional[str] = None) -> str:
    """
    Transcribe audio using Google Cloud Speech-to-Text.
    
    Args:
        audio_content: Audio data as bytes
        language_hint: Optional language hint code
        
    Returns:
        Transcribed text
    """
    client = initialize_speech_client()
    if not client:
        return "Speech recognition service unavailable."
        
    try:
        # Create RecognitionAudio object
        audio = RecognitionAudio(content=audio_content)
        
        # Determine language(s) to use
        if language_hint and language_hint in LANGUAGE_CODE_MAP:
            language_code = LANGUAGE_CODE_MAP[language_hint]
            config = RecognitionConfig(
                encoding=RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=language_code,
                enable_automatic_punctuation=True,
                model="default"
            )
        else:
            # If no language hint, try to auto-detect between supported languages
            config = RecognitionConfig(
                encoding=RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="en-IN",  # Primary language
                alternative_language_codes=[
                    "hi-IN", "mr-IN", "te-IN"
                ],
                enable_automatic_punctuation=True,
                model="default"
            )
            
        # Perform speech recognition
        response = client.recognize(config=config, audio=audio)
        
        # Extract transcription
        transcript = ""
        for result in response.results:
            transcript += result.alternatives[0].transcript
            
        return transcript.strip()
    except Exception as e:
        print(f"Speech-to-Text error: {e}")
        return "Error processing audio."

def process_audio_base64(audio_base64: str, language_hint: Optional[str] = None) -> str:
    """
    Process base64-encoded audio and return transcription.
    
    Args:
        audio_base64: Base64-encoded audio data
        language_hint: Optional language hint code
        
    Returns:
        Transcribed text
    """
    try:
        # Decode base64 data
        if "," in audio_base64:
            # Handle data URLs (e.g., "data:audio/webm;base64,...")
            audio_base64 = audio_base64.split(",", 1)[1]
            
        audio_content = base64.b64decode(audio_base64)
        
        # Transcribe the audio
        transcription = transcribe_audio(audio_content, language_hint)
        
        # If no language hint was provided, detect language from the transcription
        if not language_hint and transcription:
            detected_lang = message_handler.detect_language(transcription)
            
            # If detected language is different from what Google might have used,
            # try again with the specific language
            if detected_lang in LANGUAGE_CODE_MAP and detected_lang != "en":
                transcription = transcribe_audio(audio_content, detected_lang)
                
        return transcription
    except Exception as e:
        print(f"Error processing audio base64: {e}")
        return "Error processing audio."