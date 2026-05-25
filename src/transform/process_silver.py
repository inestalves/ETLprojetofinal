import pandas as pd
import json
import re
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_track_name(name):
    if pd.isna(name):
        return name
    name = str(name)
    name = re.sub(r'\(.*?\)', '', name)  # Remove (feat. Ciara)
    name = re.sub(r'\[.*?\]', '', name)  # Remove [Radio Edit]
    name = name.split('-')[0]            # Remove tudo após um hífen
    return name.strip().lower()          # Minúsculas e remove espaços

def clean_artist_name(name):
    if pd.isna(name): return name
    return str(name).strip().lower()

def main():
    os.makedirs('data/silver', exist_ok=True)
    
    logging.info("A ler os ficheiros da camada Raw...")
    df_spotify = pd.read_csv('data/raw/spotify_sample.csv')
    df_lastfm = pd.read_csv('data/raw/lastfm_raw.csv')
    df_mb = pd.read_csv('data/raw/musicbrainz_dataset.csv')
    
    with open('data/raw/artist_bios_sample.json', 'r', encoding='utf-8') as f:
        bios_dict = json.load(f)
    df_wiki = pd.DataFrame(list(bios_dict.items()), columns=['artist_name', 'biography'])

    logging.info("A limpar os nomes diretamente nas colunas finais...")
    # Em vez de criar colunas novas, substituímos a própria coluna artist_name e track_name
    for df in [df_spotify, df_lastfm, df_mb, df_wiki]:
        if 'artist_name' in df.columns:
            df['artist_name'] = df['artist_name'].apply(clean_artist_name)
        if 'track_name' in df.columns:
            df['track_name'] = df['track_name'].apply(clean_track_name)

    logging.info("A remover duplicados absolutos das fontes...")
    # O Spotify traz a mesma música várias vezes porque vem de playlists diferentes. Vamos manter só 1 de cada!
    df_spotify = df_spotify.drop_duplicates(subset=['artist_name', 'track_name'])
    df_lastfm = df_lastfm.drop_duplicates(subset=['artist_name'])
    df_mb = df_mb.drop_duplicates(subset=['artist_name', 'track_name'])
    df_wiki = df_wiki.drop_duplicates(subset=['artist_name'])

    logging.info("A realizar a integração dos dados (Joins)...")
    # Como as colunas originais já estão limpas, fazemos o JOIN diretamente por elas
    df_master = pd.merge(df_spotify, df_lastfm, on=['artist_name'], how='left')    
    
    # Adicionamos um sufixo apenas para não dar conflito na coluna mbi_id (que vem do lastfm e do mb)
    df_master = pd.merge(df_master, df_mb, on=['artist_name', 'track_name'], how='left', suffixes=('', '_mb'))
    
    df_master = pd.merge(df_master, df_wiki, on=['artist_name'], how='left')

    logging.info("A normalizar os tipos de dados e nulos...")
    df_master.replace("Unknown", pd.NA, inplace=True)

    df_master['playcount'] = pd.to_numeric(df_master['playcount'], errors='coerce')
    df_master['listeners'] = pd.to_numeric(df_master['listeners'], errors='coerce')
    df_master['release_date'] = pd.to_datetime(df_master['release_date'], errors='coerce')

    output_path = 'data/silver/dataset_integrado.csv'
    df_master.to_csv(output_path, index=False)
    logging.info(f"Transformação concluída! Dataset limpo e sem duplicados guardado em: {output_path}")
    
    print("\n--- Resumo de Qualidade de Dados ---")
    print(df_master.info())

if __name__ == "__main__":
    main()