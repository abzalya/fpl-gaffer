# optimizer SCHEMA definitions

from sqlalchemy import ( 
    MetaData, Table, Column, BigInteger, Integer, SmallInteger, String, Numeric, 
    Boolean, UniqueConstraint, Index)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import TIMESTAMP 

optimizer_metadata = MetaData(schema="optimizer")

# optimizer SCHEMA
# 2 tables.
# 1. optimization result with a 15 man suggestion what is the return structure of the result? run_id & timestamp, transfers suggested, expected points, expected points with hits, total hits, gw of the suggestion, budget left, user input?, tokens booleans
# 2. logger to have run_id, timestamp, input params and config snapshot for each run
