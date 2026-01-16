# Use Python 3.12 como base
FROM python:3.12-slim

# Instalar dependências do sistema para múltiplos drivers de banco de dados
# - gcc: compilação de extensões Python
# - curl: download do uv
# - libpq-dev: PostgreSQL client library
# - default-libmysqlclient-dev: MySQL/MariaDB client library
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    libpq-dev \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos do projeto
COPY pyproject.toml ./
COPY src/ ./src/
COPY main.py ./

# Sincronizar dependências com uv
RUN uv sync

# Comando padrão
CMD ["uv", "run", "python", "-m", "compare_firebird_diferent_os.benchmark"]
