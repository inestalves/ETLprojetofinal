# Dicionário de Dados

Este documento descreve os campos de todas as camadas do pipeline: Silver, Gold (dimensões e factos) e base de dados SQLite final.

---

## Camada Silver — `data/silver/dataset_integrado.csv`

Dataset consolidado após limpeza e integração das quatro fontes.

| Campo | Tipo | Origem | Descrição | Regra de Transformação |
| :--- | :--- | :--- | :--- | :--- |
| `artist_name` | String | Spotify | Nome do artista | Convertido para minúsculas, espaços removidos |
| `track_name` | String | Spotify | Nome da faixa | Removidos `(feat. X)`, `[Radio Edit]`, tudo após hífen; convertido para minúsculas |
| `artist_uri` | String | Spotify | Identificador único do artista no Spotify | Sem transformação |
| `track_uri` | String | Spotify | Identificador único da faixa no Spotify | Sem transformação |
| `playlist_appearances` | Integer | Spotify (raw) | Nº de playlists do MPD que incluem o artista (antes de deduplicação) | Calculado por `groupby('artist_name').size()` no ficheiro raw |
| `mbi_id` | String | Last.fm | MusicBrainz ID recolhido via Last.fm | `"Unknown"` convertido para NULL |
| `playcount` | Float | Last.fm | Total de reproduções globais do artista no Last.fm | Forçado para numérico; erros convertidos para NULL |
| `listeners` | Float | Last.fm | Ouvintes únicos do artista no Last.fm | Forçado para numérico; erros convertidos para NULL |
| `tags_genres_era` | String | Last.fm | Tags do artista (géneros, épocas, estilos) — até 10 tags separadas por vírgula | `"Unknown"` convertido para NULL |
| `mbi_id_mb` | String | MusicBrainz | MusicBrainz ID recolhido diretamente da API MusicBrainz | Sufixo `_mb` para evitar conflito com `mbi_id` do Last.fm |
| `release_country` | String | MusicBrainz | Código ISO do país de lançamento (ex: `US`, `GB`, `FR`) | `"Unknown"` convertido para NULL |
| `release_date` | Datetime | MusicBrainz | Data de lançamento original da faixa | Convertido para `datetime64`; erros convertidos para NULL |
| `label` | String | MusicBrainz | Editora discográfica do lançamento original | `"Unknown"` convertido para NULL |
| `biography` | String | Wikipedia | Resumo biográfico do artista (REST API `/page/summary/`) | Páginas de desambiguação excluídas; só texto com mais de 100 caracteres |

---

## Camada Gold — `data/gold/`

### `dim_artists.csv` — Dimensão de Artistas

| Campo | Tipo | Origem | Descrição |
| :--- | :--- | :--- | :--- |
| `artist_id` | Integer (PK) | Gerado | Surrogate key sequencial |
| `artist_name` | String | Silver | Nome do artista (limpo) |
| `mbi_id` | String | Last.fm | MusicBrainz ID via Last.fm |
| `playcount` | Float | Last.fm | Total de reproduções no Last.fm |
| `listeners` | Float | Last.fm | Ouvintes únicos no Last.fm |
| `tags_genres_era` | String | Last.fm | Tags de géneros e épocas |
| `biography` | String | Wikipedia | Biografia do artista |
| `playlist_appearances` | Integer | Spotify raw | Nº de playlists que incluem o artista |

### `dim_tracks.csv` — Dimensão de Faixas

| Campo | Tipo | Origem | Descrição |
| :--- | :--- | :--- | :--- |
| `track_id` | Integer (PK) | Gerado | Surrogate key sequencial |
| `track_name` | String | Silver | Nome da faixa (limpo) |
| `artist_id` | Integer (FK) | dim_artists | Referência ao artista |
| `track_uri` | String | Spotify | URI único da faixa no Spotify |
| `release_date` | String | MusicBrainz | Data de lançamento |
| `release_country` | String | MusicBrainz | País de lançamento (código ISO) |
| `label` | String | MusicBrainz | Editora discográfica |

### `fact_popularity.csv` — Tabela de Factos

| Campo | Tipo | Origem | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | Integer (PK) | Gerado | Chave primária autoincrement |
| `artist_id` | Integer (FK) | dim_artists | Referência ao artista |
| `track_id` | Integer (FK) | dim_tracks | Referência à faixa |
| `playcount` | Float | Last.fm | Total de reproduções |
| `listeners` | Float | Last.fm | Ouvintes únicos |

---

## Notas de Qualidade

| Coluna | Cobertura | Causa dos nulos |
| :--- | :--- | :--- |
| `playlist_appearances` | 100% (24 723 artistas) | Nenhum nulo — calculado do raw Spotify |
| `listeners` / `playcount` | ~4% (1 000 artistas) | Extração Last.fm limitada aos 1 000 artistas mais populares |
| `tags_genres_era` | ~3.9% (973 artistas) | Idem — alguns artistas não têm tags no Last.fm |
| `release_country` | ~0.3% (318 faixas) | Extração MusicBrainz limitada a 500 faixas; baixa taxa de match |
| `biography` | ~1.5% (381 artistas) | Artistas sem página Wikipedia ou com página de desambiguação |