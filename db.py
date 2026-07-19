from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Iterable, Mapping, Any
import pandas as pd

DB_PATH = Path(__file__).with_name("tracker.sqlite3")

SCHEMA = """
CREATE TABLE IF NOT EXISTS candidates (
    author_id TEXT PRIMARY KEY,
    full_name TEXT,
    given_name TEXT,
    surname TEXT,
    affiliation TEXT,
    country TEXT,
    h_index INTEGER,
    citation_count INTEGER,
    document_count INTEGER,
    current_doc_count INTEGER,
    orcid TEXT,
    subject_areas TEXT,
    source_query TEXT,
    relevance_score REAL,
    notes TEXT,
    last_updated TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

def connect() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.execute(SCHEMA)
    con.commit()
    return con

def upsert_candidates(rows: Iterable[Mapping[str, Any]]) -> None:
    con = connect()
    sql = """
    INSERT INTO candidates (
        author_id, full_name, given_name, surname, affiliation, country,
        h_index, citation_count, document_count, current_doc_count, orcid,
        subject_areas, source_query, relevance_score, notes, last_updated
    ) VALUES (
        :author_id, :full_name, :given_name, :surname, :affiliation, :country,
        :h_index, :citation_count, :document_count, :current_doc_count, :orcid,
        :subject_areas, :source_query, :relevance_score, :notes, CURRENT_TIMESTAMP
    )
    ON CONFLICT(author_id) DO UPDATE SET
        full_name=excluded.full_name,
        given_name=excluded.given_name,
        surname=excluded.surname,
        affiliation=excluded.affiliation,
        country=excluded.country,
        h_index=excluded.h_index,
        citation_count=excluded.citation_count,
        document_count=excluded.document_count,
        current_doc_count=excluded.current_doc_count,
        orcid=excluded.orcid,
        subject_areas=excluded.subject_areas,
        source_query=excluded.source_query,
        relevance_score=excluded.relevance_score,
        notes=excluded.notes,
        last_updated=CURRENT_TIMESTAMP
    """
    con.executemany(sql, list(rows))
    con.commit()
    con.close()

def load_candidates() -> pd.DataFrame:
    con = connect()
    df = pd.read_sql_query("SELECT * FROM candidates", con)
    con.close()
    return df
