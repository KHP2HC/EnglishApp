import socket
import subprocess
import sys
import os
import time
import webbrowser

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]

def main():
    api_port = get_free_port()

    print(f"Starting FastAPI on port {api_port}...")
    env = os.environ.copy()
    env["API_PORT"] = str(api_port)

    # Start FastAPI (which now serves both the API and the new frontend)
    fastapi_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", str(api_port)],
        env=env
    )

    time.sleep(2) # Wait for backend to initialize

    local_url = f"http://localhost:{api_port}"
    print(f"==================================================")
    print(f"EnglishCoachPro SPA is running!")
    print(f"Opening browser to: {local_url}")
    print(f"==================================================")
    
    # Automatically open the browser
    webbrowser.open(local_url)

    try:
        fastapi_proc.wait()
    except KeyboardInterrupt:
        print("Shutting down...")
        fastapi_proc.terminate()

if __name__ == "__main__":
    main()
