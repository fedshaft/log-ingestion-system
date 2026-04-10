import redis
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

r = redis.Redis(host='localhost', port=6379, db=0)

class logentry(BaseModel):
    service_name: str
    level: str
    message: str
    timestamp: str

@app.post("/log")
async def create_log(entry: logentry):
    log_json = entry.model_dump_json()
    r.lpush('logs', log_json)
    return {"status": "received", "entry": log_json}
