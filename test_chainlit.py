"""
✅ Unit tests for the Real Estate Chatbot UI.
"""
import pytest
import chainlit as cl
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_welcome_message():
    """Test chatbot startup message."""
    start_mock = AsyncMock()
    cl.on_chat_start = start_mock

    await start_mock()

    start_mock.assert_called_once()
    assert "Hello, welcome" in start_mock.call_args[1]["content"]

@pytest.mark.asyncio
async def test_user_message():
    """Test user message response."""
    message_mock = AsyncMock()
    cl.on_message = message_mock

    test_message = cl.Message(content="Hello, chatbot!")
    await message_mock(test_message)

    message_mock.assert_called_once()
    assert "You said: Hello, chatbot!" in message_mock.call_args[1]["content"]
