import os
from openai import OpenAI
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

api_key = os.environ.get('OPENAI_API_KEY')
print(f"API Key found: {api_key[:10]}...")

client = OpenAI(api_key=api_key)

try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say hello!"}]
    )
    print("Response:", response.choices[0].message.content)
except Exception as e:
    print("Error:", e)
