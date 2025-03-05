import chainlit as cl
import uuid
from my_config import config

# Mock user DB
USERS = {
    "agent@example.com": {
        "password": "password123",
        "name": "Demo Agent",
        "role": "agent",
    },
    "admin@example.com": {
        "password": "admin123",
        "name": "Admin",
        "role": "admin",
    }
}

@cl.on_chat_start
async def on_chat_start():
    """
    Show a login form plus optional instructions for voice input.
    """
    elements = [
        cl.Input(id="email", label="Email", placeholder="Enter your email"),
        cl.Password(id="password", label="Password", placeholder="Enter your password"),
        cl.Action(name="login", value="login", label="Login")
    ]
    
    content = (
        "👋 **Welcome to the Login Page**!\n\n"
        "You can **type** your email/password or attach a **voice message** with your credentials (for demo)."
    )
    await cl.Message(content=content, elements=elements).send()

@cl.on_message
async def on_message(message: cl.Message):
    """
    If user tries voice input for login (in real scenario, you'd parse carefully).
    """
    if message.elements and any(e.get('type') == 'audio' for e in message.elements):
        audio_elem = next(e for e in message.elements if e.get('type') == 'audio')
        # (Pretend we parse email/password from audio transcript)
        await cl.Message(content="(Voice login isn't truly implemented, but here's the concept.)").send()
    else:
        await cl.Message(content="Please use the login form above.", author="System").send()

@cl.action_callback("login")
async def on_login(action):
    """
    Handle the login form.
    """
    data = action.data
    email = data.get("email","").strip().lower()
    password = data.get("password","")

    user = USERS.get(email)
    if user and user["password"] == password:
        # Logged in
        await cl.Message(
            content=f"✅ **Login successful**! Hello {user['name']}, you can now open the Chatbot or Admin Dashboard in separate tabs.",
            author="Login"
        ).send()
    else:
        await cl.Message(content="❌ Invalid credentials, please try again.", author="Login").send()
