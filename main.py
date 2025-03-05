"""
Main entry point for the Real Estate Chatbot application.
"""
import os
import argparse
import subprocess
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
    
    # Set mode-specific target file
    if args.mode == "admin":
        target_file = "chainlit_ui/dashboard.py"
        print(f"Starting ADMIN dashboard on port {args.port}...")
    else:
        target_file = "chainlit_ui/app.py"
        print(f"Starting CHATBOT on port {args.port}...")
    
    print("=== Real Estate Multilingual Chatbot ===")
    print(f"Mode: {args.mode}")
    print(f"Port: {args.port}")
    print(f"Debug: {args.debug}")
    print(f"Target: {target_file}")
    print("=======================================")
    
    # Build the command
    cmd = ["chainlit", "run", target_file, "--port", str(args.port)]
    if args.debug:
        cmd.append("--debug")
    
    try:
        # Run the chainlit command as a subprocess
        subprocess.run(cmd)
    except Exception as e:
        print(f"Error running application: {e}")

if __name__ == "__main__":
    main()
