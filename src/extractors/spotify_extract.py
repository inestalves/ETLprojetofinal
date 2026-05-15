import zipfile
import json
import csv
import os
from tqdm import tqdm
import pathlib

#Ler o dataset em chunks
def extract_spotify_metadata(zip_path, output_csv, limit_files=10):
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    tracks_metadata = []
    print(f"A abrir arquivo: {zip_path}")

    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            json_files = [f for f in z.namelist() if f.endswith('.json') and 'data/' in f]
            files_to_process = json_files[:limit_files]
            print(f"A processar {len(files_to_process)} ficheiros (Amostra)...")
            for file_name in tqdm(files_to_process):
                with z.open(file_name) as f:
                    data = json.load(f)
                    for playlist in data['playlists']:
                        for track in playlist['tracks']:
                            tracks_metadata.append({
                                'artist_name': track['artist_name'],
                                'track_name': track['track_name'],
                                'artist_uri': track['artist_uri'],
                                'track_uri': track['track_uri']
                            })

        if not tracks_metadata:
            print("Aviso: Nenhum dado foi extraído.")
            return

        keys = tracks_metadata[0].keys()
        with open(output_csv, 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(tracks_metadata)

        print(f"Sucesso! Amostra guardada em: {output_csv}")

    except Exception as e:
        print(f"Erro ao processar o ZIP: {e}")

if __name__ == "__main__":
    current_dir = pathlib.Path(__file__).parent.resolve()
    project_root = current_dir.parent.parent
    ZIP_FILE = project_root / "data" / "raw" / "spotify_million_playlist_dataset.zip"
    OUTPUT = project_root / "data" / "raw" / "spotify_sample.csv"
    if ZIP_FILE.exists():
        extract_spotify_metadata(str(ZIP_FILE), str(OUTPUT), limit_files=5)
    else:
        print(f"Erro Crítico: O ficheiro ZIP não foi encontrado em: {ZIP_FILE}")