# Dicionário de Dados - Camada Silver (`dataset_integrado.csv`)

Este documento descreve as colunas presentes no dataset consolidado após a integração das fontes Spotify, Last.fm, MusicBrainz e Wikipedia.

| Coluna | Tipo de Dado | Origem | Descrição |
| :--- | :--- | :--- | :--- |
| `artist_name` | String | Spotify | Nome original do artista. |
| `track_name` | String | Spotify | Nome original da faixa. |
| `artist_uri` | String | Spotify | Identificador único do artista no ecossistema Spotify. |
| `track_uri` | String | Spotify | Identificador único da faixa no ecossistema Spotify. |
| `mbi_id` | String | Last.fm | MusicBrainz Identifier recolhido através do Last.fm. |
| `playcount` | Float | Last.fm | Número total de reproduções globais do artista no Last.fm. |
| `listeners` | Float | Last.fm | Número de ouvintes únicos do artista no Last.fm. |
| `tags_genres_era` | String | Last.fm | Lista de tags associadas ao artista (ex: 'pop', '80s', 'rock'). |
| `mbi_id_mb` | String | MusicBrainz | MusicBrainz Identifier recolhido diretamente da API do MusicBrainz. |
| `release_country` | String | MusicBrainz | Código do país de lançamento da faixa (ex: 'US', 'GB', 'FR'). |
| `release_date` | Datetime | MusicBrainz | Data de lançamento original da faixa. |
| `label` | String | MusicBrainz | Editora discográfica associada ao lançamento original. |
| `biography` | String | Wikipedia | Resumo biográfico ou contexto histórico do artista em texto livre. |

### Notas de Qualidade de Dados
* As colunas oriundas do Last.fm e Wikipedia foram integradas usando uma aproximação de chave pelo nome do artista (`artist_name` convertido para minúsculas).
* As colunas oriundas do MusicBrainz foram integradas usando chave composta (`artist_name` + `track_name` limpos de parênteses e hífens). Devido à rigidez de correspondência da API do MusicBrainz, estas colunas apresentam uma alta taxa de valores nulos estruturais.