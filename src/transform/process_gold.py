import pandas as pd
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def build_dim_artists(df: pd.DataFrame) -> pd.DataFrame:
    dim = (
        df[['artist_name', 'mbi_id', 'playcount', 'listeners', 'tags_genres_era', 'biography']]
        .drop_duplicates(subset=['artist_name'])
        .reset_index(drop=True)
    )
    dim.insert(0, 'artist_id', range(1, len(dim) + 1))
    return dim


def build_dim_tracks(df: pd.DataFrame, dim_artists: pd.DataFrame) -> pd.DataFrame:
    dim = (
        df[['track_name', 'artist_name', 'track_uri', 'release_date', 'release_country', 'label']]
        .drop_duplicates(subset=['track_name', 'artist_name'])
        .reset_index(drop=True)
    )
    dim = dim.merge(dim_artists[['artist_id', 'artist_name']], on='artist_name', how='left')
    dim.drop(columns=['artist_name'], inplace=True)
    dim.insert(0, 'track_id', range(1, len(dim) + 1))
    return dim


def build_fact_popularity(df: pd.DataFrame, dim_artists: pd.DataFrame, dim_tracks: pd.DataFrame) -> pd.DataFrame:
    fact = df[['artist_name', 'track_name', 'playcount', 'listeners']].copy()
    fact = fact.merge(dim_artists[['artist_id', 'artist_name']], on='artist_name', how='left')
    fact = fact.merge(dim_tracks[['track_id', 'track_name', 'artist_id']], on=['track_name', 'artist_id'], how='left')
    fact = fact[['artist_id', 'track_id', 'playcount', 'listeners']].dropna(subset=['artist_id', 'track_id'])
    fact['artist_id'] = fact['artist_id'].astype(int)
    fact['track_id'] = fact['track_id'].astype(int)
    return fact.reset_index(drop=True)


def main():
    os.makedirs('data/gold', exist_ok=True)

    logging.info("A ler a camada Silver...")
    df = pd.read_csv('data/silver/dataset_integrado.csv')

    logging.info("A construir dimensão de artistas...")
    dim_artists = build_dim_artists(df)

    logging.info("A construir dimensão de faixas...")
    dim_tracks = build_dim_tracks(df, dim_artists)

    logging.info("A construir tabela de factos de popularidade...")
    fact_popularity = build_fact_popularity(df, dim_artists, dim_tracks)

    dim_artists.to_csv('data/gold/dim_artists.csv', index=False)
    dim_tracks.to_csv('data/gold/dim_tracks.csv', index=False)
    fact_popularity.to_csv('data/gold/fact_popularity.csv', index=False)

    logging.info(f"Gold layer concluída: {len(dim_artists)} artistas, {len(dim_tracks)} faixas, {len(fact_popularity)} factos.")


if __name__ == "__main__":
    main()
