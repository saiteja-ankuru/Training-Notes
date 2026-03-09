"""
db_ingestion.py
---------------
Handles reading the nutrition dataset from a database into a pandas DataFrame.

IMPORT THIS FILE IN: app.py  ← only here, at the top alongside other imports.
DO NOT import it in graphs.py — graphs.py only receives DataFrames as arguments
and should stay completely unaware of where the data comes from.

Usage in app.py — replace:
    df = pd.read_csv("nutrition.csv")
With:
    from db_ingestion import load_from_db
    df = load_from_db()
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from urllib.parse import quote_plus

# ──────────────────────────────────────────────────────────────────────────────
# ✏️  CONFIGURATION — fill in your values here (or use environment variables)
# ──────────────────────────────────────────────────────────────────────────────

DB_BACKEND = "mysql"

# ── MySQL (SQLAlchemy) ──
DB_HOST     = os.getenv("DB_HOST",     "localhost")
DB_PORT     = os.getenv("DB_PORT",     "3306")          
DB_NAME     = os.getenv("DB_NAME",     "Nutrition")
DB_USER     = os.getenv("DB_USER",     "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "saiteja123")
DB_TABLE    = os.getenv("DB_TABLE",    "nutrition")     # table that holds your CSV data
encoded_password = quote_plus(DB_PASSWORD)
QUERY_FILTER = None


# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────


def _load_mysql() -> pd.DataFrame:
    """Read from MySQL using SQLAlchemy + PyMySQL."""
    url = URL.create(
    drivername="mysql+pymysql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME
    )
    # f"mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    engine = create_engine(url, echo=True)
    query = (
        f"SELECT * FROM {DB_TABLE} WHERE {QUERY_FILTER}"
        if QUERY_FILTER
        else f"SELECT * FROM {DB_TABLE}"
    )
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)
    return df


# ──────────────────────────────────────────────────────────────────────────────
# Public API — the only function app.py needs to call
# ──────────────────────────────────────────────────────────────────────────────

_LOADERS = {
    "mysql": _load_mysql,
}


def load_from_db() -> pd.DataFrame:
    """
    Load the nutrition dataset from the configured database backend.

    Returns:
        pd.DataFrame — equivalent to pd.read_csv("nutrition.csv"),
                       with the same column names the rest of the app expects.

    Raises:
        ValueError   — if DB_BACKEND is not one of the supported options.
        Exception    — propagates any connection / query errors with a clear message.
    """
    if DB_BACKEND not in _LOADERS:
        raise ValueError(
            f"Unknown DB_BACKEND '{DB_BACKEND}'. "
            f"Choose one of: {list(_LOADERS.keys())}"
        )

    try:
        df = _LOADERS[DB_BACKEND]()
    except Exception as exc:
        raise RuntimeError(
            f"Failed to load data from {DB_BACKEND!r}.\n"
            f"Check your connection settings in db_ingestion.py.\n"
            f"Original error: {exc}"
        ) from exc

    if df.empty:
        raise RuntimeError(
            f"Query returned 0 rows from {DB_BACKEND!r}. "
            "Check that the table/collection name and any QUERY_FILTER are correct."
        )

    return df


# ──────────────────────────────────────────────────────────────────────────────
# Optional: push the CSV into your DB for the first time
# ──────────────────────────────────────────────────────────────────────────────

def ingest_csv_to_db(csv_path: str = "nutrition.csv", if_exists: str = "replace") -> None:
    """
    One-time helper: read the CSV and write it into the configured database.
    Run this once from the terminal to seed your database:

        python db_ingestion.py

    Args:
        csv_path  — path to the source CSV file.
        if_exists — "replace" overwrites the table; "append" adds rows; "fail" errors if table exists.
    """
    df = pd.read_csv(csv_path)

    
    if DB_BACKEND == "mysql":
        from sqlalchemy import create_engine
        engine = create_engine(
            f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
    df.to_sql(DB_TABLE, engine, if_exists=if_exists, index=False)
    print(f"✅  Inserted {len(df):,} rows into {DB_BACKEND} table '{DB_TABLE}'.")


# ──────────────────────────────────────────────────────────────────────────────
# Run directly to seed the database
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Seeding {DB_BACKEND!r} from CSV …")
    ingest_csv_to_db()
