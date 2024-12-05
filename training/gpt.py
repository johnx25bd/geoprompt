
import openai
import json

client = openai.OpenAI()

# read gpt-prompt.md
with open('gpt-prompt.md', 'r') as file:
    system_content = file.read()

def fetch_sql(prompt: str):
    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "system", 
                "content": system_content
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

with open('validate.json', 'r') as file:
    data = json.load(file)

responses = {}
for i, item in enumerate(data):
    print(f'Processing item {i+1} of {len(data)}:', item['prompt'])
    response = fetch_sql(item['prompt'])
    responses[item['prompt']] = response['sql']
    if i > 3:
        break

# save the response to a file
with open('response.json', 'w') as file:
    json.dump(responses, file)

