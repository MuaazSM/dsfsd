#!/usr/bin/env python3
"""
Launch chatbot, admin dashboard, and login simultaneously on different ports.
"""
import subprocess

def main():
    chatbot_port = 8000
    admin_port   = 8001
    login_port   = 8002

    # Start processes
    procs = []
    procs.append(subprocess.Popen(["chainlit", "run", "chainlit_ui/app.py", "--port", str(chatbot_port)]))
    procs.append(subprocess.Popen(["chainlit", "run", "chainlit_ui/dashboard.py", "--port", str(admin_port)]))
    procs.append(subprocess.Popen(["chainlit", "run", "chainlit_ui/login.py", "--port", str(login_port)]))

    print(f"Chatbot:   http://localhost:{chatbot_port}")
    print(f"Dashboard: http://localhost:{admin_port}")
    print(f"Login:     http://localhost:{login_port}")

    try:
        for p in procs:
            p.wait()
    except KeyboardInterrupt:
        print("Stopping all services...")
        for p in procs:
            p.terminate()

if __name__ == "__main__":
    main()
