import sqlite3
import pandas as pd
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_PATH = "data/music_analytics.db"

GOLD_FILES = {
    "dim_artists":    "data/gold/dim_artists.csv",
    "dim_tracks":     "data/gold/dim_tracks.csv",
    "fact_popularity": "data/gold/fact_popularity.csv",
}


def load_table(conn: sqlite3.Connection, table: str, csv_path: str):
    df = pd.read_csv(csv_path)
    # Substituir NaN por None para que o sqlite3 grave como NULL
    df = df.where(pd.notna(df), None)
    rows_before = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    df.to_sql(table, conn, if_exists="replace", index=False)
    rows_after = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    logging.info(f"{table}: {rows_after} registos carregados (antes: {rows_before}).")


def run_post_load_checks(conn: sqlite3.Connection):
    checks = {
        "total_artists":   "SELECT COUNT(*) FROM dim_artists",
        "total_tracks":    "SELECT COUNT(*) FROM dim_tracks",
        "total_facts":     "SELECT COUNT(*) FROM fact_popularity",
        "facts_sem_artista": "SELECT COUNT(*) FROM fact_popularity WHERE artist_id NOT IN (SELECT artist_id FROM dim_artists)",
        "facts_sem_track":   "SELECT COUNT(*) FROM fact_popularity WHERE track_id  NOT IN (SELECT track_id  FROM dim_tracks)",
        "tracks_sem_artista": "SELECT COUNT(*) FROM dim_tracks WHERE artist_id NOT IN (SELECT artist_id FROM dim_artists)",
        "artistas_duplicados": "SELECT COUNT(*) FROM (SELECT artist_name, COUNT(*) c FROM dim_artists GROUP BY artist_name HAVING c > 1)",
    }
    print("\n=== Relatório de Validação Pós-Load ===")
    results = {}
    for label, sql in checks.items():
        val = conn.execute(sql).fetchone()[0]
        results[label] = val
        status = "OK" if ("sem_" not in label and "duplicados" not in label) or val == 0 else "ALERTA"
        print(f"  [{status}] {label}: {val}")
    return results


def main():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"Base de dados não encontrada em {DB_PATH}. "
            "Execute primeiro: python src/load/create_schema.py"
        )

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    for table, csv_path in GOLD_FILES.items():
        if not os.path.exists(csv_path):
            raise FileNotFoundError(
                f"Ficheiro Gold não encontrado: {csv_path}. "
                "Execute primeiro: python src/transform/process_gold.py"
            )
        load_table(conn, table, csv_path)

    logging.info("A recriar índices...")
    conn.executescript("""
        CREATE INDEX IF NOT EXISTS idx_fact_artist  ON fact_popularity(artist_id);
        CREATE INDEX IF NOT EXISTS idx_fact_track   ON fact_popularity(track_id);
        CREATE INDEX IF NOT EXISTS idx_track_artist ON dim_tracks(artist_id);
    """)

    run_post_load_checks(conn)
    conn.commit()
    conn.close()
    logging.info("Carga concluída com sucesso.")


if __name__ == "__main__":
    main()
