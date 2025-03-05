"""
Main entry point for the Real Estate Chatbot application.
"""
import os
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Real Estate Chatbot")
    
    parser.add_argument(
        "--mode",
        type=str,
        choices=["chatbot", "admin"],
        default="chatbot",
        help="Application mode (chatbot or admin dashboard)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the application on"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run in debug mode"
    )
    
    return parser.parse_args()

def main():
    """Main entry point for the application."""
    args = parse_args()
    
    # Set debug flag in environment
    if args.debug:
        os.environ["DEBUG"] = "True"
    
    # Set mode-specific environment variable for Chainlit
    if args.mode == "admin":
        os.environ["CHAINLIT_APP_DIR"] = "chainlit_ui"
        os.environ["CHAINLIT_APP_MODULE"] = "dashboard"
    else:
        os.environ["CHAINLIT_APP_DIR"] = "chainlit_ui"
        os.environ["CHAINLIT_APP_MODULE"] = "app"
    
    # Set port in environment
    os.environ["CHAINLIT_PORT"] = str(args.port)
    
    # Run Chainlit application
    import chainlit.cli
    chainlit.cli.run_chainlit()

if __name__ == "__main__":
    main()