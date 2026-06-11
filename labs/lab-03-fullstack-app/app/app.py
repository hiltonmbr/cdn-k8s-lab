# Fullstack API — Flask + PostgreSQL (external)
from flask import Flask, jsonify, request
import psycopg2
import psycopg2.extras
import os
import socket
import time

app = Flask(__name__)

# Configuration via environment variables (injected by ConfigMap/Secret)
DB_HOST = os.environ.get("DB_HOST", "postgres")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "school")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "password123")


def get_db_connection():
    """Connect to PostgreSQL with retry."""
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
    """Create the students table if it doesn't exist."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100),
            grade DECIMAL(4,2)
        )
    """)
    # Insert sample data if the table is empty
    cur.execute("SELECT COUNT(*) FROM students")
    if cur.fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO students (name, email, grade) VALUES
                ('Mary Silva', 'maria@email.com', 9.5),
                ('John Santos', 'joao@email.com', 8.7),
                ('Anne Oliveira', 'ana@email.com', 10.0),
                ('Peter Costa', 'pedro@email.com', 7.8),
                ('Lucy Ferreira', 'lucia@email.com', 9.2)
        """)
    conn.commit()
    cur.close()
    conn.close()


@app.route("/")
def index():
    return jsonify({
        "app": "School API — K8s Lab",
        "version": "1.0",
        "pod": socket.gethostname(),
        "database": f"{DB_HOST}:{DB_PORT}/{DB_NAME}",
        "endpoints": ["/students", "/students/<id>", "/health"],
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


@app.route("/students", methods=["GET"])
def listar_alunos():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM students ORDER BY id")
    alunos = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({"students": alunos, "total": len(alunos)})


@app.route("/students/<int:aluno_id>", methods=["GET"])
def buscar_aluno(aluno_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM students WHERE id = %s", (aluno_id,))
    aluno = cur.fetchone()
    cur.close()
    conn.close()
    if aluno:
        return jsonify(aluno)
    return jsonify({"error": "Student not found"}), 404


@app.route("/students", methods=["POST"])
def criar_aluno():
    dados = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "INSERT INTO students (name, email, grade) VALUES (%s, %s, %s) RETURNING *",
        (dados["name"], dados.get("email"), dados.get("grade")),
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
