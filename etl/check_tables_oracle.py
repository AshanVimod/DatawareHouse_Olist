from db_connection import get_engine
from sqlalchemy import text

engine = get_engine()

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT table_name FROM user_tables ORDER BY table_name
    """))
    tables = result.fetchall()

print("Tables found in Oracle schema:")
for t in tables:
    print(" -", t[0])