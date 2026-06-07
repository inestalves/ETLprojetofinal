import requests
import time
import os
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
USER_AGENT = os.getenv('MUSICBRAINZ_USER_AGENT')


def get_musicbrainz_data(artist_name, track_name):
    #  recording para cruzar artista + música
    query = f'artist:"{artist_name}" AND recording:"{track_name}"'
    url = f"https://musicbrainz.org/ws/2/recording/?query={query}&fmt=json"
    headers = {'User-Agent': USER_AGENT}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('recordings'):
                rec = data['recordings'][0]

                artist_mbid = rec.get('artist-credit', [{}])[0].get('artist', {}).get('id', 'Unknown')

                # Release info
                releases = rec.get('releases', [{}])
                first_release = releases[0] if releases else {}

                return {
                    'mbi_id': artist_mbid,
                    'release_country': first_release.get('country', 'Unknown'),
                    'release_date': first_release.get('date', 'Unknown'),
                    'label': first_release.get('label-info', [{}])[0].get('label', {}).get('name', 'Unknown')
                }
        return None
    except Exception as e:
        print(f"Erro ao consultar {artist_name} - {track_name}: {e}")
        return None


if __name__ == "__main__":
    root = Path(__file__).parent.parent.parent
    input_file = root / "data" / "raw" / "spotify_sample.csv"
    output_file = root / "data" / "raw" / "musicbrainz_dataset.csv"

    SAMPLE_SIZE = 500  # Cada faixa demora ~1.2s → 500 faixas ≈ 10 minutos

    df = pd.read_csv(input_file)

    # Selecionar as faixas dos artistas mais populares por aparições em playlists
    top_artists = (
        df.groupby('artist_name')
        .size()
        .sort_values(ascending=False)
        .head(SAMPLE_SIZE)
        .index
        .tolist()
    )
    sample_data = df[df['artist_name'].isin(top_artists)].drop_duplicates(
        subset=['artist_name', 'track_name']
    ).head(SAMPLE_SIZE)

    print(f"A iniciar MusicBrainz para {len(sample_data)} faixas dos artistas mais populares...")

    results = []
    for _, row in sample_data.iterrows():
        artist = row['artist_name']
        track = row['track_name']

        print(f"A pesquisar: {artist} - {track}")
        mb_info = get_musicbrainz_data(artist, track)

        # Unimos os dados originais do Spotify com os novos do MusicBrainz
        entry = {
            'artist_name': artist,
            'track_name': track,
            'mbi_id': mb_info['mbi_id'] if mb_info else 'Unknown',
            'release_country': mb_info['release_country'] if mb_info else 'Unknown',
            'release_date': mb_info['release_date'] if mb_info else 'Unknown',
            'label': mb_info['label'] if mb_info else 'Unknown'
        }
        results.append(entry)

        # rait limit
        time.sleep(1.2)

    pd.DataFrame(results).to_csv(output_file, index=False)
    print(f"Sucesso! Amostra guardada em:{output_file}")