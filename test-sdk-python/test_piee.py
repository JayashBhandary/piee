from piee import PIEE
from piee.exceptions import PIEEAPIError
import os

# To test against the local server
base_url = os.getenv("PIEE_BASE_URL", "http://localhost:8000")
api_key = os.getenv("PIEE_API_KEY", "pk-test-key")

print(f"Testing PIEE Python SDK against {base_url}")

def test_chat():
    try:
        with PIEE(base_url="http://localhost:8000", api_key="pk-8W_6zBOfpbzb_juLdLP2AMGJQCRC94jTMnvI650LEhFIiBoXZIixwkt6xPIF7Kei") as client:
            print("\n--- 1. Testing Chat Completions ---")
            
            # Non-streaming
            print("Requesting non-streaming completion...")
            response = client.chat.completions.create(
                model="openai/gpt-4o",
                messages=[{"role": "user", "content": "Hello, how are you?"}]
            )
            print("Response:", response.choices[0].message.content)

            # Streaming
            print("\nRequesting streaming completion...")
            stream_response = client.chat.completions.stream(
                model="openai/gpt-4o",
                messages=[{"role": "user", "content": "Write a short haiku about AI."}]
            )
            print("Streaming output:", end=" ", flush=True)
            for chunk in stream_response:
                if chunk.choices and chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end="", flush=True)
            print()
            
    except PIEEAPIError as e:
        print(f"API Error [Status {e.status}]: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def test_models():
    try:
        with PIEE(base_url=base_url, api_key=api_key) as client:
            print("\n--- 2. Testing Models List ---")
            models = client.models.list()
            print("Available models:", [m.id for m in models.data])
    except Exception as e:
        print(f"Error fetching models: {e}")

if __name__ == "__main__":
    test_models()
    test_chat()
    print("\nTests complete!")
