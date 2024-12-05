
import openai
import json
import sqlparse

client = openai.OpenAI()

# read gpt-prompt.md
with open('gpt-prompt.md', 'r') as file:
    system_content = file.read()

def fetch_sql(prompt: str, system_content: str):
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


if __name__ == '__main__':
        
    with open('validate.json', 'r') as file:
        prompts = json.load(file)

    responses = []
    print("=============")
    for i, item in enumerate(prompts):
        print(f'Processing item {i+1} of {len(prompts)}:', item['prompt'])
        
        response = fetch_sql(item['prompt'], system_content)
        response = json.loads(response)
        print(response)
        print('============')
        sql = response['sql']
        responses.append(response['sql'])
    
        formatted_query = sqlparse.format(sql, reindent=True, keyword_case="upper")
        print(formatted_query)
        # append to file
        with open('experiments/responses-formatted-ex2.sql', 'a') as file:
            file.write(formatted_query + '\n')
        print('============')

        if i > 3:
            break


    # save the response to a file
    with open('experiments/responses-ex2.json', 'w') as file:
        json.dump(responses, file)




