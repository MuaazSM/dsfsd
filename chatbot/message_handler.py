"""
Message handling functionality for the Real Estate Chatbot.
Includes language detection, translation, detail extraction, and suggestion generation.
"""
import json
import re
from typing import Dict, List, Any, Optional

import openai
from langdetect import detect as langdetect_detect
from langdetect import DetectorFactory

# Local imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config, prompt_template

# Set langdetect to be deterministic
DetectorFactory.seed = 0

def detect_language(text: str) -> str:
    """
    Detect the language of a text string.
    Falls back to English if detection fails.
    
    Args:
        text: Text to analyze
        
    Returns:
        Language code (e.g., 'en', 'hi', 'mr', 'te')
    """
    try:
        detected = langdetect_detect(text)
        
        # Map to our supported languages or default to English
        if detected in config.SUPPORTED_LANGUAGES:
            return detected
        
        # Special case for Hindi/Marathi detection which can be ambiguous
        if detected == 'hi' and any(marathi_char in text for marathi_char in ['ी', 'े', 'ै', 'ो', 'ौ']):
            return 'mr'
            
        return 'en'  # Default to English for unsupported languages
    except Exception as e:
        print(f"Language detection error: {e}")
        return 'en'  # Default to English on error

def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """
    Translate text between languages using OpenAI.
    If source and target are the same, returns the original text.
    
    Args:
        text: Text to translate
        source_lang: Source language code
        target_lang: Target language code
        
    Returns:
        Translated text
    """
    # No translation needed if languages are the same
    if source_lang == target_lang:
        return text
    
    try:
        # Get language names for more accurate translation
        source_name = config.SUPPORTED_LANGUAGES.get(source_lang, source_lang)
        target_name = config.SUPPORTED_LANGUAGES.get(target_lang, target_lang)
        
        # Format the translation prompt
        system_message = prompt_template.TRANSLATION_PROMPT.format(
            source_language=source_name,
            target_language=target_name
        )
        
        # Call the OpenAI API
        response = openai.ChatCompletion.create(
            model=config.TRANSLATION_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": text}
            ],
            temperature=0.3,
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original text on error

def extract_details(conversation: str) -> Dict[str, Any]:
    """
    Extract real estate details from conversation text.
    
    Args:
        conversation: Full conversation text
        
    Returns:
        Dictionary of extracted details
    """
    try:
        response = openai.ChatCompletion.create(
            model=config.DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": prompt_template.DETAIL_EXTRACTION_PROMPT},
                {"role": "user", "content": conversation}
            ],
            temperature=0.3,
        )
        
        # Parse the JSON response
        content = response.choices[0].message.content.strip()
        
        # Handle potential formatting issues
        content = re.sub(r'```json\s*|\s*```', '', content)
        content = content.strip()
        
        details = json.loads(content)
        return details
    except Exception as e:
        print(f"Detail extraction error: {e}")
        return {
            "budget": {"min": None, "max": None, "currency": "INR"},
            "property_type": [],
            "locations": [],
            "urgency": None,
            "special_requirements": []
        }

def generate_response_suggestions(conversation: str, language: str = "en") -> List[str]:
    """
    Generate response suggestions for the real estate agent.
    
    Args:
        conversation: Full conversation text
        language: Language to generate suggestions in
        
    Returns:
        List of suggestion strings
    """
    try:
        language_name = config.SUPPORTED_LANGUAGES.get(language, "English")
        
        system_message = prompt_template.RESPONSE_SUGGESTIONS_PROMPT.format(
            language=language_name
        )
        
        response = openai.ChatCompletion.create(
            model=config.DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": conversation}
            ],
            temperature=0.7,
            max_tokens=300,
        )
        
        content = response.choices[0].message.content.strip()
        
        # Split suggestions by line and clean them
        suggestions = [s.strip() for s in content.split('\n') if s.strip()]
        
        # Limit to 3 suggestions
        return suggestions[:3]
    except Exception as e:
        print(f"Suggestion generation error: {e}")
        return []

def format_extracted_details(details: Dict[str, Any], language: str = "en") -> str:
    """
    Format extracted details into a readable string.
    
    Args:
        details: Dictionary of extracted details
        language: Language to format the string in
        
    Returns:
        Formatted string of details
    """
    if language == "en":
        result = "📋 **Extracted Client Information:**\n\n"
        
        # Budget
        if details.get("budget") and details["budget"].get("max"):
            min_budget = details["budget"].get("min", "")
            if min_budget:
                result += f"💰 **Budget:** {min_budget} - {details['budget']['max']} {details['budget'].get('currency', 'INR')}\n"
            else:
                result += f"💰 **Budget:** Up to {details['budget']['max']} {details['budget'].get('currency', 'INR')}\n"
        
        # Property Type
        if details.get("property_type") and any(details["property_type"]):
            prop_types = ", ".join([p for p in details["property_type"] if p])
            if prop_types:
                result += f"🏠 **Property Type:** {prop_types}\n"
        
        # Locations
        if details.get("locations") and any(details["locations"]):
            locations = ", ".join([l for l in details["locations"] if l])
            if locations:
                result += f"📍 **Locations:** {locations}\n"
        
        # Urgency
        if details.get("urgency"):
            result += f"⏱️ **Timeframe:** {details['urgency']}\n"
        
        # Special Requirements
        if details.get("special_requirements") and any(details["special_requirements"]):
            requirements = ", ".join([r for r in details["special_requirements"] if r])
            if requirements:
                result += f"✅ **Special Requirements:** {requirements}\n"
                
        return result
    elif language in ["hi", "mr", "te"]:
        # Translate to the required language
        english_text = format_extracted_details(details, "en")
        return translate_text(english_text, "en", language)
    else:
        # Default to English for unsupported languages
        return format_extracted_details(details, "en")

def format_suggestions(suggestions: List[str]) -> str:
    """
    Format response suggestions for display.
    
    Args:
        suggestions: List of suggestion strings
        
    Returns:
        Formatted string of suggestions
    """
    if not suggestions:
        return ""
        
    result = "💬 **Suggested Responses:**\n\n"
    
    for i, suggestion in enumerate(suggestions):
        result += f"{i+1}. {suggestion}\n"
        
    return result