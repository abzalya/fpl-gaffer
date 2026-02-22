# Init the db. Creating schemas and tables. Run this before running the pipeline for the first time, or after making changes to the schema.

# Version 1.0.0

from sqlalchemy import text
from schema import archive_metadata, processed_metadata, ml_metadata, optimizer_metadata, public_metadata
from engine import engine

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