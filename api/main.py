import logging
from fastapi import FastAPI, HTTPException, Request

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
    return {"message": "Welcome to themap API. Use POST /prompt to send an prompt and receive a query"}

# The prompt endpoint
@app.post("/prompt")
async def process_prompt(request: PromptRequest):

    logger.debug(f"Processing new prompt request: {request.prompt}")
    model = request.model

    try:
        # For future: using different models :P
        # if model == "gpt":
        #     # Call 4o API
        #     pass
        # elif model == "xxx":
        #     # Call xxx API
        #     pass
        # else:
        #     raise HTTPException(status_code=400, detail="Invalid model")
    
        query = "invalid query"
        if request.prompt == "building":
            query = "SELECT id, num_floors, geometry FROM omf_building LIMIT 10"
        elif request.prompt == "water":
            query = "SELECT id, class, geometry FROM omf_water LIMIT 10"
        elif request.prompt == "places":
            query = "SELECT names::json->>'primary' as name, geometry FROM omf_place LIMIT 10"
        return {"query": query}
        
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
