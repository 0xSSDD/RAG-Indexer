#!/usr/bin/env python3
"""
Test Ollama model directly without embeddings
"""
import requests
import json

def test_model_direct():
    """Test llama3.2:3b model directly"""

    url = "http://localhost:11434/api/generate"

    # Test prompts
    prompts = [
        "what about genservers"
    ]

    print("🔍 Testing llama3.2:3b model directly...\n")

    for i, prompt in enumerate(prompts, 1):
        print(f"--- Test {i} ---")
        print(f"Prompt: {prompt}")

        payload = {
            "model": "llama3.2:3b",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "max_tokens": 100
            }
        }

        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                print(f"Response: {result.get('response', 'No response')}")
            else:
                print(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error: {e}")

        print()

    print("✅ Direct model testing complete!")

if __name__ == "__main__":
    test_model_direct()
