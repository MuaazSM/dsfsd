"""
Conversation summarization module for the Real Estate Chatbot.
"""
import openai
from typing import Dict, List, Any, Optional

# Local imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from my_config import config, prompt_template

def generate_summary(conversation: str) -> str:
    """
    Generate a summary of the conversation.
    
    Args:
        conversation: Full conversation text
        
    Returns:
        Summary text
    """
    try:
        response = openai.ChatCompletion.create(
            model=config.SUMMARIZATION_MODEL,
            messages=[
                {"role": "system", "content": prompt_template.SUMMARY_PROMPT},
                {"role": "user", "content": conversation}
            ],
            temperature=0.5,
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Summarization error: {e}")
        return "Unable to generate summary."

def generate_agent_report(conversation: str, extracted_details: Dict[str, Any]) -> str:
    """
    Generate a comprehensive report for the real estate agent.
    
    Args:
        conversation: Full conversation text
        extracted_details: Dictionary of extracted details
        
    Returns:
        Formatted report
    """
    try:
        # Get the basic summary
        summary = generate_summary(conversation)
        
        # Format the report
        report = "# Client Conversation Report\n\n"
        report += "## Summary\n"
        report += f"{summary}\n\n"
        
        # Add extracted details
        report += "## Client Requirements\n"
        
        # Budget
        budget = extracted_details.get("budget", {})
        if budget and budget.get("max"):
            min_val = budget.get("min", "")
            max_val = budget.get("max", "")
            currency = budget.get("currency", "INR")
            
            if min_val:
                report += f"- **Budget:** {min_val} - {max_val} {currency}\n"
            else:
                report += f"- **Budget:** Up to {max_val} {currency}\n"
        
        # Property Type
        prop_types = extracted_details.get("property_type", [])
        if prop_types and any(prop_types):
            types_str = ", ".join([p for p in prop_types if p])
            report += f"- **Property Type:** {types_str}\n"
        
        # Locations
        locations = extracted_details.get("locations", [])
        if locations and any(locations):
            loc_str = ", ".join([l for l in locations if l])
            report += f"- **Locations:** {loc_str}\n"
        
        # Urgency
        urgency = extracted_details.get("urgency")
        if urgency:
            report += f"- **Timeframe:** {urgency}\n"
        
        # Special Requirements
        requirements = extracted_details.get("special_requirements", [])
        if requirements and any(requirements):
            req_str = ", ".join([r for r in requirements if r])
            report += f"- **Special Requirements:** {req_str}\n"
        
        # Generate follow-up recommendations
        report += "\n## Recommended Follow-up Actions\n"
        
        try:
            # Use OpenAI to generate follow-up recommendations
            system_message = """Based on the conversation and client requirements, 
            suggest 3-5 specific follow-up actions the real estate agent should take. 
            Format each recommendation as a bullet point. Be specific, actionable, and practical."""
            
            response = openai.ChatCompletion.create(
                model=config.DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": conversation}
                ],
                temperature=0.7,
                max_tokens=300,
            )
            
            recommendations = response.choices[0].message.content.strip()
            report += recommendations
            
        except Exception as e:
            print(f"Follow-up recommendation error: {e}")
            report += "- Contact the client to confirm requirements\n"
            report += "- Share relevant property listings matching their criteria\n"
            report += "- Schedule a follow-up call to discuss options\n"
        
        return report
    except Exception as e:
        print(f"Report generation error: {e}")
        return f"Summary: {generate_summary(conversation)}"

def generate_market_insights(locations: List[str]) -> str:
    """
    Generate market insights for specific locations.
    
    Args:
        locations: List of location names
        
    Returns:
        Market insights text
    """
    if not locations or not any(locations):
        return "No locations specified for market insights."
        
    try:
        locations_str = ", ".join([l for l in locations if l])
        
        system_message = prompt_template.MARKET_INSIGHTS_PROMPT.format(
            locations=locations_str
        )
        
        response = openai.ChatCompletion.create(
            model=config.DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Provide market insights for: {locations_str}"}
            ],
            temperature=0.7,
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Market insights error: {e}")
        return f"Unable to generate market insights for {', '.join(locations)}."

def generate_followup_messages(summary: str, language: str = "en") -> List[str]:
    """
    Generate follow-up messages for the agent to send to the client.
    
    Args:
        summary: Conversation summary
        language: Language code for the messages
        
    Returns:
        List of follow-up message texts
    """
    try:
        language_name = config.SUPPORTED_LANGUAGES.get(language, "English")
        
        system_message = prompt_template.FOLLOWUP_PROMPT.format(
            summary=summary,
            language=language_name
        )
        
        response = openai.ChatCompletion.create(
            model=config.DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": "Generate follow-up messages based on this conversation summary."}
            ],
            temperature=0.7,
        )
        
        content = response.choices[0].message.content.strip()
        
        # Split by numbered sections or paragraphs
        messages = []
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                # Remove numbering if present
                clean_line = re.sub(r'^\d+[\.\)]\s*', '', line).strip()
                if clean_line:
                    messages.append(clean_line)
        
        return messages[:3]  # Limit to 3 messages
    except Exception as e:
        print(f"Follow-up message generation error: {e}")
        return []

import re  # Added missing import at the end