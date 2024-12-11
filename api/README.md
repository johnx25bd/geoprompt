# The Geoprompt API

A FastAPI service that converts natural language to SQL queries for spatial data, powered by OpenAI's GPT models and PostGIS.

## Quickstart

1. Set up environment:
   ```bash
   cp .env.example .env
   # Open .evn and add your OpenAI API key to .env
   OPENAI_API_KEY=sk-your-key-here
   ```

2. Build and run:
   ```bash
   docker build -t geoprompt-api:0.1 .
   docker run -p 8000:8000 --env-file .env geoprompt-api
   ```

3. Visit [http://localhost:8000/docs](http://localhost:8000/docs) to explore the API

## API Endpoints

- `POST /prompt`
  - Converts natural language to SQL
  - Request body: `{ "prompt": "find parks in london", "model": "gpt-4" }`
  - Returns: `{ "query": {"sql": "SELECT ... FROM ... WHERE ..." }}`

- `POST /query`
  - Executes SQL and returns GeoJSON
  - Request body: `{ "query": "SELECT ... FROM ..." }`
  - Returns: GeoJSON FeatureCollection

## Code Structure

```plaintext
api/
├── main.py               # FastAPI app and endpoints
├── services/
│   ├── openai.py         # Prompt engineering and API calls
│   ├── gpt-prompt.md     # Prompt Markdown file
│   └── postgis.py        # Database interactions
└── models/
    └── schemas.py        # Request/response models
```

## How It Works

1. Natural language prompts are sent to `/prompt`
2. The prompt is processed using system prompts (in `services/openai.py`) to generate valid PostGIS SQL
3. The SQL can be executed via `/query` to fetch spatial data in GeoJSON format

## Example

```bash
# Convert natural language to SQL
curl -X POST http://localhost:8000/prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "find buildings within 100m of regents canal", "model": "gpt-4o-2024-08-06"}'

# Execute the returned SQL
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT ..."}'
```