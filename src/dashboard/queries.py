import sqlite3
import pandas as pd

DB_PATH = "data/music_analytics.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── Filtros disponíveis ────────────────────────────────────────────────────────

def get_countries() -> list:
    conn = get_connection()
    df = pd.read_sql("""
        SELECT DISTINCT release_country
        FROM dim_tracks
        WHERE release_country IS NOT NULL
        ORDER BY release_country
    """, conn)
    conn.close()
    return df["release_country"].tolist()


def get_genres() -> list:
    """Devolve géneros individuais (split das tags compostas)."""
    conn = get_connection()
    df = pd.read_sql("""
        SELECT tags_genres_era FROM dim_artists
        WHERE tags_genres_era IS NOT NULL
    """, conn)
    conn.close()
    genres = set()
    for tags in df["tags_genres_era"]:
        for tag in tags.split(","):
            genres.add(tag.strip().lower())
    return sorted(genres)


# ── Queries analíticas ─────────────────────────────────────────────────────────

def get_top_artists_by_playlist(top_n: int = 10, country: str = None) -> pd.DataFrame:
    """Top N artistas por aparições em playlists (cobre todos os artistas)."""
    conn = get_connection()
    country_filter = "AND t.release_country = :country" if country else ""
    df = pd.read_sql(f"""
        SELECT
            a.artist_name,
            a.playlist_appearances,
            a.listeners,
            a.playcount,
            a.tags_genres_era
        FROM dim_artists a
        LEFT JOIN dim_tracks t ON a.artist_id = t.artist_id
        WHERE a.playlist_appearances IS NOT NULL
        {country_filter}
        GROUP BY a.artist_name
        ORDER BY a.playlist_appearances DESC
        LIMIT :top_n
    """, conn, params={"top_n": top_n, "country": country})
    conn.close()
    return df


def get_top_artists_by_listeners(top_n: int = 10, country: str = None) -> pd.DataFrame:
    """Top N artistas por número de ouvintes Last.fm."""
    conn = get_connection()
    country_filter = "AND t.release_country = :country" if country else ""
    df = pd.read_sql(f"""
        SELECT
            a.artist_name,
            a.listeners,
            a.playcount,
            a.playlist_appearances,
            a.tags_genres_era
        FROM dim_artists a
        LEFT JOIN dim_tracks t ON a.artist_id = t.artist_id
        WHERE a.listeners IS NOT NULL
        {country_filter}
        GROUP BY a.artist_name
        ORDER BY a.listeners DESC
        LIMIT :top_n
    """, conn, params={"top_n": top_n, "country": country})
    conn.close()
    return df


def get_tracks_by_country(top_n: int = 15) -> pd.DataFrame:
    """Número de faixas por país de lançamento."""
    conn = get_connection()
    df = pd.read_sql("""
        SELECT release_country, COUNT(*) AS total_faixas
        FROM dim_tracks
        WHERE release_country IS NOT NULL
        GROUP BY release_country
        ORDER BY total_faixas DESC
        LIMIT :top_n
    """, conn, params={"top_n": top_n})
    conn.close()
    return df


def get_top_genres(top_n: int = 15, country: str = None) -> pd.DataFrame:
    """Géneros mais frequentes (split das tags compostas), filtrável por país."""
    conn = get_connection()
    country_filter = "AND t.release_country = :country" if country else ""
    df = pd.read_sql(f"""
        SELECT a.tags_genres_era, a.playlist_appearances
        FROM dim_artists a
        LEFT JOIN dim_tracks t ON a.artist_id = t.artist_id
        WHERE a.tags_genres_era IS NOT NULL
        {country_filter}
        GROUP BY a.artist_name
    """, conn, params={"country": country})
    conn.close()

    # Tags que NÃO são géneros (geográficas, culturais, meta-tags)
    NON_GENRE_TAGS = {
        "canadian", "american", "british", "australian", "swedish", "german",
        "french", "irish", "scottish", "welsh", "norwegian", "danish",
        "urban", "atlanta", "west coast", "east coast", "southern rap",
        "x factor", "disney", "guilty pleasure", "seen live", "favourite",
        "favorites", "love", "beautiful", "awesome", "cool", "good",
        "new", "old", "classic", "best", "top", "viral",
    }

    # Split das tags compostas em géneros individuais
    genre_counts = {}
    for _, row in df.iterrows():
        for tag in row["tags_genres_era"].split(","):
            tag = tag.strip().lower()
            if tag and tag not in NON_GENRE_TAGS:
                genre_counts[tag] = genre_counts.get(tag, 0) + 1

    result = pd.DataFrame(
        sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:top_n],
        columns=["genero", "total_artistas"]
    )
    return result


def get_listeners_vs_playlist(country: str = None) -> pd.DataFrame:
    """Relação entre listeners Last.fm e aparições em playlists Spotify."""
    conn = get_connection()
    country_filter = "AND t.release_country = :country" if country else ""
    df = pd.read_sql(f"""
        SELECT
            a.artist_name,
            a.listeners,
            a.playlist_appearances,
            a.tags_genres_era
        FROM dim_artists a
        LEFT JOIN dim_tracks t ON a.artist_id = t.artist_id
        WHERE a.listeners IS NOT NULL
          AND a.playlist_appearances IS NOT NULL
        {country_filter}
        GROUP BY a.artist_name
    """, conn, params={"country": country})
    conn.close()
    return df


def get_releases_over_time(country: str = None) -> pd.DataFrame:
    """Número de lançamentos por ano."""
    conn = get_connection()
    country_filter = "AND release_country = :country" if country else ""
    df = pd.read_sql(f"""
        SELECT
            SUBSTR(release_date, 1, 4) AS ano,
            COUNT(*) AS total_lancamentos
        FROM dim_tracks
        WHERE release_date IS NOT NULL
          AND SUBSTR(release_date, 1, 4) BETWEEN '1950' AND '2025'
          {country_filter}
        GROUP BY ano
        ORDER BY ano
    """, conn, params={"country": country})
    conn.close()
    return df


def get_genre_vs_success(metric: str = "playlist_appearances") -> pd.DataFrame:
    """Média da métrica de sucesso por género musical."""
    conn = get_connection()
    df = pd.read_sql(f"""
        SELECT a.tags_genres_era, a.{metric}
        FROM dim_artists a
        WHERE a.tags_genres_era IS NOT NULL
          AND a.{metric} IS NOT NULL
    """, conn)
    conn.close()

    NON_GENRE_TAGS = {
        "canadian", "american", "british", "australian", "swedish", "german",
        "french", "irish", "scottish", "welsh", "norwegian", "danish",
        "urban", "atlanta", "west coast", "east coast", "southern rap",
        "x factor", "disney", "guilty pleasure", "seen live", "favourite",
        "favorites", "love", "beautiful", "awesome", "cool", "good",
        "new", "old", "classic", "best", "top", "viral",
    }

    rows = []
    for _, row in df.iterrows():
        for tag in row["tags_genres_era"].split(","):
            tag = tag.strip().lower()
            if tag and tag not in NON_GENRE_TAGS:
                rows.append({"genero": tag, metric: row[metric]})

    result = (
        pd.DataFrame(rows)
        .groupby("genero")[metric]
        .agg(["mean", "count"])
        .reset_index()
        .rename(columns={"mean": f"media_{metric}", "count": "n_artistas"})
        .query("n_artistas >= 3")   # só géneros com dados suficientes
        .sort_values(f"media_{metric}", ascending=False)
        .head(15)
    )
    return result
