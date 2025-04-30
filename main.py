from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()

class InputData(BaseModel):
    prompt: str

@app.post("/run")
async def run_job(input: InputData):
    result = f"Processed prompt: {input.prompt}"
    return {"result": result}
