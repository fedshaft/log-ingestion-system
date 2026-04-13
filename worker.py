import redis
import psycopg2
import json
import time
from dotenv import load_dotenv
import os

load_dotenv()

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def dbconnection():
    wait_time = 1
    max_time = 50
    while True:
        try:
            conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST")
            )
            conn.autocommit = True
            print("Database connection established")
            return conn
        except Exception as e:
            print(f"Database connection failed: {e}. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            wait_time = min(wait_time * 2, max_time)
        except Exception as e:
            print(f"Error: {e}")
            raise 

def start_worker():
    print("Worker started")
    conn = dbconnection()
    cur = conn.cursor()
    while True:
        result = r.brpop('logs', timeout=0)
        if result:
            _, log_json = result
            log_entry = json.loads(log_json)
            try:
                cur.execute(
                    "INSERT INTO logs (service_name, level, message, timestamp) VALUES (%s, %s, %s, %s)",
                    (log_entry['service_name'], log_entry['level'], log_entry['message'], log_entry['timestamp'])
                )
                print(f"Inserted log: {log_entry}")
            except psycopg2.OperationalError as e:
                conn =dbconnection()
                cur = conn.cursor()
            except Exception as e:
                print(f"Permanent insertion error: {e}")
                r.rpush('logs', log_json)
                break

if __name__ == "__main__":
    start_worker()