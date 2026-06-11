# Sales API — Flask for K8s Lab
from flask import Flask, jsonify
import os
import socket

app = Flask(__name__)

# API version (used to demonstrate rolling updates)
VERSION = os.environ.get("APP_VERSION", "1.0")


@app.route("/")
def index():
    return jsonify({
        "app": "Sales API",
        "version": VERSION,
        "hostname": socket.gethostname(),  # Pod name
        "message": f"Hello from Pod {socket.gethostname()}! 🚀"
    })


@app.route("/health")
def health():
    return jsonify({"status": "healthy", "version": VERSION})


@app.route("/sales")
def vendas():
    # Sample data
    dados = [
        {"id": 1, "product": "Laptop", "price": 4500.00},
        {"id": 2, "product": "27\" Monitor", "price": 1800.00},
        {"id": 3, "product": "Mechanical Keyboard", "price": 350.00},
    ]
    return jsonify({"sales": dados, "total": sum(v["price"] for v in dados)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
