from sqlalchemy import text
from schema import ml_metadata
from engine import engine

def init_schema():
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS ml"))
        conn.commit()
    ml_metadata.create_all(engine)

if __name__ == "__main__":
    init_schema()
    print("Done")