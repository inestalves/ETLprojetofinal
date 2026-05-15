# Inventário das Fontes de Dados - Semana 1

Este documento detalha as fontes de dados selecionadas para o projeto, respondendo à pergunta de investigação: *"Que fatores influenciam as tendências musicais em cada país?"*

## 1. Fonte de Maior Volume: Spotify Million Playlist Dataset (MPD)

* 
**Descrição:** Dataset estático principal contendo metadados de 1 milhão de playlists criadas por utilizadores do Spotify.


* **Objetivo:** Extrair uma lista de identificadores únicos (URIs) de faixas e artistas para servir de base às extrações subsequentes.
* **Acessibilidade e Licença:** Acesso público para fins de investigação (via AIcrowd). Não permite uso comercial.
* **Volume/Desafios Técnicos:** ~33 GB descompactado. Exige processamento em blocos (*chunks*) e amostragem local para evitar sobrecarga de memória.

## 2. API Principal: Spotify Web API

* 
**Descrição:** API oficial do Spotify.


* **Objetivo:** Cruzar os URIs obtidos no MPD para extrair *audio features* (dançabilidade, energia, tempo) e métricas de popularidade/mercados disponíveis (países).
* **Acessibilidade e Licença:** Gratuita mediante registo de aplicação de developer e geração de tokens OAuth 2.0.
* **Restrições:** Limites de taxa (*rate limits*) dinâmicos. A equipa implementará pausas temporais (*sleep*) em caso de erro 429.

## 3. APIs Complementares: Last.fm API & MusicBrainz

* 
**Descrição:** APIs públicas de metadados musicais globais.


* **Objetivo:** Enriquecer os dados dos artistas e faixas com *tags* de género musical (que o Spotify por vezes omite) e dados de *scrobbles* globais para validação cruzada de tendências.
* **Acessibilidade e Licença:** Uso gratuito para projetos não comerciais.
* **Restrições:** Last.fm tem um limite aproximado de 5 pedidos por segundo.

## 4. Fonte Complementar (Scraping/API API): Wikipedia REST API

* **Descrição:** Endpoint oficial da Wikipedia para resumos de artigos.
* **Objetivo:** Obter uma biografia curta e descritiva para contextualizar os artistas selecionados na nossa amostra.
* **Acessibilidade e Licença:** API pública e aberta (Licença CC BY-SA 3.0).
* 
**Restrições:** Exige a inclusão de um cabeçalho descritivo (`User-Agent`) explícito para não sobrecarregar os servidores. A equipa adotou a API REST (`/page/summary/`) após pivot arquitetural para evitar a instabilidade do *Web Scraping* tradicional em HTML.
