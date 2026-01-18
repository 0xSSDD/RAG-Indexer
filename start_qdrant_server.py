#!/usr/bin/env python3
"""
Start Qdrant server with web UI
"""

import subprocess
import time
import webbrowser
import os

def start_qdrant_server():
    """Start Qdrant server and open web UI"""
    print("🚀 Starting Qdrant server...")

    # Stop any existing Qdrant processes
    try:
        subprocess.run(["pkill", "-f", "qdrant"], check=False)
        time.sleep(2)
    except:
        pass

    # Try Docker first (most reliable)
    print("🐳 Trying Docker...")
    try:
        # Check if Docker is available
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker found, starting Qdrant container...")

            # Stop existing container
            subprocess.run(["docker", "stop", "qdrant-server"], check=False)
            subprocess.run(["docker", "rm", "qdrant-server"], check=False)

            # Start new container
            process = subprocess.Popen([
                "docker", "run", "-p", "6333:6333", "--name", "qdrant-server",
                "qdrant/qdrant:latest"
            ])

            print("✅ Qdrant server starting...")
            print("🌐 Web UI: http://localhost:6333/dashboard")
            print("📊 API: http://localhost:6333")

            # Wait for server to start
            print("⏳ Waiting for server to start...")
            time.sleep(5)

            # Open browser
            webbrowser.open("http://localhost:6333/dashboard")

            print("🔧 Press Ctrl+C to stop the server")

            # Keep running
            process.wait()
            return

    except FileNotFoundError:
        print("❌ Docker not found")
    except Exception as e:
        print(f"❌ Docker error: {e}")

    # Fallback: Try to start Qdrant binary
    print("🔧 Trying Qdrant binary...")
    try:
        # Try to find and run qdrant binary
        process = subprocess.Popen(["qdrant", "--host", "0.0.0.0", "--port", "6333"])

        print("✅ Qdrant binary starting...")
        print("🌐 Web UI: http://localhost:6333/dashboard")
        print("📊 API: http://localhost:6333")

        time.sleep(3)
        webbrowser.open("http://localhost:6333/dashboard")

        print("🔧 Press Ctrl+C to stop the server")
        process.wait()

    except FileNotFoundError:
        print("❌ Qdrant binary not found")
    except Exception as e:
        print(f"❌ Binary error: {e}")

    # If all else fails, show instructions
    print("\n🎯 Manual Setup Options:")
    print("\n1️⃣ Install Docker and run:")
    print("   docker run -p 6333:6333 qdrant/qdrant:latest")
    print("\n2️⃣ Install Qdrant binary:")
    print("   curl -L https://github.com/qdrant/qdrant/releases/latest/download/qdrant-macos-aarch64.tar.gz | tar xz")
    print("   ./qdrant --host 0.0.0.0 --port 6333")
    print("\n3️⃣ Use Qdrant Cloud:")
    print("   https://cloud.qdrant.io/")
    print("\nThen visit: http://localhost:6333/dashboard")

if __name__ == "__main__":
    start_qdrant_server()
