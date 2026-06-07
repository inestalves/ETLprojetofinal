import sqlite3
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS dim_artists (
    artist_id            INTEGER PRIMARY KEY,
    artist_name          TEXT    NOT NULL UNIQUE,
    mbi_id               TEXT,
    playcount            REAL,
    listeners            REAL,
    tags_genres_era      TEXT,
    biography            TEXT,
    playlist_appearances INTEGER
);

CREATE TABLE IF NOT EXISTS dim_tracks (
    track_id         INTEGER PRIMARY KEY,
    track_name       TEXT    NOT NULL,
    artist_id        INTEGER NOT NULL REFERENCES dim_artists(artist_id),
    track_uri        TEXT,
    release_date     TEXT,
    release_country  TEXT,
    label            TEXT
);

CREATE TABLE IF NOT EXISTS fact_popularity (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    artist_id   INTEGER NOT NULL REFERENCES dim_artists(artist_id),
    track_id    INTEGER NOT NULL REFERENCES dim_tracks(track_id),
    playcount   REAL,
    listeners   REAL
);

CREATE INDEX IF NOT EXISTS idx_fact_artist  ON fact_popularity(artist_id);
CREATE INDEX IF NOT EXISTS idx_fact_track   ON fact_popularity(track_id);
CREATE INDEX IF NOT EXISTS idx_track_artist ON dim_tracks(artist_id);
"""


def create_schema(db_path: str = "data/music_analytics.db"):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()
    logging.info(f"Schema criado com sucesso em: {db_path}")


if __name__ == "__main__":
    create_schema()
