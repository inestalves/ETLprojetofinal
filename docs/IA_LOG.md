# Registo de Uso de IA - Semana 1 (Módulo de Extração)

## 1. Abordagem Metodológica

A equipa adotou uma abordagem *Spec-Driven Development* para a construção do módulo de extração complementar (Wikipedia). Antes da geração de código, definimos a intenção e os requisitos técnicos, utilizando a IA (Gemini) como parceira de *pair programming* e revisão arquitetural.

### 1.1. Intenção e Requisitos Iniciais

* 
**Objetivo:** Construir um script em Python para obter uma biografia curta de artistas extraídos do *Million Playlist Dataset*.


* 
**Entradas:** Ficheiro CSV com `artist_name` únicos.


* 
**Saídas:** Ficheiro JSON com o mapeamento `"Nome do Artista": "Biografia"`.


* 
**Restrições:** Evitar sobrecarga dos servidores e garantir rastreabilidade.


* 
**Critérios de Aceitação:** O script deve ignorar artistas sem página, extrair apenas texto legível (sem formatação HTML) e ser executável localmente.



2. Iterações e Validação Humana 

### Iteração 1: Web Scraping Tradicional

* **Prompt/Intenção:** Solicitação da geração de um script modular usando `requests` e `BeautifulSoup` com base nos requisitos acima definidos.
* **Resultado da IA:** Código gerado corretamente em termos de sintaxe.
* **Validação Humana:** O código falhou ao executar na maioria dos artistas (erro 403 / "Página não encontrada"). A equipa detetou que a Wikipedia bloqueia pedidos automáticos sem identificação clara.
* 
**Decisão:** Rejeitada a implementação inicial. Foi pedido à IA para ajustar a implementação introduzindo boas práticas de ética de *scraping*.



### Iteração 2: Adição de User-Agent e Regras de Qualidade

* **Prompt/Intenção:** Alterar a função para incluir cabeçalhos (`User-Agent`) e adicionar filtros de qualidade (ignorar páginas de desambiguação e extrair parágrafos com mais de 100 caracteres).
* **Resultado da IA:** O código contornou os bloqueios e adicionou os filtros.
* **Validação Humana:** A extração funcionou para alguns artistas (ex: Missy Elliott), mas falhou em páginas de desambiguação ("Shaggy") e quebrou em URLs com espaços invisíveis ou caracteres especiais (ex: "Beyoncé").
* 
**Decisão:** A equipa avaliou que o HTML da Wikipedia era demasiado variável para garantir a robustez de um *pipeline* de dados contínuo.



### Iteração 3: Pivot Arquitetural para API Oficial

* **Discussão:** A equipa interveio e, com a consultoria da IA, concluiu que fazer *scrape* a HTML é frágil face à existência de uma alternativa melhor estruturada.
* **Desenho Final:** Mudança do *scraper* para consumir o endpoint oficial da Wikipedia REST API (`/api/rest_v1/page/summary/`).
* **Validação Humana:** O código lidou perfeitamente com a codificação de URLs (`urllib.parse.quote`), detectou automaticamente páginas de desambiguação através do campo `type` do JSON devolvido, e extraiu o texto limpo na primeira tentativa.
* **Impacto no Projeto:** O pipeline ficou imensamente mais robusto, rápido e com menor probabilidade de quebrar em extrações futuras. Esta decisão técnica elevou a qualidade dos dados brutos armazenados.



## Semana 2: Transformação e Qualidade de Dados

* **Objetivo:** Desenvolver o script de integração em Pandas (`process_silver.py`) e mitigar problemas de *matching* entre as chaves do Spotify e do MusicBrainz.
* **Uso da IA:** O LLM foi utilizado como assistente de programação para gerar o código de limpeza base e estruturar a arquitetura dos *Joins*.
* **Prompt Principal:** "Preciso de um script em Pandas que faça o Left Join de 4 ficheiros (Spotify, Last.fm, MusicBrainz e Wikipedia). As faixas do Spotify têm metadados como '(feat. X)' que impedem o match com o MusicBrainz. Como posso limpar isso antes do Join?"
* **Ação Humana / Validação:** O código fornecido pela IA tentou inicialmente cruzar o dataset do Last.fm usando a chave `track_name`. No entanto, ao analisar o erro de execução `KeyError`, percebemos que a extração da Semana 1 focava-se no nível do *artista*. O script foi corrigido manualmente pela equipa para realizar o *join* apenas por `artist_name`, o que resolveu o problema estrutural com sucesso. A IA foi também consultada para diagnosticar erros de leitura do Pandas (ex: `EmptyDataError`).

---

## Semana 3: Carregamento (Load) e Modelação

### Intenção e Requisitos

* **Objetivo:** Modelar os dados transformados num Star Schema SQLite e implementar scripts de criação de schema, carga e validação pós-load.
* **Entradas:** `data/silver/dataset_integrado.csv`
* **Saídas:** `data/gold/` (3 CSVs) + `data/music_analytics.db` (SQLite com 3 tabelas)
* **Critérios de aceitação:** 0 falhas de integridade referencial, contagens consistentes entre Gold CSV e SQLite, schema documentado com diagrama ER.

### Desenho aprovado antes da implementação

Foi adotado um **Star Schema** com:
- `dim_artists` — chave surrogate `artist_id`, atributos de artista e métricas Last.fm
- `dim_tracks` — chave surrogate `track_id`, FK para `dim_artists`, metadados Spotify/MusicBrainz
- `fact_popularity` — FK para ambas as dimensões, métricas de popularidade

Motor escolhido: **SQLite** (sem servidor, ficheiro único, local).

### Iterações e Validação Humana

**Iteração 1 — Gold layer**
* **Prompt/Intenção:** Gerar script `process_gold.py` que constrói dimensões e tabela de factos a partir do Silver, usando surrogate keys.
* **Resultado da IA:** Script gerado com `build_dim_artists`, `build_dim_tracks`, `build_fact_popularity`.
* **Validação Humana:** Execução confirmou 24 723 artistas, 101 813 faixas e 101 813 factos. Resultado aceite sem alterações.

**Iteração 2 — Schema e carga**
* **Prompt/Intenção:** Gerar `create_schema.py` com DDL SQLite incluindo chaves primárias, FK e índices, e `load_data.py` com verificações pós-load automáticas.
* **Resultado da IA:** Scripts gerados com PRAGMA foreign_keys, índices sobre `artist_id`/`track_id`, e 7 queries de validação integradas.
* **Validação Humana:** Todas as 7 verificações retornaram OK (0 violações de integridade). Aceite sem alterações.

**Decisão sobre `artist_bios_sample.json`:**
Durante a execução, o `process_silver.py` falhou com `FileNotFoundError` porque o ficheiro estava em `amostras/` mas o script esperava em `data/raw/`. Decisão da equipa: copiar o ficheiro para `data/raw/` e documentar a inconsistência para corrigir na Semana 4.