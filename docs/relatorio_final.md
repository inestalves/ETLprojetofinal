# Relatório Técnico Final Consolidado

Este relatório final descreve a implementação do pipeline de dados, a arquitetura técnica adotada, e as conclusões analíticas do projeto focado nas tendências musicais globais.

## 1. Contexto do Problema e Objetivos
O projeto teve como objetivo recolher dados crus do **Spotify Million Playlist Dataset**, enriquecê-los com APIs externas e cruzar esses dados de forma a tentar entender as características que influenciam a popularidade de artistas e faixas a nível mundial. Pretendia-se também perceber as origens geográficas de faixas de sucesso e traçar diferenças entre os utilizadores curadores do Spotify e utilizadores scrobblers do Last.fm.

## 2. Arquitetura e Pipeline Modular

O projeto foi organizado de forma puramente modular, assegurando as etapas de Extração, Transformação, Carregamento e Visualização.

*   **Extract:** Extração agendada/customizada que recolhe os dados da amostra do Spotify, consome dados descritivos através de *web scraping* oficial à Wikipedia (via a sua REST API), e consome metadados e estatísticas das APIs do Last.fm e MusicBrainz. Os resultados foram dispostos em `/data/raw` (Bronze Layer).
*   **Transform:** Foi adotada uma arquitetura estruturada do tipo *Medallion*. Os scripts em `src/transform/` leem os dados raw, filtram nulos e *outliers*, normalizam a informação (`process_silver.py`), e posteriormente agregam as chaves principais transformando o dataset de forma a estar pronto para a carga analítica (`process_gold.py`).
*   **Load:** Considerando o ambiente de avaliação local e ausência de restrições de cloud obrigatória, foi adotado o **SQLite**. Construiu-se um modelo dimensional (Star Schema) assente no script de schema (`create_schema.py`) onde uma `fact_popularity` cruza chaves com a `dim_artists` e `dim_tracks`.
*   **Visualização:** Utilização de **Streamlit** (através da `plotly` para renderização), por garantir portabilidade e uma criação veloz e robusta de uma aplicação interativa local.

## 3. Fontes de Dados e Qualidade

**Fontes Utilizadas:**
1.  **Spotify:** Dataset de 1 Milhão de Playlists (Amostra Estática). Base principal de extração.
2.  **Wikipedia:** Usada para enriquecimento biográfico dos artistas.
3.  **Last.fm (API):** Crucial para recolher estatísticas globais alternativas de *listeners* e *playcounts*.
4.  **MusicBrainz:** Fonte focada nos domínios geográficos (país de origem) e identificadores técnicos das faixas musicais.

**Desafios e Qualidade de Dados:**
A integração demonstrou dificuldades na agregação entre as APIs, especialmente devido à discrepância de chaves únicas (falta do Spotify URI em muitos resultados do MusicBrainz). Isto forçou a adoção de técnicas de cruzamento mistas (por título+artista). As métricas de *missing values* e deduplicação foram documentadas no ficheiro `relatorio_qualidade.md`.

## 4. Resultados e Insights Analíticos

As principais descobertas suportadas pelo Dashboard incluem:

*   **Dicotomia de Géneros Plataforma-Dependentes:** Constatou-se que as curadorias do Spotify (Playlists) dão prioridade a fenómenos contemporâneos como o Hip-Hop (Trap, Cloud Rap). Em contraponto, o número de ouvintes globais agregados (no Last.fm) sublinha o peso de géneros de longo curso como o Rock e Pop Alternativo.
*   **Popularidade vs Presença (Correlação fraca):** Ter milhões de ouvintes não implica ser promovido fortemente em centenas de playlists. Isto reflete os dois padrões de sucesso na música: sucessos explosivos/momentâneos vs audiências consolidadas ao longo de décadas.
*   **Dominância Anglo-Americana:** Cerca de 44% das faixas com país identificado nos metadados apontam para os EUA, e em seguida, Reino Unido. Contudo, **identificou-se uma limitação forte nos dados**: apenas 0,3% das faixas dispõe de origem perfeitamente etiquetada no MusicBrainz dentro da nossa amostra, o que inviabiliza deduções perfeitas de regionalidade global.

## 5. Próximos Passos e Limitações
A maior limitação encontra-se na baixa cobertura da chave primária (MBID) e país de lançamento. Em trabalhos futuros, recomenda-se:
1.  Aprofundar a técnica de `fuzzy matching` entre os nomes do Spotify e a base do MusicBrainz para aumentar o número de registos de metadados geográficos apurados.
2.  Adicionar um *Orquestrador* puro (como Airflow ou Prefect) ao pipeline para mitigar falhas ao encadear os scripts sequencialmente.
3.  Implantar a base de dados numa Cloud (ex: BigQuery, Snowflake) para escalar as *queries* quando o milhão de playlists fosse injetado na íntegra.
