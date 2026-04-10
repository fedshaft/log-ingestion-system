from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class logentry(BaseModel):
    service_name: str
    level: str
    message: str
    timestamp: str

@app.post("/log")
async def create_log(entry: logentry):
    print(f"Received log entry: {entry.service_name}, level: {entry.level}, message: {entry.message}, timestamp: {entry.timestamp}")
    return{"status" : "received"}


