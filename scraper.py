import requests
from bs4 import BeautifulSoup

def scrape_website(url):
    """
    Faz o scraping de uma URL específica, extraindo os elementos 'h2'.

    Args:
        url (str): A URL da página a ser analisada.

    Returns:
        dict: Um dicionário contendo o status e os dados extraídos.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Verifica se a resposta é 200 OK.
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extraindo os elementos desejados (personalizável)
        headers = soup.find_all("h2")
        data = [header.text.strip() for header in headers]

        return {"status": "success", "data": data}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}
