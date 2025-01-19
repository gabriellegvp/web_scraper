# Web Scraper com Backend

Um projeto de web scraping desenvolvido com BeautifulSoup e Flask, projetado para coletar dados de páginas web e disponibilizá-los por meio de uma API.

## Recursos
- Extração de dados estruturados de sites.
- API para consultar os dados extraídos.
- Exportação de dados para formatos como JSON ou CSV.

## Como Configurar
1. Clone o repositório:  
   git clone <url-do-repositorio>
2. Instale as dependências:  
   pip install -r requirements.txt
3. Execute o servidor:  
   flask run

## Endpoints Principais
- POST /scrape  
  Entrada: URL do site para scraping.  
  Saída: Dados extraídos.  

- GET /data  
  Retorna os dados extraídos em JSON.  

## Exemplos
1. Solicite o scraping de um site:  
   ```bash
   curl -X POST http://localhost:5000/scrape -d '{"url": "https://exemplo.com"}'
