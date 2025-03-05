"""
Wrapper script to run the Real Estate Chatbot with the correct Python path.
"""
import os
import sys
import subprocess

# First let's modify the pythonpath to prioritize our local modules
current_dir = os.path.abspath('.')
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Make sure site-packages is at the end of the path
site_packages = [p for p in sys.path if 'site-packages' in p]
for p in site_packages:
    sys.path.remove(p)
    sys.path.append(p)

# Build the command
def main():
    import argparse
    
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
    
    args = parser.parse_args()
    
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
    
    # Set environment for subprocess
    env = os.environ.copy()
    env["PYTHONPATH"] = current_dir + os.pathsep + env.get("PYTHONPATH", "")
    
    # Build the command
    cmd = ["chainlit", "run", target_file, "--port", str(args.port)]
    if args.debug:
        cmd.append("--debug")
    
    try:
        # Run the chainlit command as a subprocess with the modified environment
        subprocess.run(cmd, env=env)
    except Exception as e:
        print(f"Error running application: {e}")

if __name__ == "__main__":
    main()
