# Creating a global engine instance to be imported across the codebase, instead of creating multiple engine instances in different files.
# Version 1.0.0

from sqlalchemy import create_engine
from config import DATABASE_URL

engine = create_engine(DATABASE_URL,
    pool_size=20, max_overflow=0, pool_pre_ping=True)
