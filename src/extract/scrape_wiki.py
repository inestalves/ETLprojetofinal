import pandas as pd
import requests
from bs4 import BeautifulSoup
import logging
import json
import time

# Configuração do Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import urllib.parse
# Podes remover a importação do BeautifulSoup lá em cima, já não precisamos dele!

def get_wiki_bio(artist_name: str) -> str:
    """
    Extrai o resumo da biografia usando a API oficial da Wikipedia,
    garantindo maior robustez e resiliência a falhas.
    """
    # 1. Limpar espaços invisíveis do início e fim do nome
    clean_name = artist_name.strip()
    
    # 2. Codificar o nome para o URL de forma segura (lida com espaços e acentos como Beyoncé)
    encoded_name = urllib.parse.quote(clean_name)
    
    # 3. Usar o endpoint oficial de "summary" da Wikipedia
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_name}"
    
    headers = {
        'User-Agent': 'ProjetoETL_Universidade/1.0 (projeto_academico@dominio.pt) Bot Python'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # A API diz-nos logo se a página é "standard" ou "disambiguation" (ex: Shaggy)
            if data.get('type') == 'standard':
                # Devolve o resumo limpo, sem HTML e sem tags de referências!
                return data.get('extract')
            else:
                logging.warning(f"Ignorado: '{artist_name}' não é uma página direta (Desambiguação).")
                
        else:
            logging.warning(f"Erro {response.status_code} - Biografia não encontrada para: {clean_name}")
            
    except Exception as e:
        logging.error(f"Erro de conexão ao extrair {clean_name}: {e}")
        
    return None

def scrape_artists_bios(input_csv: str, output_json: str, limit: int = 5):
    """
    Lê os artistas do CSV e extrai as biografias de uma amostra.
    """
    logging.info(f"A ler artistas do ficheiro: {input_csv}")
    
    try:
        df = pd.read_csv(input_csv)
        # Limpar valores nulos e obter artistas únicos
        unique_artists = df['artist_name'].dropna().unique()
        
        results = {}
        logging.info(f"A iniciar o scraping para {limit} artistas (amostra de teste)...")
        
        # Iterar apenas sobre um limite pequeno para não sermos bloqueados pela Wikipedia
        for artist in unique_artists[:limit]:
            logging.info(f"A extrair: {artist}")
            bio = get_wiki_bio(artist)
            if bio:
                results[artist] = bio
            
            # Pausa de 1 segundo entre pedidos (Boas Práticas de Scraping / Ética)
            time.sleep(1)
            
        # Guardar os dados brutos de forma rastreável
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
            
        logging.info(f"Scraping concluído! Dados guardados em: {output_json}")
        
    except FileNotFoundError:
        logging.error("O ficheiro CSV gerado no passo anterior não foi encontrado.")

if __name__ == "__main__":
    # Caminhos baseados na nossa estrutura
    INPUT_FILE = "data/raw/unique_tracks_sample.csv"
    OUTPUT_FILE = "data/raw/artist_bios_sample.json"
    
    # IMPORTANTE: Estamos a usar um limite de 5 artistas para testar.
    # Quando tiveres a certeza que funciona, podes aumentar este limite!
    scrape_artists_bios(INPUT_FILE, OUTPUT_FILE, limit=5)