import requests
from bs4 import BeautifulSoup
from functools import lru_cache
from urllib.parse import urljoin

# Cache simples para evitar requisições repetidas à mesma URL
@lru_cache(maxsize=100)
def fetch_url_content(url, headers=None, timeout=10):
    """
    Faz uma requisição HTTP e retorna o conteúdo da resposta.

    Args:
        url (str): A URL a ser requisitada.
        headers (dict): Cabeçalhos personalizados para a requisição.
        timeout (int): Tempo máximo de espera para a requisição.

    Returns:
        str: O conteúdo da resposta.
    """
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()  # Verifica se a resposta é 200 OK.
        return response.text
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Erro ao acessar a URL: {e}")

def scrape_website(url, elements=None, extract_links=False, headers=None, timeout=10):
    """
    Faz o scraping de uma URL específica, extraindo elementos HTML e/ou links.

    Args:
        url (str): A URL da página a ser analisada.
        elements (list): Lista de elementos HTML a serem extraídos (ex: ["h1", "h2", "p"]).
        extract_links (bool): Se True, extrai URLs de links na página.
        headers (dict): Cabeçalhos personalizados para a requisição.
        timeout (int): Tempo máximo de espera para a requisição.

    Returns:
        dict: Um dicionário contendo o status e os dados extraídos.
    """
    try:
        # Validação dos elementos a serem extraídos
        if elements is None:
            elements = ["h2"]  # Padrão: extrair apenas h2

        # Faz a requisição e obtém o conteúdo da página
        content = fetch_url_content(url, headers=headers, timeout=timeout)

        # Verifica se o conteúdo é HTML
        if not content.strip().lower().startswith("<!doctype html>"):
            return {"status": "error", "message": "O conteúdo não é HTML"}

        # Parseia o conteúdo com BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')

        # Extrai os elementos desejados
        extracted_data = {}
        for element in elements:
            tags = soup.find_all(element)
            extracted_data[element] = [tag.text.strip() for tag in tags]

        # Extrai links, se solicitado
        if extract_links:
            links = soup.find_all("a", href=True)
            extracted_data["links"] = [urljoin(url, link["href"]) for link in links]

        return {"status": "success", "data": extracted_data}

    except RuntimeError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"Erro inesperado: {e}"}

# Exemplo de uso
if __name__ == "__main__":
    url = "https://example.com"
    result = scrape_website(
        url,
        elements=["h1", "h2", "p"],  # Extrai h1, h2 e parágrafos
        extract_links=True,  # Extrai links
        headers={"User-Agent": "Mozilla/5.0"},  # Cabeçalhos personalizados
        timeout=15  # Timeout de 15 segundos
    )
    print(result)