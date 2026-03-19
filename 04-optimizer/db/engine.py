# Creating a global engine instance to be imported across the codebase, instead of creating multiple engine instances in different files.
# Version 1.0.0

from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv("database_url"),
    pool_size=20, max_overflow=0, pool_pre_ping=True)
