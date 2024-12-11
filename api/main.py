import logging
from fastapi import FastAPI, HTTPException, Request

from services.openai import fetch_sql
from services.postgis import fetch_geojson
from models.schemas import PromptRequest, QueryRequest

app = FastAPI()

logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Request failed: {str(e)}", exc_info=True)
        raise

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Geoprompt API. Use POST /prompt to send an prompt and receive a query, and POST /query to send a query and receive a GeoJSON response."}

# The prompt endpoint
@app.post("/prompt")
async def process_prompt(request: PromptRequest):

    logger.debug(f"Processing new prompt request: {request.prompt}")
    model = request.model if request.model else "gpt-4o-2024-08-06"

    try:
        sql = fetch_sql(request.prompt, model)
        return {"query": sql}
        
    except Exception as e:
        logger.error("Error in process_prompt", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# The query endpoint


@app.post("/query")
async def process_query(request: QueryRequest):
    logger.debug(f"Processing new query request: {request.query}")
    try: 
        # Call the database
        geojson = fetch_geojson(request.query)
        return geojson
    except Exception as e:
        logger.error("Error in process_query", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
