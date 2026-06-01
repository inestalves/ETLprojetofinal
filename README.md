ETLprojetofinal - Análise de Tendências Musicais Globais

Este projeto consiste num pipeline ETL (Extract, Transform, Load) modular, desenvolvido para extrair e processar dados musicais de diversas fontes (Spotify, Wikipedia, Last.fm e MusicBrainz). O objetivo principal é analisar que fatores influenciam as tendências musicais em diferentes países.

## Estrutura do Projeto

ETLprojetofinal/
├── data/
│   └── raw/              # Dados brutos e amostras extraídas (Bronze Layer)
├── docs/                 # Documentação do projeto (Fontes, IA Log, etc.)
├── src/
│   ├── extractors/       # Scripts de extração de dados das APIs e Scraping
│   └── utils/            # Funções auxiliares e utilitárias
├── .env.example          # Exemplo de configuração de chaves de API
├── .gitignore            # Configuração de ficheiros a ignorar pelo Git
├── requirements.txt      # Dependências do projeto
└── README.md             # Documentação principal



## Fluxo de Extração (Semana 1)

O pipeline atual realiza as seguintes operações:

1. **Spotify**: Extração de metadados a partir do *Million Playlist Dataset* (ZIP).
2. **Wikipedia**: Obtenção de biografias de artistas via REST API.
3. **Last.fm**: Recolha de métricas de popularidade (ouvintes, playcount) e tags de género/época.
4. **MusicBrainz**: Cruzamento de dados para obtenção de países de lançamento e editoras.


## 🛠️ Configuração e Instalação

### 1. Pré-requisitos

* Python 3.9 ou superior.

### 2. Instalação de Dependências

Instale as bibliotecas necessárias utilizando o ficheiro de requisitos:

pip install -r requirements.txt


### 3. Configuração de APIs

1. Crie um ficheiro chamado `.env` na raiz do projeto.
2. Copie o conteúdo de `.env.example` para o seu `.env`.
3. Preencha com as suas chaves de API (Last.fm e MusicBrainz).

## Execução

Para correr os extratores, execute os scripts a partir da raiz do projeto:

# Extrair dados do Spotify
python src/extractors/spotify_extract.py

# Extrair biografias da Wikipedia
python src/extractors/scrape_wiki.py

# Extrair dados do Last.fm
python src/extractors/lastfm_extract.py

# Extrair dados do MusicBrainz
python src/extractors/musicbrainz_extract.py


## 📄 Documentação Adicional

* Inventário de Fontes: Detalhes sobre as APIs e licenças.
* Registo de IA : Documentação da metodologia Spec-Driven e uso de IA.

## Estratégia de Modelação (Camada Gold)

Para a construção do Data Warehouse analítico, optou-se por um **Modelo em Estrela (Star Schema)**, desenhado para otimizar a agregação de dados e a performance das *queries* no futuro Dashboard.

O modelo é composto por:
* **Tabela de Factos (`Fact_Trends`):** Centraliza as métricas quantitativas de popularidade (`playcount`, `listeners`) obtidas do Last.fm. Granularidade: Uma linha por cada par Artista-Faixa.
* **Dimensões:**
  * **`Dim_Artist`**: Contém os atributos descritivos do artista (nome, biografia da Wikipedia e *tags* de género musical).
  * **`Dim_Track`**: Contém os detalhes da música (nome da faixa e editora/label).
  * **`Dim_Geography`**: Isola o país de lançamento (`release_country`) para permitir o filtro geográfico das tendências.
  * **`Dim_Date`**: Derivada da data de lançamento (`release_date`), permitindo agregar tendências por ano ou década.

  erDiagram
    Fact_Trends {
        int fact_id PK
        string artist_uri FK
        string track_uri FK
        int geo_id FK
        int date_id FK
        float playcount
        float listeners
    }

    Dim_Artist {
        string artist_uri PK
        string artist_name
        string mbi_id
        string tags_genres_era
        text biography
    }

    Dim_Track {
        string track_uri PK
        string track_name
        string label
    }

    Dim_Geography {
        int geo_id PK
        string release_country
    }

    Dim_Date {
        int date_id PK
        date release_date
        int release_year
    }

    Fact_Trends }|--|| Dim_Artist : "tem"
    Fact_Trends }|--|| Dim_Track : "refere"
    Fact_Trends }|--|| Dim_Geography : "ocorre em"
    Fact_Trends }|--|| Dim_Date : "lançado em"