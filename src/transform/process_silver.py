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
    name = re.sub(r'\(.*?\)', '', name)  
    name = re.sub(r'\[.*?\]', '', name)  
    name = name.split('-')[0]           
    return name.strip().lower()          #

def clean_artist_name(name):
    """Passa o nome do artista para minúsculas para evitar falhas no Join por causa de maiúsculas/minúsculas."""
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

    logging.info("A normalizar chaves de cruzamento (nomes de artistas e faixas)...")
    for df in [df_spotify, df_lastfm, df_mb]:
        df['artist_join'] = df['artist_name'].apply(clean_artist_name)
        if 'track_name' in df.columns:
            df['track_join'] = df['track_name'].apply(clean_track_name)
            
    df_wiki['artist_join'] = df_wiki['artist_name'].apply(clean_artist_name)

    logging.info("A realizar a integração dos dados (Joins)...")
    df_master = pd.merge(df_spotify, df_lastfm, on=['artist_join'], how='left', suffixes=('', '_lastfm'))    
    
    df_master = pd.merge(df_master, df_mb, on=['artist_join', 'track_join'], how='left', suffixes=('', '_mb'))
    
    df_master = pd.merge(df_master, df_wiki, on=['artist_join'], how='left', suffixes=('', '_wiki'))

    logging.info("A limpar e normalizar colunas finais...")
    colunas_para_apagar = ['artist_join', 'track_join', 'artist_name_lastfm', 'track_name_lastfm', 
                           'artist_name_mb', 'track_name_mb', 'artist_name_wiki']
    df_master.drop(columns=[col for col in colunas_para_apagar if col in df_master.columns], inplace=True)

    df_master.replace("Unknown", pd.NA, inplace=True)

    df_master['playcount'] = pd.to_numeric(df_master['playcount'], errors='coerce')
    df_master['listeners'] = pd.to_numeric(df_master['listeners'], errors='coerce')

    df_master['release_date'] = pd.to_datetime(df_master['release_date'], errors='coerce')

    output_path = 'data/silver/dataset_integrado.csv'
    df_master.to_csv(output_path, index=False)
    logging.info(f"Transformação concluída! Dataset guardado em: {output_path}")
    
    print("\n--- Resumo de Qualidade de Dados ---")
    print(df_master.info())

if __name__ == "__main__":
    main()