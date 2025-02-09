from flask import Flask, request, jsonify, render_template, make_response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from werkzeug.security import check_password_hash
from functools import wraps
from scraper import scrape_website
import json
import os
from datetime import datetime
import re

# Inicialização do app Flask
app = Flask(__name__)
CORS(app)  # Habilita CORS para todos os endpoints

# Configuração do rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,  # Limita por endereço IP
    default_limits=["200 per minute"]  # Limite padrão de 200 requisições por minuto
)

# Caminho para salvar os dados extraídos
DATA_FILE = os.path.join("data", "extracted_data.json")

# Configuração de autenticação básica (usuário e senha fictícios)
USER_DATA = {
    "admin": "pbkdf2:sha256:260000$H1v9z5yW$5e8b9f8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0"
}

def basic_auth_required(f):
    """
    Decorador para exigir autenticação básica em endpoints protegidos.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_password_hash(USER_DATA.get(auth.username, ""), auth.password):
            return jsonify({"status": "error", "message": "Autenticação necessária"}), 401
        return f(*args, **kwargs)
    return decorated

def validate_url(url):
    """
    Valida se a URL fornecida é válida.
    """
    regex = re.compile(
        r"^(https?://)?"  # Protocolo (http ou https)
        r"(www\.)?"  # Subdomínio opcional
        r"([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}"  # Domínio e TLD
        r"(/[a-zA-Z0-9-._~:/?#[\]@!$&'()*+,;=]*)?$",  # Caminho e parâmetros
        re.IGNORECASE
    )
    return re.match(regex, url) is not None

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

def log_request(action, details=None):
    """Registra informações das requisições em um arquivo de log estruturado."""
    try:
        log_file = "data/request_logs.json"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "action": action,
            "details": details or {}
        }
        if not os.path.exists("data"):
            os.makedirs("data")
        with open(log_file, "a") as file:
            file.write(json.dumps(log_entry) + "\n")
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
@limiter.limit("10 per minute")  # Limita a 10 requisições por minuto
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
        log_request("scrape", {"status": "error", "message": "URL não fornecida"})
        return jsonify({"status": "error", "message": "URL não fornecida"}), 400

    url = data["url"]
    if not validate_url(url):
        log_request("scrape", {"status": "error", "message": "URL inválida", "url": url})
        return jsonify({"status": "error", "message": "URL inválida"}), 400

    log_request("scrape", {"url": url})
    result = scrape_website(url)

    if result["status"] == "success":
        save_data(result)
        return jsonify(result), 200
    else:
        return jsonify(result), 500

@app.route("/data", methods=["GET"])
@basic_auth_required  # Protege o endpoint com autenticação básica
def get_data():
    """
    Endpoint para recuperar os dados extraídos previamente.
    Retorna um JSON contendo os dados salvos localmente.
    """
    log_request("get_data")
    data = load_data()
    return jsonify(data), 200

@app.route("/download", methods=["GET"])
@basic_auth_required  # Protege o endpoint com autenticação básica
def download_data():
    """
    Permite que o usuário baixe os dados extraídos como um arquivo JSON.
    """
    log_request("download_data")
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
@basic_auth_required  # Protege o endpoint com autenticação básica
def clear_data():
    """
    Limpa os dados salvos localmente, permitindo reiniciar o scraping.
    """
    log_request("clear_data")
    try:
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        return jsonify({"status": "success", "message": "Dados excluídos com sucesso"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/logs", methods=["GET"])
@basic_auth_required  # Protege o endpoint com autenticação básica
def get_logs():
    """
    Retorna os logs de requisições registrados no servidor.
    """
    try:
        log_file = "data/request_logs.json"
        if os.path.exists(log_file):
            with open(log_file, "r") as file:
                logs = [json.loads(line) for line in file.readlines()]
            return jsonify({"status": "success", "logs": logs}), 200
        else:
            return jsonify({"status": "success", "logs": []}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.errorhandler(404)
def not_found_error(error):
    """
    Tratamento para erros 404 (página não encontrada).
    """
    log_request("error", {"error": "404 Not Found"})
    return jsonify({"status": "error", "message": "Página não encontrada"}), 404

@app.errorhandler(500)
def internal_error(error):
    """
    Tratamento para erros 500 (erro interno do servidor).
    """
    log_request("error", {"error": "500 Internal Server Error"})
    return jsonify({"status": "error", "message": "Erro interno do servidor"}), 500

if __name__ == "__main__":
    # Garante que o diretório de dados exista antes de iniciar o servidor
    os.makedirs("data", exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=5000)