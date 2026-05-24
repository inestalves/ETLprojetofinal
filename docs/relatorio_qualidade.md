# Relatório de Qualidade de Dados e Transformação (Semana 2)

## 1. Processo de Limpeza e Normalização
Durante a construção da camada *Silver*, foram aplicadas as seguintes transformações aos dados extraídos (camada *Raw*):

* **Padronização de Chaves:** Os nomes dos artistas (`artist_name`) foram convertidos para minúsculas e os espaços extra foram removidos (`strip()`) para evitar falhas no cruzamento de dados devido a diferenças de *casing*.
* **Limpeza de Títulos de Faixas (RegEx):** Os nomes das faixas provenientes do Spotify continham frequentemente metadados extra (ex: `(feat. Ciara)`, `[Radio Edit]`, ou `- Remastered`). Utilizámos Expressões Regulares (`re.sub`) para remover conteúdos entre parênteses e cortar tudo o que surgisse após um hífen. Isto foi crucial para aumentar a taxa de correspondência com a API estrita do MusicBrainz.
* **Tipagem de Dados:** * As métricas `playcount` e `listeners` do Last.fm foram forçadas para tipos numéricos (`float64`), convertendo eventuais anomalias de texto em nulos.
  * A coluna `release_date` foi convertida para o formato nativo `datetime64` do Pandas, preparando os dados para análises temporais na Semana 3.

## 2. Estratégia de Integração (Joins)
O *Dataset* do Spotify foi utilizado como tabela principal (Base) para garantir que nenhuma faixa da amostra original fosse perdida (utilização de *Left Joins*).
* **Last.fm:** O cruzamento foi efetuado apenas pela chave `artist_name`, uma vez que a extração focou-se nas métricas de popularidade global do artista.
* **MusicBrainz:** O cruzamento foi efetuado pela chave composta `[artist_name, track_name]`.
* **Wikipedia:** O cruzamento foi efetuado pela chave `artist_name`.

## 3. Análise de Valores Nulos e Limitações
A análise à tabela final (`dataset_integrado.csv`) revelou uma elevada presença de valores nulos (cerca de 66.000 registos sem dados enriquecidos). Após auditoria à arquitetura, concluímos que existem duas naturezas distintas para estes nulos:

1. **Nulos por Amostragem (Maioria):** O *Dataset* base do Spotify contém 67.503 faixas. No entanto, por restrições de tempo de processamento e limites de *rate-limiting* das APIs na Semana 1, os scripts de extração (Last.fm, MusicBrainz e Wikipedia) foram executados apenas para uma **amostra reduzida** (entre 100 a 1000 registos). Devido à natureza do `LEFT JOIN` (que preserva a tabela base na íntegra), as dezenas de milhares de faixas que não foram alvo de extração resultaram naturalmente em nulos.
2. **Nulos Estruturais (API Mismatch):** Nas faixas que foram efetivamente alvo de pesquisa, o Last.fm e a Wikipedia apresentaram uma excelente taxa de correspondência. Em contrapartida, o MusicBrainz apresentou valores nulos estruturais (originalmente gravados como `"Unknown"`). Esta limitação deve-se à elevada sensibilidade da API do MusicBrainz a pequenas variações nos títulos de faixas que não correspondam exatamente ao lançamento oficial em álbum.

**Decisão:** Decidimos preservar os nulos gerados pelo `LEFT JOIN`, pois mantêm a integridade da amostra original do Spotify, permitindo-nos escalar a extração no futuro sem alterar o código da camada de transformação.
