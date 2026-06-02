# API Fullstack — Flask + PostgreSQL (externo)
from flask import Flask, jsonify, request
import psycopg2
import psycopg2.extras
import os
import socket
import time

app = Flask(__name__)

# Configuração via variáveis de ambiente (injetadas por ConfigMap/Secret)
DB_HOST = os.environ.get("DB_HOST", "postgres")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "escola")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "senha123")


def get_db_connection():
    """Conecta ao PostgreSQL com retry."""
    for attempt in range(5):
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
            )
            return conn
        except psycopg2.OperationalError:
            if attempt < 4:
                time.sleep(2)
            else:
                raise


def init_db():
    """Cria a tabela de alunos se não existir."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS alunos (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(100),
            nota DECIMAL(4,2)
        )
    """)
    # Inserir dados de exemplo se a tabela estiver vazia
    cur.execute("SELECT COUNT(*) FROM alunos")
    if cur.fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO alunos (nome, email, nota) VALUES
                ('Maria Silva', 'maria@email.com', 9.5),
                ('João Santos', 'joao@email.com', 8.7),
                ('Ana Oliveira', 'ana@email.com', 10.0),
                ('Pedro Costa', 'pedro@email.com', 7.8),
                ('Lucia Ferreira', 'lucia@email.com', 9.2)
        """)
    conn.commit()
    cur.close()
    conn.close()


@app.route("/")
def index():
    return jsonify({
        "app": "API Escola — K8s Lab",
        "version": "1.0",
        "pod": socket.gethostname(),
        "database": f"{DB_HOST}:{DB_PORT}/{DB_NAME}",
        "endpoints": ["/alunos", "/alunos/<id>", "/health"],
    })


@app.route("/health")
def health():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return jsonify({"status": "healthy", "database": "connected"})
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 503


@app.route("/alunos", methods=["GET"])
def listar_alunos():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM alunos ORDER BY id")
    alunos = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({"alunos": alunos, "total": len(alunos)})


@app.route("/alunos/<int:aluno_id>", methods=["GET"])
def buscar_aluno(aluno_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM alunos WHERE id = %s", (aluno_id,))
    aluno = cur.fetchone()
    cur.close()
    conn.close()
    if aluno:
        return jsonify(aluno)
    return jsonify({"error": "Aluno não encontrado"}), 404


@app.route("/alunos", methods=["POST"])
def criar_aluno():
    dados = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "INSERT INTO alunos (nome, email, nota) VALUES (%s, %s, %s) RETURNING *",
        (dados["nome"], dados.get("email"), dados.get("nota")),
    )
    aluno = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(aluno), 201


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
