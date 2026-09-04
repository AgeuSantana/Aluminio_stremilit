# Imagem base oficial do Python (versão slim para otimizar tamanho e segurança)
FROM python:3.11-slim

# Evita que o Python gere arquivos .pyc e força flush imediato de stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Define diretório de trabalho dentro do container
WORKDIR /app

# Instala dependências do sistema necessárias para compilação se exigido por wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala primeiro os requirements para aproveitar o cache de camadas do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia os arquivos da aplicação
COPY src/ ./src/
COPY app.py .

# Expõe a porta padrão do Streamlit
EXPOSE 8501

# Healthcheck para validar disponibilidade do serviço
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Ponto de entrada da aplicação sem abrir navegador e ouvindo em todas as interfaces
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]