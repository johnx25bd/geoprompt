import openai
import json
import sqlparse
from pathlib import Path
client = openai.OpenAI()

# Get absolute path to the prompt file
PROMPT_PATH = Path(__file__).parent / 'gpt-prompt.md'

def load_system_content():
    try:
        with open(PROMPT_PATH, 'r') as file:
            content = file.read()
            print(f"Successfully loaded system content from {PROMPT_PATH}")
            # Print first few characters to verify content
            print(f"Content preview: {content[:100]}...")
            return content
    except Exception as e:
        print(f"Error loading system content: {e}")
        raise

# Load system content once when module is imported
SYSTEM_CONTENT = load_system_content()

def fetch_sql(prompt: str, model="gpt-4o-2024-08-06"):
    # Make sure the model is in the correct format, later
    if model not in ["gpt-4o-2024-08-06", "o1-preview-2024-09-12", "o1-mini", "gpt-4o-mini"]:
        model = "gpt-4o-2024-08-06" # fallback
    
    # print("SYSTEM CONTENT within fetch_sql", SYSTEM_CONTENT)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system", 
                "content": SYSTEM_CONTENT
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "sql_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                        "sql": {
                            "description": "The SQL query described by the user in natural language",
                            "type": "string"
                        },
                        "additionalProperties": False
                    }
                }
            }
        }
    )
    return response.choices[0].message.content
