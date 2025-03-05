import os
import chainlit as cl
from datetime import datetime
from my_config import config
from database import firestore
from chatbot import summarizer, message_handler

@cl.on_chat_start
async def on_chat_start():
    """
    Initialize the admin dashboard:
    - Possibly show conversation analytics
    - Show follow-ups
    - Provide search box
    """
    await cl.Message(
        content="👋 **Welcome to the Real Estate Admin Dashboard**.",
        author="Admin"
    ).send()

    # For example: get recent conversations
    conversations = firestore.get_user_conversations(None, limit=5)
    content = "### Recent Conversations\n\n"
    if not conversations:
        content += "No recent conversations."
    else:
        for i, conv in enumerate(conversations):
            cid = conv.get("id","")
            last = conv.get("lastUpdated","")
            content += f"{i+1}. **ID**: {cid}, Last Updated: {last}\n"

    await cl.Message(content=content, author="Admin").send()
    
    # Provide instructions for searching
    await cl.Message(
        content="Type `search: <text>` to find conversations, or `followups` to see pending follow-ups.",
        author="Admin"
    ).send()

@cl.on_message
async def on_message(message: cl.Message):
    """
    Handle admin commands:
    - 'search: xyz'
    - 'followups'
    - etc.
    """
    text = message.content.lower().strip()

    if text.startswith("search:"):
        query_text = text.split("search:",1)[1].strip()
        results = firestore.search_conversations(query_text)
        if results:
            result_str = "\n".join([f"- {r['id']} (Title: {r.get('title','No Title')})" for r in results])
            await cl.Message(content=f"**Search Results**:\n{result_str}", author="Admin").send()
        else:
            await cl.Message(content="No conversations found with that query.", author="Admin").send()

    elif text == "followups":
        followups = firestore.get_pending_followups()
        if not followups:
            await cl.Message(content="No pending follow-ups.", author="Admin").send()
        else:
            summary = []
            for fup in followups:
                summary.append(f"{fup['id']} → {fup['notes']} @ {fup['scheduledFor']}")
            await cl.Message(
                content="**Pending Follow-ups**:\n" + "\n".join(summary),
                author="Admin"
            ).send()
    else:
        await cl.Message(
            content="Admin Dashboard Commands:\n- `search: <text>`\n- `followups`",
            author="Admin"
        ).send()
