from sqlalchemy import text
from schema import optimizer_metadata
from engine import engine

def init_schema():
    with engine.connect() as conn:
        conn.execute(text("DROP SCHEMA IF EXISTS optimizer CASCADE"))
        conn.execute(text("CREATE SCHEMA optimizer"))
        conn.commit()
    optimizer_metadata.create_all(engine)

if __name__ == "__main__":
    init_schema()
    print("Done")