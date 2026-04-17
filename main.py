import redis
from fastapi import FastAPI
from pydantic import BaseModel
from enum import Enum

app = FastAPI()

r = redis.Redis(host='localhost', port=6379, db=0)

class Loglevel(str, Enum):
    INFO = "INFO"
    ERROR = "ERROR"
    WARNING = 'WARNING'

class logentry(BaseModel):
    service_name: str
    level: Loglevel
    message: str
    timestamp: str

@app.post("/log")
async def create_log(entry: logentry):
    log_json = entry.model_dump_json()
    r.lpush('logs', log_json)
    return {"status": "received", "entry": log_json}