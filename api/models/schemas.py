from pydantic import BaseModel

class PromptRequest(BaseModel):
    prompt: str
    model: str

class QueryRequest(BaseModel):
    query: str
