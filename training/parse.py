import json
import sqlparse

with open('experiments/responses-ex1.json', 'r') as file:
    data = json.load(file)

for prompt, sql in data.items():
    sql = json.loads(sql)['sql']
    formatted_query = sqlparse.format(sql, reindent=True, keyword_case="upper")
    print(formatted_query)
    # append to file
    with open('experiments/responses-formatted-ex1.sql', 'a') as file:
        file.write(formatted_query + '\n')
    print('============')
