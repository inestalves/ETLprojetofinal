import requests
import os
import pandas as pd
import time
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
API_KEY = os.getenv('LASTFM_API_KEY')


def get_lastfm_data(artist_name):
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        'method': 'artist.getInfo',
        'artist': artist_name,
        'api_key': API_KEY,
        'format': 'json'
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            artist_data = data.get('artist', {})

            # popularidade
            stats = artist_data.get('stats', {})
            playcount = stats.get('playcount', 0)
            listeners = stats.get('listeners', 0)

            # tags (Género, Mood e Época)
            tags_list = artist_data.get('tags', {}).get('tag', [])
            all_tags = [tag['name'].lower() for tag in tags_list]

            # identificador
            mbid = artist_data.get('mbid', 'Unknown')

            return {
                'playcount': playcount,
                'listeners': listeners,
                'tags_genres_era': ", ".join(all_tags[:10]),
                'mbi_id': mbid
            }
        return None
    except Exception as e:
        print(f"Erro no Last.fm para {artist_name}: {e}")
        return None


if __name__ == "__main__":
    root = Path(__file__).parent.parent.parent
    # Lemos diretamente da amostra base do Spotify
    input_file = root / "data" / "raw" / "spotify_sample.csv"
    output_file = root / "data" / "raw" / "lastfm_raw.csv"

    if not input_file.exists():
        print("Erro: O ficheiro spotify_sample.csv não existe!")
    else:
        df = pd.read_csv(input_file)
        unique_artists = df['artist_name'].unique()[:10]  # amostra teste

        print(f"A extrair dados do Last.fm para {len(unique_artists)} artistas...")

        results = []
        for artist in unique_artists:
            print(f"A consultar: {artist}")
            info = get_lastfm_data(artist)

            if info:
                results.append({
                    'artist_name': artist,
                    'mbi_id': info['mbi_id'],
                    'playcount': info['playcount'],
                    'listeners': info['listeners'],
                    'tags_genres_era': info['tags_genres_era']
                })

            time.sleep(0.2)  # Rate limit

        pd.DataFrame(results).to_csv(output_file, index=False)
        print(f"Extração Last.fm concluída: {output_file}")