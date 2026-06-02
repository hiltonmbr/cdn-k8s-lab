# Imagem base leve com Python
FROM python:3.12-slim

# Diretório de trabalho
WORKDIR /app

# Instalar dependências primeiro (cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY app.py .

# Porta exposta pelo contêiner
EXPOSE 8000

# Comando de inicialização
CMD ["python", "app.py"]
