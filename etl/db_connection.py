from sqlalchemy import create_engine
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

def get_engine():
    conn_str = os.getenv("DB_CONNECTION_STRING")
    if not conn_str:
        raise ValueError("DB_CONNECTION_STRING not found in .env file")

    if conn_str.startswith("sqlite:///") and not conn_str.startswith("sqlite:////"):
        db_filename = conn_str.replace("sqlite:///", "")
        project_root = Path(__file__).parent.parent
        absolute_path = project_root / db_filename
        # Use forward slashes (as_posix) - SQLAlchemy's sqlite URL parser
        # does not reliably handle Windows backslashes in the path.
        conn_str = f"sqlite:///{absolute_path.as_posix()}"
        print(f"[db_connection] Using database file: {absolute_path}")

    return create_engine(conn_str)