# Relatório de Validação Pós-Load (Semana 3)

## 1. Ambiente de Execução

- Motor: **SQLite** (`data/music_analytics.db`)
- Script de carga: `src/load/load_data.py`
- Data de execução: 2026-06-04

## 2. Resultados das Verificações

| Verificação | Resultado | Estado |
|-------------|-----------|--------|
| Total de artistas carregados | 24 723 | OK |
| Total de faixas carregadas | 101 813 | OK |
| Total de factos carregados | 101 813 | OK |
| Factos sem artista correspondente | 0 | OK |
| Factos sem faixa correspondente | 0 | OK |
| Faixas sem artista correspondente | 0 | OK |
| Artistas duplicados em `dim_artists` | 0 | OK |

Todas as verificações de integridade referencial passaram sem alertas.

## 3. Análise de Completude

A completude dos dados enriquecidos é reduzida, conforme já documentado no **Relatório de Qualidade (Semana 2)**. Os valores abaixo são esperados e não representam falhas de carga:

| Coluna | Valores não-nulos | Cobertura |
|--------|-------------------|-----------|
| `playcount` (artistas) | ~410 | ~1.7% |
| `listeners` (artistas) | ~410 | ~1.7% |
| `tags_genres_era` | ~307 | ~1.2% |
| `biography` | ~381 | ~1.5% |
| `release_country` | ~8 | <0.1% |

**Causa:** A extração das APIs (Last.fm, MusicBrainz, Wikipedia) foi executada apenas para uma amostra reduzida de artistas por restrições de rate-limiting. Os nulos resultam do `LEFT JOIN` que preserva a totalidade do dataset Spotify (101 813 faixas). Esta decisão está documentada no Relatório de Qualidade da Semana 2.

## 4. Índices e Performance

Os seguintes índices foram criados no schema:

```sql
CREATE INDEX idx_fact_artist  ON fact_popularity(artist_id);
CREATE INDEX idx_fact_track   ON fact_popularity(track_id);
CREATE INDEX idx_track_artist ON dim_tracks(artist_id);
```

Estes índices aceleram as queries mais previsíveis do dashboard: filtrar factos por artista, juntar faixas com métricas, e agregar por artista.

## 5. Decisão de Estratégia de Carga

Foi implementada uma **carga completa (full load)** com `if_exists="replace"`, ou seja, cada execução do script substitui os dados existentes. Esta abordagem é adequada para o tamanho atual do dataset e para o contexto académico do projeto. Uma estratégia incremental (upsert por chave) seria recomendada para produção.
