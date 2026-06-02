# API de Vendas — Flask para K8s Lab
from flask import Flask, jsonify
import os
import socket

app = Flask(__name__)

# Versão da API (usado para demonstrar rolling updates)
VERSION = os.environ.get("APP_VERSION", "1.0")

@app.route("/")
def index():
    return jsonify({
        "app": "API de Vendas",
        "version": VERSION,
        "hostname": socket.gethostname(),  # Nome do Pod
        "message": f"Olá do Pod {socket.gethostname()}! 🚀"
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "version": VERSION})

@app.route("/vendas")
def vendas():
    # Dados de exemplo
    dados = [
        {"id": 1, "produto": "Notebook", "valor": 4500.00},
        {"id": 2, "produto": "Monitor 27\"", "valor": 1800.00},
        {"id": 3, "produto": "Teclado Mecânico", "valor": 350.00},
    ]
    return jsonify({"vendas": dados, "total": sum(v["valor"] for v in dados)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
