from flask import Flask, request, jsonify, render_template, make_response
from scraper import scrape_website
import json
import os
from datetime import datetime

# Inicialização do app Flask
app = Flask(__name__)

# Caminho para salvar os dados extraídos
DATA_FILE = os.path.join("data", "extracted_data.json")

def save_data(data):
    """Salva os dados extraídos em um arquivo JSON."""
    try:
        if not os.path.exists("data"):
            os.makedirs("data")
        with open(DATA_FILE, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Erro ao salvar os dados: {e}")

def load_data():
    """Carrega os dados extraídos de um arquivo JSON."""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as file:
                return json.load(file)
        return {"status": "success", "data": []}
    except Exception as e:
        print(f"Erro ao carregar os dados: {e}")
        return {"status": "error", "message": str(e)}

def log_request(data):
    """Registra informações das requisições em um arquivo de log."""
    try:
        log_file = "data/request_logs.txt"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {json.dumps(data)}\n"
        with open(log_file, "a") as file:
            file.write(log_entry)
    except Exception as e:
        print(f"Erro ao registrar log: {e}")

@app.route("/")
def home():
    """
    Página inicial da aplicação.
    Oferece uma interface amigável para o usuário realizar scraping.
    """
    return render_template("index.html")

@app.route("/scrape", methods=["POST"])
def scrape():
    """
    Endpoint para realizar o scraping de uma URL específica.
    Recebe um JSON contendo a URL e retorna os dados extraídos.

    Exemplo de entrada:
    {
        "url": "https://exemplo.com"
    }
    """
    data = request.json
    if not data or not data.get("url"):
        return jsonify({"status": "error", "message": "URL não fornecida"}), 400

    url = data["url"]
    log_request({"action": "scrape", "url": url})

    result = scrape_website(url)
    if result["status"] == "success":
        save_data(result)
        return jsonify(result), 200
    else:
        return jsonify(result), 500

@app.route("/data", methods=["GET"])
def get_data():
    """
    Endpoint para recuperar os dados extraídos previamente.
    Retorna um JSON contendo os dados salvos localmente.
    """
    log_request({"action": "get_data"})
    data = load_data()
    return jsonify(data), 200

@app.route("/download", methods=["GET"])
def download_data():
    """
    Permite que o usuário baixe os dados extraídos como um arquivo JSON.
    """
    log_request({"action": "download_data"})
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            data = file.read()
        response = make_response(data)
        response.headers["Content-Disposition"] = "attachment; filename=extracted_data.json"
        response.headers["Content-Type"] = "application/json"
        return response
    else:
        return jsonify({"status": "error", "message": "Nenhum dado disponível para download"}), 404

@app.route("/clear_data", methods=["POST"])
def clear_data():
    """
    Limpa os dados salvos localmente, permitindo reiniciar o scraping.
    """
    log_request({"action": "clear_data"})
    try:
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        return jsonify({"status": "success", "message": "Dados excluídos com sucesso"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.errorhandler(404)
def not_found_error(error):
    """
    Tratamento para erros 404 (página não encontrada).
    """
    log_request({"action": "error", "error": "404 Not Found"})
    return jsonify({"status": "error", "message": "Página não encontrada"}), 404

@app.errorhandler(500)
def internal_error(error):
    """
    Tratamento para erros 500 (erro interno do servidor).
    """
    log_request({"action": "error", "error": "500 Internal Server Error"})
    return jsonify({"status": "error", "message": "Erro interno do servidor"}), 500

@app.route("/logs", methods=["GET"])
def get_logs():
    """
    Retorna os logs de requisições registrados no servidor.
    """
    try:
        log_file = "data/request_logs.txt"
        if os.path.exists(log_file):
            with open(log_file, "r") as file:
                logs = file.readlines()
            return jsonify({"status": "success", "logs": logs}), 200
        else:
            return jsonify({"status": "success", "logs": []}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # Garante que o diretório de dados exista antes de iniciar o servidor
    os.makedirs("data", exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=5000)
