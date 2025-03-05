"""
UI utilities for the Real Estate Chatbot Chainlit interface.
"""
import chainlit as cl
from typing import List, Dict, Any

# Local imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from my_config import config

def create_language_selector() -> List[Dict[str, Any]]:
    """
    Create a language selector dropdown.
    
    Returns:
        List of UI elements for language selection
    """
    options = []
    for lang_code, lang_name in config.SUPPORTED_LANGUAGES.items():
        options.append({
            "value": lang_code,
            "label": lang_name
        })
    
    return [
        cl.Select(
            id="language_selector",
            label="Select Language",
            values=options,
            initial_value="en"
        )
    ]

def create_voice_button(language: str = "en") -> cl.Action:
    """
    Create a voice input button with the appropriate language.
    
    Args:
        language: Language code for voice recognition
        
    Returns:
        Voice input button UI element
    """
    language_name = config.SUPPORTED_LANGUAGES.get(language, "English")
    
    return cl.Action(
        name="voice_input",
        value=language,
        description=f"Click to record voice in {language_name}",
        label="🎤 Voice Input"
    )

def format_property_data(property_data: Dict[str, Any]) -> str:
    """
    Format property information as markdown text.
    
    Args:
        property_data: Dictionary containing property details
        
    Returns:
        Formatted markdown string
    """
    # Extract property details
    title = property_data.get("title", "Property")
    location = property_data.get("location", "Unknown location")
    price = property_data.get("price", "Price not available")
    bedrooms = property_data.get("bedrooms", "")
    bathrooms = property_data.get("bathrooms", "")
    area = property_data.get("area", "")
    
    # Create description
    description = f"## {title}\n\n"
    description += f"**Location:** {location}\n\n"
    
    specs = []
    if bedrooms:
        specs.append(f"**Bedrooms:** {bedrooms}")
    if bathrooms:
        specs.append(f"**Bathrooms:** {bathrooms}")
    if area:
        specs.append(f"**Area:** {area}")
    
    if specs:
        description += " | ".join(specs) + "\n\n"
    
    description += f"**Price:** {price}"
    
    return description

def format_extracted_details(details: Dict[str, Any]) -> str:
    """
    Format extracted details into markdown text.
    
    Args:
        details: Dictionary of extracted details
        
    Returns:
        Formatted markdown string
    """
    content = "## 📋 Client Requirements\n\n"
    
    # Budget
    if details.get("budget") and details["budget"].get("max"):
        min_budget = details["budget"].get("min", "")
        if min_budget:
            content += f"💰 **Budget:** {min_budget} - {details['budget']['max']} {details['budget'].get('currency', 'INR')}\n\n"
        else:
            content += f"💰 **Budget:** Up to {details['budget']['max']} {details['budget'].get('currency', 'INR')}\n\n"
    
    # Property Type
    if details.get("property_type") and any(details["property_type"]):
        prop_types = ", ".join([p for p in details["property_type"] if p])
        if prop_types:
            content += f"🏠 **Property Type:** {prop_types}\n\n"
    
    # Locations
    if details.get("locations") and any(details["locations"]):
        locations = ", ".join([l for l in details["locations"] if l])
        if locations:
            content += f"📍 **Locations:** {locations}\n\n"
    
    # Urgency
    if details.get("urgency"):
        content += f"⏱️ **Timeframe:** {details['urgency']}\n\n"
    
    # Special Requirements
    if details.get("special_requirements") and any(details["special_requirements"]):
        requirements = ", ".join([r for r in details["special_requirements"] if r])
        if requirements:
            content += f"✅ **Special Requirements:** {requirements}\n\n"
    
    return content

def create_response_suggestions_buttons(suggestions: List[str]) -> List[cl.Action]:
    """
    Create buttons for response suggestions.
    
    Args:
        suggestions: List of suggestion strings
        
    Returns:
        List of Action UI elements
    """
    buttons = []
    
    for i, suggestion in enumerate(suggestions):
        buttons.append(
            cl.Action(
                name=f"suggestion_{i}",
                value=suggestion,
                description="Use this response",
                label=f"Response {i+1}"
            )
        )
    
    return buttons

def create_notification(message: str, type: str = "info") -> Dict[str, Any]:
    """
    Create a notification data structure.
    
    Args:
        message: Notification message
        type: Type of notification ('info', 'warning', 'error', 'success')
        
    Returns:
        Notification data dictionary
    """
    return {
        "title": "Real Estate Assistant",
        "content": message,
        "type": type,
        "duration": 5000  # 5 seconds
    }