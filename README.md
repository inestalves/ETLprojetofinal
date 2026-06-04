# ETLprojetofinal — Análise de Tendências Musicais Globais

Este projeto consiste num pipeline ETL (Extract, Transform, Load) modular, desenvolvido para extrair e processar dados musicais de diversas fontes (Spotify, Wikipedia, Last.fm e MusicBrainz). O objetivo principal é analisar que fatores influenciam as tendências musicais em diferentes países.

## Estrutura do Projeto

```
ETLprojetofinal/
├── data/
│   ├── raw/              # Bronze Layer — dados brutos extraídos
│   ├── silver/           # Silver Layer — dados limpos e integrados
│   ├── gold/             # Gold Layer — modelo dimensional (CSVs)
│   └── music_analytics.db  # Base de dados SQLite (Star Schema)
├── docs/
│   ├── fontes.md             # Inventário de fontes e licenças
│   ├── dicionario.md         # Dicionário de dados
│   ├── modelo_ER.md          # Diagrama ER e estratégia de modelação
│   ├── relatorio_qualidade.md    # Qualidade de dados (Semana 2)
│   ├── relatorio_validacao_load.md  # Validação pós-load (Semana 3)
│   └── IA_LOG.md             # Registo de uso de IA
├── src/
│   ├── extractors/       # Scripts de extração (Semana 1)
│   ├── transform/        # Scripts de transformação (Semanas 2 e 3)
│   │   ├── process_silver.py
│   │   └── process_gold.py
│   ├── load/             # Scripts de carga (Semana 3)
│   │   ├── create_schema.py
│   │   └── load_data.py
│   └── utils/
├── .env.example          # Exemplo de configuração de chaves de API
├── .gitignore
├── requirements.txt
└── README.md
```

## Configuração e Instalação

### 1. Pré-requisitos

- Python 3.9 ou superior
- Para visualizar a base de dados SQLite: [DB Browser for SQLite](https://sqlitebrowser.org/) (gratuito)

### 2. Instalação de Dependências

```bash
pip install -r requirements.txt
```

### 3. Configuração de APIs

1. Crie um ficheiro `.env` na raiz do projeto.
2. Copie o conteúdo de `.env.example` e preencha as suas chaves de API (Last.fm, Spotify).

## Execução do Pipeline Completo

Execute os comandos **a partir da raiz do projeto**, pela ordem indicada.

### Semana 1 — Extração

```bash
python src/extractors/spotify_extract.py
python src/extractors/scrape_wiki.py
python src/extractors/lastfm_extract.py
python src/extractors/musicbrainz_extract.py
```

### Semana 2 — Transformação (Silver)

```bash
python src/transform/process_silver.py
```

Produz: `data/silver/dataset_integrado.csv`

### Semana 3 — Transformação (Gold) + Load

```bash
# 1. Construir camada Gold (modelo dimensional em CSV)
python src/transform/process_gold.py

# 2. Criar o schema SQLite
python src/load/create_schema.py

# 3. Carregar dados para a base de dados
python src/load/load_data.py
```

Produz: `data/gold/` (CSVs) e `data/music_analytics.db` (SQLite)

O script `load_data.py` imprime automaticamente um relatório de validação pós-load com contagens e verificações de integridade referencial.

## Modelo de Dados

O modelo é um **Star Schema** com as seguintes tabelas:

| Tabela | Tipo | Descrição |
|--------|------|-----------|
| `dim_artists` | Dimensão | Artistas com métricas Last.fm e biography |
| `dim_tracks` | Dimensão | Faixas com metadados Spotify e MusicBrainz |
| `fact_popularity` | Factos | Métricas de popularidade por artista e faixa |

Ver diagrama completo em [docs/modelo_ER.md](docs/modelo_ER.md).

## Documentação Adicional

- [docs/fontes.md](docs/fontes.md) — Inventário de fontes e licenças
- [docs/dicionario.md](docs/dicionario.md) — Dicionário de dados
- [docs/modelo_ER.md](docs/modelo_ER.md) — Diagrama ER e decisões de modelação
- [docs/relatorio_qualidade.md](docs/relatorio_qualidade.md) — Relatório de qualidade (Semana 2)
- [docs/relatorio_validacao_load.md](docs/relatorio_validacao_load.md) — Relatório de validação pós-load (Semana 3)
- [docs/IA_LOG.md](docs/IA_LOG.md) — Registo de uso de IA
