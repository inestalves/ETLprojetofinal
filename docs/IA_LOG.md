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



