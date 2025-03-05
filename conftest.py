"""
Configuration file for pytest.
"""
import os
import sys
import importlib.util

# Get the project root directory
project_root = os.path.dirname(os.path.abspath(__file__))

# Modify Python path to prioritize our modules
sys.path.insert(0, project_root)

# Check if there's a conflicting chatbot module and remove it from sys.modules
if 'chatbot' in sys.modules:
    del sys.modules['chatbot']

# Force import our chatbot package
chatbot_path = os.path.join(project_root, 'chatbot', '__init__.py')
if os.path.exists(chatbot_path):
    spec = importlib.util.spec_from_file_location('chatbot', chatbot_path)
    chatbot_module = importlib.util.module_from_spec(spec)
    sys.modules['chatbot'] = chatbot_module
    spec.loader.exec_module(chatbot_module)