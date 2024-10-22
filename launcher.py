import os
import sys
import subprocess
import time
import psutil
import signal
import requests
import platform
from threading import Thread

class ApplicationLauncher:
    def __init__(self, port=5000):
        self.port = port
        self.backend_process = None
        self.frontend_process = None
        self.should_exit = False
        self.system = platform.system().lower()
        
        # Get the application base path
        if getattr(sys, 'frozen', False):
            self.base_path = sys._MEIPASS
        else:
            self.base_path = os.path.dirname(os.path.abspath(__file__))

    def start_backend(self):
        backend_path = os.path.join(self.base_path, 'backend', 'server.py')
        # python_executable = sys.executable if not getattr(sys, 'frozen', False) else os.path.join(self.base_path, 'python', 'python.exe')
        
        python_executable = sys.executable
        
        self.backend_process = subprocess.Popen(
            [python_executable, backend_path, str(self.port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for backend to be ready
        max_attempts = int(sys.argv[2]) if len(sys.argv) > 1 else 30
        while max_attempts > 0:
            try:
                requests.get(f'http://localhost:{self.port}/health')
                print("Backend server started successfully")
                return True
            except requests.RequestException:
                time.sleep(1)
                print("Waiting for backend server to start...")
                max_attempts -= 1
        
        print("Failed to start backend server")
        return False

    def start_frontend(self):
        frontend_path = os.path.join(
            self.base_path, 'frontend', 'build', 'linux',
            'x64', 'release', 'bundle', 'frontend'
        )
        # On Linux, we might need to make the file executable
        if self.system == 'linux':
            try:
                os.chmod(frontend_path, 0o755)
            except Exception as e:
                print(f"Warning: Could not set executable permissions: {str(e)}")
        
        self.frontend_process = subprocess.Popen(
            [frontend_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    def cleanup(self):
        if self.backend_process:
            for child in psutil.Process(self.backend_process.pid).children(recursive=True):
                child.terminate()
            self.backend_process.terminate()
            
        if self.frontend_process:
            self.frontend_process.terminate()

    def run(self):
        try:
            if not self.start_backend():
                return  
            self.start_frontend()               
            # Monitor processes
            while not self.should_exit:
                if self.frontend_process.poll() is not None:
                    print("Frontend process has ended")
                    break
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("Received shutdown signal")
        finally:
            self.cleanup()

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\nShutdown signal received")
    if launcher:
        launcher.should_exit = True

if __name__ == "__main__":
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and run the launcher
    try:
        # You can specify a different port if needed
        launcher = ApplicationLauncher(port=5000)
        launcher.run()
    except Exception as e:
        print(f"Failed to start application: {str(e)}")
        sys.exit(1)