from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_engine(os.getenv("database_url"))

def create_schemas():
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS archive"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS processed"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS ml"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS optimizer"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS public"))
        conn.commit()

def create_tables():
    public_metadata.create_all(engine)
    archive_metadata.create_all(engine)
    processed_metadata.create_all(engine)
    ml_metadata.create_all(engine)
    optimizer_metadata.create_all(engine)

if __name__ == "__main__":
    create_schemas()
    create_tables()
    print("Done")