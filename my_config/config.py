"""
Configuration settings for the Real Estate Chatbot application.
Handles environment variables, API keys, and application settings.
"""
import os
import json
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_CLOUD_API_KEY = os.getenv("GOOGLE_CLOUD_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Firebase/Firestore Config
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH")
FIREBASE_SERVICE_ACCOUNT_KEY = {}

# Try to load Firebase credentials either from JSON string or file path
try:
    if os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY"):
        FIREBASE_SERVICE_ACCOUNT_KEY = json.loads(os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY", "{}"))
    elif FIREBASE_CREDENTIALS_PATH and os.path.exists(FIREBASE_CREDENTIALS_PATH):
        with open(FIREBASE_CREDENTIALS_PATH, 'r') as f:
            FIREBASE_SERVICE_ACCOUNT_KEY = json.load(f)
except (json.JSONDecodeError, FileNotFoundError) as e:
    print(f"WARNING: Failed to load Firebase credentials: {e}")

# OpenAI Models
DEFAULT_MODEL = "gpt-4-turbo"
TRANSLATION_MODEL = "gpt-4-turbo"
SUMMARIZATION_MODEL = "gpt-4-turbo"

# Supported Languages
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
    "te": "Telugu"
}

# Application Settings
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
LANGUAGE_DETECTION_CONFIDENCE = float(os.getenv("LANGUAGE_DETECTION_CONFIDENCE", "0.7"))

# UI Settings
CHAINLIT_MAX_HISTORY_LENGTH = 50
CHAINLIT_SHOW_LANGUAGE_INFO = True

# Message Processing
MAX_TOKENS = 4096
TEMPERATURE = 0.7
TOP_P = 1.0
FREQUENCY_PENALTY = 0.0
PRESENCE_PENALTY = 0.0

# Database Settings
FIRESTORE_CONVERSATIONS_COLLECTION = "conversations"
FIRESTORE_MESSAGES_SUBCOLLECTION = "messages"
FIRESTORE_FOLLOWUPS_COLLECTION = "followups"

# Twilio Settings
TWILIO_CALL_TIMEOUT = 300  # seconds

# Check for required credentials and warn if missing
if not OPENAI_API_KEY:
    print("WARNING: OpenAI API key not found. The application may not function correctly.")

if not FIREBASE_SERVICE_ACCOUNT_KEY:
    print("WARNING: Firebase credentials not found. Running without database support.")