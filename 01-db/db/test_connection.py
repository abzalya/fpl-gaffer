from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_engine(os.getenv("database_url"))

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        print("Connected successfully")
        print(result.scalar())
except Exception as e:
    print(f"Connection failed: {e}")