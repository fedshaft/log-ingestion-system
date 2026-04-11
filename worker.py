import redis
import psycopg2
import json
import time
from dotenv import load_dotenv
import os

load_dotenv()

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

pg_conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST")
)

pg_conn.autocommit = True  
cursor = pg_conn.cursor()

def start_worker():
    print("Worker started")

    while True:
        result = r.brpop('logs', timeout=0)
        if result:
            _, log_json = result
            log_entry = json.loads(log_json)
            try:
                cursor.execute(
                    "INSERT INTO logs (service_name, level, message, timestamp) VALUES (%s, %s, %s, %s)",
                    (log_entry['service_name'], log_entry['level'], log_entry['message'], log_entry['timestamp'])
                )
                print(f"Inserted log: {log_entry}")
            except Exception as e:
                print(f"Error inserting log: {e}")
                r.rpush('logs', log_json)
                time.sleep(1)
            
if __name__ == "__main__":
    start_worker()