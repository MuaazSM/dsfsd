#!/usr/bin/env python3
"""
Run the Real Estate Chatbot (with advanced features), Admin Dashboard, or Login page.
"""
import os
import sys
import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Real Estate Chatbot Runner")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["chatbot", "admin", "login", "all"],
        default="chatbot",
        help="Run chatbot, admin, login, or all"
    )
    parser.add_argument("--port", type=int, default=8000, help="Port if running single mode")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    args = parser.parse_args()

    # If user wants all
    if args.mode == "all":
        script_path = os.path.abspath("run_all.py")
        os.system(f"{sys.executable} {script_path}")
        return

    # Single-file launch
    mode_to_file = {
        "chatbot": "chainlit_ui/app.py",
        "admin": "chainlit_ui/dashboard.py",
        "login": "chainlit_ui/login.py"
    }
    target_file = mode_to_file[args.mode]

    print(f"Starting {args.mode} on port {args.port}...")

    cmd = ["chainlit", "run", target_file, "--port", str(args.port)]
    if args.debug:
        cmd.append("--debug")

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
