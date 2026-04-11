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
    print("Worker is awake (using psycopg2)...")
    
    while True:
        result = r.brpop("logs", timeout=0)
        
        if result:
            _, log_json = result
            
            log_data = json.loads(log_json)
            try:
                cursor.execute("""
                    INSERT INTO logs (service_name, level, message, timestamp)
                    VALUES (%s, %s, %s, %s)
                """, (
                    log_data['service_name'], 
                    log_data['level'], 
                    log_data['message'], 
                    log_data['timestamp']
                ))
                print(f"Saved log from: {log_data['service_name']}")
            except Exception as e:
                print(f"Database error: {e}")

if __name__ == "__main__":
    start_worker()
    