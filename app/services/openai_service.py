from openai import OpenAI
import os
from app.config.config_loader import config

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def ask_openai(question: str) -> str:
    try:
        messages = config["openai"]["messages"].copy()
        messages.append({"role": "user", "content": question})
        
        response = client.chat.completions.create(
            model=config["openai"]["model"],
            messages=messages,
            temperature=config["openai"]["temperature"]
        )

        print("Full OpenAI Response:", response)

        if response and response.choices:
            return response.choices[0].message.content

        return "Error: OpenAI response is empty or invalid."

    except Exception as e:
        return f"OpenAI API Error: {str(e)}"