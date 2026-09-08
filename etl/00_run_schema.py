import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DIALECT = os.getenv("DB_DIALECT", "sqlite")
PROJECT_ROOT = Path(__file__).parent.parent

SQL_FILES = {
    "sqlite": PROJECT_ROOT / "sql" / "01_create_schema_sqlite.sql",
    "oracle": PROJECT_ROOT / "sql" / "01_create_schema_oracle.sql",
    "postgresql": PROJECT_ROOT / "sql" / "01_create_schema.sql",
}

def run_schema_sqlite():
    import sqlite3
    db_path = PROJECT_ROOT / "olist_dwh.db"
    sql_file = SQL_FILES["sqlite"]
    print(f"[00_run_schema] SQLite database: {db_path}")
    print(f"[00_run_schema] SQL file: {sql_file}")

    conn = sqlite3.connect(db_path)
    conn.executescript(sql_file.read_text())
    conn.commit()
    conn.close()
    print("Schema created successfully.")

def run_schema_oracle():
    from db_connection import get_engine
    from sqlalchemy import text

    sql_file = SQL_FILES["oracle"]
    print(f"[00_run_schema] Oracle target. SQL file: {sql_file}")

    sql_script = sql_file.read_text()

    # Oracle PL/SQL blocks are separated by a lone "/" on its own line.
    # Plain CREATE TABLE / CREATE INDEX statements are separated by ";".
    blocks = []
    current = []
    for line in sql_script.splitlines():
        if line.strip() == "/":
            blocks.append("\n".join(current))
            current = []
        else:
            current.append(line)
    if current:
        blocks.append("\n".join(current))

    def is_plsql_block(block):
        # Look at the first non-empty, non-comment line to decide.
        for line in block.splitlines():
            s = line.strip()
            if not s or s.startswith("--"):
                continue
            return s.upper().startswith("BEGIN")
        return False

    engine = get_engine()
    with engine.begin() as conn:
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            if is_plsql_block(block):
                print(f"Running PL/SQL block:\n{block[:80]}...\n")
                conn.execute(text(block))
            else:
                for stmt in [s.strip() for s in block.split(";") if s.strip()]:
                    print(f"Running:\n{stmt[:80]}...\n")
                    conn.execute(text(stmt))

    print("Schema created successfully.")

def run_schema_postgresql():
    from db_connection import get_engine
    from sqlalchemy import text

    sql_file = SQL_FILES["postgresql"]
    print(f"[00_run_schema] PostgreSQL target. SQL file: {sql_file}")

    sql_script = sql_file.read_text()
    statements = [s.strip() for s in sql_script.split(";") if s.strip()]

    engine = get_engine()
    with engine.begin() as conn:
        for stmt in statements:
            print(f"Running:\n{stmt[:80]}...\n")
            conn.execute(text(stmt))

    print("Schema created successfully.")

if __name__ == "__main__":
    if DIALECT == "sqlite":
        run_schema_sqlite()
    elif DIALECT == "oracle":
        run_schema_oracle()
    elif DIALECT == "postgresql":
        run_schema_postgresql()
    else:
        raise ValueError(f"Unknown DB_DIALECT: {DIALECT}")