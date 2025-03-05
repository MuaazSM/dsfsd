import os
import uuid
import chainlit as cl

# Local imports
from my_config import config
from chatbot import bot, message_handler, summarizer, speech_to_text
from database import firestore

@cl.on_chat_start
async def on_chat_start():
    """
    Initialize the Real Estate Chatbot session.
    - Set up conversation in Firestore
    - Provide a welcome message
    - Optionally add a language selector or voice input button
    """
    conversation_id = str(uuid.uuid4())
    firestore.store_conversation(conversation_id, user_id="anonymous_user")

    cl.user_session.set("conversation_id", conversation_id)
    cl.user_session.set("messages", [])

    # Example: Offer a welcome message with instructions
    await cl.Message(
        content=(
            "👋 **Welcome to the Real Estate Chatbot!**\n\n"
            "I can help with property requirements in multiple languages. "
            "You can also send voice messages (click the mic icon) or type your questions below."
        ),
        author="Real Estate Chatbot"
    ).send()

@cl.on_message
async def on_message(message: cl.Message):
    """
    Handle incoming messages:
    1. Check if it's audio → transcribe
    2. Detect language → translate to English
    3. Feed conversation to the chatbot
    4. Extract details & suggestions
    5. Send AI response, suggestions, etc.
    """
    conversation_id = cl.user_session.get("conversation_id")
    messages = cl.user_session.get("messages", [])

    # Step 1: Check if user uploaded audio
    if message.elements and any(e.get('type') == 'audio' for e in message.elements):
        audio_element = next(e for e in message.elements if e.get('type') == 'audio')
        audio_base64 = audio_element.get('content', '')

        if audio_base64:
            # Acknowledge
            processing_msg = cl.Message(content="🎤 Processing your voice message...")
            await processing_msg.send()

            # Transcribe the audio
            transcription = speech_to_text.process_audio_base64(audio_base64)
            if transcription:
                await processing_msg.update(content=f"🎤 I heard: '{transcription}'")
                message.content = transcription
            else:
                await processing_msg.update(content="❌ Sorry, couldn't understand the audio. Please try again.")
                return

    # Step 2: Detect language
    detected_lang = message_handler.detect_language(message.content)
    # If not English, translate
    translated_content = message.content
    if detected_lang != "en":
        translated_content = message_handler.translate_text(message.content, detected_lang, "en")

    # Step 3: Store user message in local conversation
    messages.append({"role": "user", "content": translated_content})
    cl.user_session.set("messages", messages)

    # Step 4: Process with your RealEstateChatbot
    response_data = bot.chatbot.process_message(
        user_message=message.content,  # original
        conversation_id=conversation_id,
        user_id="anonymous_user",
        conversation_history=messages
    )
    ai_response = response_data["response"]  # possibly translated back
    extracted_details = response_data["extracted_details"]
    suggestions = response_data["suggestions"]
    messages = response_data["conversation_history"]

    # Step 5a: Send AI response
    await cl.Message(
        content=ai_response,
        author="Real Estate Chatbot"
    ).send()

    # Step 5b: Show extracted details (if any)
    if extracted_details and any(extracted_details.values()):
        # Format them however you'd like
        detail_str = message_handler.format_extracted_details(extracted_details, detected_lang)
        await cl.Message(
            content=f"**Extracted Client Information:**\n\n{detail_str}",
            author="Real Estate Chatbot"
        ).send()

    # Step 5c: Show suggestions
    if suggestions:
        suggestion_text = "**Suggested Responses**:\n\n" + "\n".join(f"- {s}" for s in suggestions)
        await cl.Message(content=suggestion_text, author="Suggestions").send()

    # Update conversation
    cl.user_session.set("messages", messages)
