from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

@app.get("/")
def home():
    return {"status": "running"}

@app.get("/leads")
def get_leads():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM leads LIMIT 50;")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows

@app.post("/leads")
def create_lead():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO leads (owner_name, property_address, surplus_amount, state)
        VALUES ('Test Owner', '123 Main St', 10000, 'TX')
    """)

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "lead created"}
