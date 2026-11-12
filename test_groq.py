import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("Groq API key not found. Check your .env file.")
else:
    try:
        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "user",
                    "content": "Introduce yourself in one simple sentence."
                }
            ]
        )

        print("Groq connected successfully!")
        print("AI Response:")
        print(response.choices[0].message.content)

    except Exception as e:
        print("Groq connection failed.")
        print("Error:", e)