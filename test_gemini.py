import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("API key not found. Check your .env file.")

else:
    client = genai.Client(api_key=api_key)

    for attempt in range(3):
        try:
            print(f"Attempt {attempt + 1}...")

            response = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents="Explain artificial intelligence in one simple sentence."
            )

            print("\nGemini connected successfully!")
            print("\nAI Response:")
            print(response.text)
            break

        except Exception as e:
            print("\nGemini request failed:", e)

            if "503" in str(e) and attempt < 2:
                print("Waiting 10 seconds before retrying...")
                time.sleep(10)
            else:
                print("Please try again later.")
                break