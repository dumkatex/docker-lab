from fastapi import FastAPI



import psycopg2
import os
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

Instrumentator().instrument(app).expose(app)

DB_CONFIG = {
    "host": "postgres",
    "database": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}





@app.get("/")
def read_root():
    return {"message": "Backend fucking3 is working"}


@app.get("/db")
def check_db():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("SELECT version();")
    result = cur.fetchone()

    cur.close()
    conn.close()

    return {"postgres_version": result[0]}


@app.get("/init")
def init_db():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

    return {"status": "table created"}


@app.get("/add/{name}")
def add_user(name: str):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO users (name) VALUES (%s) RETURNING id;",
        (name,)
    )
    user_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return {"id": user_id, "name": name}


@app.get("/users")
def get_users():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("SELECT id, name FROM users;")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [{"id": r[0], "name": r[1]} for r in rows]
