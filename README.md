# ETLprojetofinal - Análise de Tendências Musicais Globais

Este projeto consiste num pipeline ETL (Extract, Transform, Load) modular, desenvolvido para extrair e processar dados musicais de diversas fontes (Spotify, Wikipedia, Last.fm e MusicBrainz). O objetivo principal é analisar que fatores influenciam as tendências musicais em diferentes países, recorrendo a um modelo de dados dimensional desenhado e construído de raiz.

## Estrutura do Projeto

```text
ETLprojetofinal/
├── data/
│   ├── raw/              # Dados brutos e amostras extraídas (Bronze Layer)
│   ├── silver/           # Dados integrados e transformados
│   └── gold/             # Tabelas prontas para modelo analítico (BD SQLite)
├── docs/                 # Documentação do projeto
├── src/
│   ├── extractors/       # Scripts de extração de dados das APIs e Scraping
│   ├── transform/        # Limpeza, validação e integração de dados
│   ├── load/             # Criação e carregamento da base de dados
│   ├── dashboard/        # Aplicação Streamlit de visualização de dados
│   └── utils/            # Funções auxiliares e utilitárias
├── .env.example          # Exemplo de configuração de chaves de API
├── .gitignore            # Configuração de ficheiros a ignorar pelo Git
├── requirements.txt      # Dependências do projeto
└── README.md             # Documentação principal
```

---

## Fluxo do Pipeline (Fases)

### 1. Extração (Extract - Semana 1)
O pipeline inicia com a extração a partir de 4 fontes:
1. **Spotify**: Extração de metadados a partir do *Million Playlist Dataset* (amostra em CSV ou ZIP).
2. **Wikipedia**: Obtenção de biografias de artistas via REST API.
3. **Last.fm**: Recolha de métricas de popularidade (ouvintes, playcount) e tags de género/época.
4. **MusicBrainz**: Cruzamento de dados para obtenção de países de lançamento e editoras.

### 2. Transformação (Transform - Semana 2)
Implementado seguindo a arquitetura medallion:
- `process_silver.py`: Realiza a limpeza dos dados da camada Bronze (raw), lida com missings, padroniza nomes, remove duplicados e integra todas as fontes. 
- `process_gold.py`: Constrói a estrutura dimensional preparando fact tables e dimension tables para a base de dados.

### 3. Carregamento (Load - Semana 3)
Carga dos dados para a estrutura de serviço analítico:
- O armazenamento é feito através de **SQLite**, utilizando o *Star Schema*. 
- `create_schema.py`: Gera as tabelas e relações na base de dados (`data/music_analytics.db`).
- `load_data.py`: Preenche a base de dados com as informações da camada Gold.

### 4. Visualização (Semana 4)
- Um **Dashboard Interativo** criado em **Streamlit** (em `src/dashboard/app.py`).
- Analisa tendências, a dominância geográfica e diferenças entre ouvintes de curto e longo prazo.

---

## 🛠️ Configuração e Execução

### 1. Pré-requisitos
* Python 3.9 ou superior.

### 2. Instalação de Dependências
Instale as bibliotecas necessárias utilizando o ficheiro de requisitos:
```bash
pip install -r requirements.txt
```

### 3. Configuração do Ambiente (.env)
1. Crie um ficheiro chamado `.env` na raiz do projeto.
2. Copie o conteúdo de `.env.example` para o seu `.env`.
3. Preencha com as suas chaves de API (necessárias para Last.fm e MusicBrainz).

### 4. Execução do Pipeline

A execução deve respeitar a ordem do processo ETL. Na raiz do projeto, execute:

**A. Extração**
```bash
python src/extractors/spotify_extract.py
python src/extractors/scrape_wiki.py
python src/extractors/lastfm_extract.py
python src/extractors/musicbrainz_extract.py
```

**B. Transformação**
```bash
python src/transform/process_silver.py
python src/transform/process_gold.py
```

**C. Carregamento**
```bash
python src/load/create_schema.py
python src/load/load_data.py
```

**D. Dashboard**
```bash
streamlit run src/dashboard/app.py
```

---

## 📄 Documentação Adicional

Todos os relatórios e documentação técnica encontram-se na pasta `docs/`.

* [**Relatório Técnico Final**](docs/relatorio_final.md): Consolidação de todas as decisões arquiteturais, insights descobertos e avaliação técnica global.
* [**Dicionário de Dados**](docs/dicionario.md): Detalha todos os campos disponíveis na base de dados (Schema).
* [**Modelo Entidade-Relacionamento (ER)**](docs/modelo_ER.md): Diagrama lógico da Base de Dados de analítica (Star Schema).
* [**Fontes e Inventário**](docs/fontes.md): Detalhes de restrições legais e uso das fontes.
* [**Relatório de Qualidade**](docs/relatorio_qualidade.md): Evidência de regras e métricas de consistência durante as transformações.
* [**Registo de IA**](docs/IA_LOG.md): Relatório do uso de IA (Spec-Driven approach).
