import json
import logging
import pandas as pd
from pathlib import Path


logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def extract_uris_from_mpd(json_path: str, output_path: str):
    logging.info(f"A iniciar a extração do ficheiro: {json_path}")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        tracks_data = []
        
        for playlist in data.get('playlists', []):
            for track in playlist.get('tracks', []):
                tracks_data.append({
                    'track_uri': track.get('track_uri'),
                    'track_name': track.get('track_name'),
                    'artist_uri': track.get('artist_uri'),
                    'artist_name': track.get('artist_name')
                })
        
        
        df = pd.DataFrame(tracks_data)
        
        df_unique = df.drop_duplicates(subset=['track_uri'])
        
        logging.info(f"Extração concluída. Encontradas {len(df_unique)} faixas únicas.")
        
        df_unique.to_csv(output_path, index=False)
        logging.info(f"Ficheiro guardado com sucesso em: {output_path}")
        
    except FileNotFoundError:
        logging.error(f"Ficheiro não encontrado! Verifica se o caminho está correto: {json_path}")
    except Exception as e:
        logging.error(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    INPUT_FILE = "data/raw/mpd.slice.0-999.json." 
    OUTPUT_FILE = "data/raw/unique_tracks_sample.csv"
    
    extract_uris_from_mpd(INPUT_FILE, OUTPUT_FILE)