import pandas as pd
import requests
import logging
import json
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import urllib.parse

def get_wiki_bio(artist_name: str) -> str:
    """
    Extrai o resumo da biografia usando a API oficial da Wikipedia,
    garantindo maior robustez e resiliência a falhas.
    """
    clean_name = artist_name.strip()
    
    encoded_name = urllib.parse.quote(clean_name)
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_name}"
    
    headers = {
        'User-Agent': 'ProjetoETL_Universidade/1.0 (projeto_academico@dominio.pt) Bot Python'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('type') == 'standard':
                return data.get('extract')
            else:
                logging.warning(f"Ignorado: '{artist_name}' não é uma página direta (Desambiguação).")
                
        else:
            logging.warning(f"Erro {response.status_code} - Biografia não encontrada para: {clean_name}")
            
    except Exception as e:
        logging.error(f"Erro de conexão ao extrair {clean_name}: {e}")
        
    return None

def scrape_artists_bios(input_csv: str, output_json: str, limit: int = 5):
    logging.info(f"A ler artistas do ficheiro: {input_csv}")
    
    try:
        df = pd.read_csv(input_csv)
        unique_artists = df['artist_name'].dropna().unique()
        
        results = {}
        logging.info(f"A iniciar o scraping para {limit} artistas (amostra de teste)...")
        
        for artist in unique_artists[:limit]:
            logging.info(f"A extrair: {artist}")
            bio = get_wiki_bio(artist)
            if bio:
                results[artist] = bio
            
            time.sleep(1)
            
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
            
        logging.info(f"Scraping concluído! Dados guardados em: {output_json}")
        
    except FileNotFoundError:
        logging.error("O ficheiro CSV gerado no passo anterior não foi encontrado.")

if __name__ == "__main__":
    INPUT_FILE = "data/raw/spotify_sample.csv"
    OUTPUT_FILE = "data/raw/artist_bios_sample.json"
    scrape_artists_bios(INPUT_FILE, OUTPUT_FILE, limit=10)