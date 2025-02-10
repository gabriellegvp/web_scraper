# Web Scraper com Backend

Um projeto de web scraping desenvolvido com **BeautifulSoup** e **Flask**, projetado para coletar dados de páginas web e disponibilizá-los por meio de uma API RESTful. Ideal para extrair informações estruturadas de sites e exportá-las em formatos como JSON ou CSV.

---

## Recursos Principais

- **Extração de dados estruturados**: Coleta de elementos HTML como títulos (`h1`, `h2`), parágrafos (`p`), links (`a`), etc.
- **API RESTful**: Endpoints para realizar scraping e consultar os dados extraídos.
- **Exportação de dados**: Suporte para exportar dados em JSON ou CSV.
- **Cache de requisições**: Evita requisições repetidas à mesma URL.
- **Autenticação básica**: Proteção de endpoints sensíveis.
- **Logs de requisições**: Registro de todas as operações para auditoria.

---

## Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- Python 3.8 ou superior
- pip (gerenciador de pacotes do Python)

---

## Como Configurar

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/gabriellegvp/web_scraper.git
   cd web_scraper