# compare-firebird-different-os

A small Python toolkit to compare the performance of two Firebird database servers running on **different operating systems** (e.g., Windows vs Linux).  
It focuses on measuring:

- Connection time
- Simple query execution time
- Repeated query benchmarks
- CSV export of raw timings
- Basic statistics per server (mean, min, max)

This is useful when you are:
- Migrating Firebird from Windows to Linux (or vice versa)
- Tuning Firebird configuration and OS settings
- Measuring network latency impact on Firebird access

> 📖 **Guia rápido?** Veja [QUICKSTART.md](QUICKSTART.md) para referência rápida  
> 🔧 **Problemas?** Veja [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## ⚡ Quick Start (TL;DR)

**Opção 1: Com Docker (mais fácil)**
```bash
# 1. Configure seus servidores Firebird
cp .env.docker .env
nano .env  # Edite com IPs e credenciais dos seus servidores

# 2. Execute com Docker
./run-benchmark.sh

# Pronto! Resultados em firebird_benchmark_results.csv
```

**Opção 2: Sem Docker (execução local)**
```bash
# 1. Instalar uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Instalar dependências
uv sync

# 3. Configurar servidores
cp .env.example .env
nano .env

# 4. Executar benchmark
uv run python -m compare_firebird_diferent_os.benchmark
```

📖 Problemas? Veja [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 🚀 Technologies

- **Python 3.10+**
- **uv** – fast Python environment & dependency manager
- **fdb** – Firebird driver for Python
- **python-dotenv** – environment variable loader
- **Docker** – containerização (opcional, mas recomendado)
- Firebird 2.5 / 3.0 / 4.0 (any version supported by `fdb`)

---

## 📦 Setup

### 1. Install `uv` (if you don’t have it yet)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Make sure `uv` is available in your shell (you may need to reload it).

### 2. Clone the repository

```bash
git clone https://github.com/andreagnoletto/compare-firebird-different-os.git
cd compare-firebird-different-os
```

### 3. Install dependencies

```bash
uv sync
```

This will create a virtual environment and install:

- `fdb`
- `python-dotenv`

---

## 🐳 Quick Start with Docker

Use Docker para executar os benchmarks sem instalar Python ou dependências localmente. O container irá se conectar aos seus servidores Firebird na rede.

### 1. Configure os servidores

Crie um arquivo `.env` na raiz do projeto:

```bash
cp .env.docker .env
```

Edite `.env` com os endereços dos seus servidores Firebird:

```dotenv
# Servidor 1 (ex: Windows)
WIN_FB_HOST=192.168.1.10
WIN_FB_PORT=3050
WIN_FB_DATABASE=C:/databases/mydb.fdb
WIN_FB_USER=sysdba
WIN_FB_PASSWORD=masterkey

# Servidor 2 (ex: Linux)
LIN_FB_HOST=192.168.1.20
LIN_FB_PORT=3050
LIN_FB_DATABASE=/var/lib/firebird/data/mydb.fdb
LIN_FB_USER=sysdba
LIN_FB_PASSWORD=masterkey

# Configurações do Benchmark
FB_BENCH_RUNS=20
FB_BENCH_QUERY=SELECT CURRENT_TIMESTAMP FROM RDB$DATABASE
```

### 2. Execute os benchmarks

**Opção A: Usando o script auxiliar (recomendado)**

```bash
./run-benchmark.sh
```

Este script irá:
- Verificar se o `.env` existe (e criar se necessário)
- Testar conectividade com os servidores
- Executar o benchmark automaticamente

**Opção B: Usando docker compose diretamente**

```bash
# Build e execução
docker compose up --build

# Executar novamente
docker compose up

# Executar de forma interativa
docker compose run --rm benchmark
```

### 3. Requisitos de rede

⚠️ **Importante**: 
- Os servidores Firebird devem estar acessíveis na rede
- Porta 3050 (padrão) precisa estar liberada no firewall
- O container usa `network_mode: host` para acessar a rede local
- Teste a conectividade antes: `ping <IP_DO_SERVIDOR>`

### 4. Resultados

Após a execução, você terá:
- **Console**: Estatísticas em tempo real de cada execução
- **CSV**: Arquivo `firebird_benchmark_results.csv` com todos os dados para análise

**Nota:** O container usa `network_mode: host` para acessar servidores na sua rede local. Se estiver no Windows/Mac, talvez precise ajustar para usar IPs acessíveis do Docker.

---

## 💻 Execução Local (sem Docker)

Se preferir executar diretamente sem Docker:

### 1. Pré-requisitos

- Python 3.12+
- uv instalado

### 2. Instalar dependências

```bash
# Instalar uv (se ainda não tiver)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sincronizar dependências
uv sync
```

### 3. Configurar servidores

```bash
# Copiar template de configuração
cp .env.example .env

# Editar com seus servidores
nano .env
```

Configure os servidores no `.env`:

```dotenv
# Servidor 1 (ex: Windows)
WIN_FB_HOST=192.168.1.10
WIN_FB_PORT=3050
WIN_FB_DATABASE=C:/databases/mydb.fdb
WIN_FB_USER=sysdba
WIN_FB_PASSWORD=masterkey

# Servidor 2 (ex: Linux)
LIN_FB_HOST=192.168.1.20
LIN_FB_PORT=3050
LIN_FB_DATABASE=/var/lib/firebird/data/mydb.fdb
LIN_FB_USER=sysdba
LIN_FB_PASSWORD=masterkey

# Configurações do Benchmark
FB_BENCH_RUNS=20
FB_BENCH_QUERY=SELECT CURRENT_TIMESTAMP FROM RDB$DATABASE
```

### 4. Executar benchmarks

```bash
# Teste rápido de conectividade
uv run python -m compare_firebird_diferent_os.main

# Benchmark completo com estatísticas
uv run python -m compare_firebird_diferent_os.benchmark
```

### 5. Analisar resultados (opcional)

```bash
# Instalar pandas para análise
uv pip install pandas

# Executar análise estatística
uv run python analyze_results.py
```

---

## ⚙️ Configuração Detalhada

### Variáveis de Ambiente (.env)

**Todas as variáveis disponíveis:**

```dotenv
# ============================================
# SERVIDOR 1 (ex: Firebird em Windows)
# ============================================
WIN_FB_HOST=192.168.1.10           # IP ou hostname do servidor
WIN_FB_PORT=3050                   # Porta do Firebird (padrão: 3050)
WIN_FB_DATABASE=C:/path/to/db.fdb  # Caminho completo ou alias
WIN_FB_USER=sysdba                 # Usuário do banco
WIN_FB_PASSWORD=masterkey          # Senha do usuário

# ============================================
# SERVIDOR 2 (ex: Firebird em Linux)
# ============================================
LIN_FB_HOST=192.168.1.20
LIN_FB_PORT=3050
LIN_FB_DATABASE=/var/lib/firebird/data/db.fdb
LIN_FB_USER=sysdba
LIN_FB_PASSWORD=masterkey

# ============================================
# CONFIGURAÇÕES DO BENCHMARK
# ============================================
FB_BENCH_RUNS=20                   # Número de execuções da query
FB_BENCH_QUERY=SELECT CURRENT_TIMESTAMP FROM RDB$DATABASE  # Query a executar
```

**Dicas de configuração:**

- **Windows**: Use caminhos com `/` ou `\\` (escape). Ex: `C:/databases/mydb.fdb` ou `C:\\databases\\mydb.fdb`
- **Linux**: Use caminhos absolutos. Ex: `/var/lib/firebird/data/mydb.fdb`
- **Aliases**: Configure em `aliases.conf` no servidor e use apenas o nome. Ex: `WIN_FB_DATABASE=mydb`
- **Queries personalizadas**: Use queries do seu sistema real para benchmarks mais significativos:
  ```dotenv
  FB_BENCH_QUERY=SELECT COUNT(*) FROM CLIENTES WHERE ATIVO = 1
  FB_BENCH_QUERY=SELECT * FROM VENDAS WHERE DATA > '2024-01-01' ORDER BY DATA DESC ROWS 100
  ```

> **⚠️ Segurança:** Nunca commite o arquivo `.env` no git! Apenas `.env.example` deve ser versionado.

---

## ▶️ Uso dos Scripts

### 1. Teste rápido de conectividade (`main.py`)

Verifica se consegue conectar aos servidores e executa uma query simples.

**Com Docker:**
```bash
docker compose run --rm benchmark uv run python -m compare_firebird_diferent_os.main
```

**Sem Docker:**
```bash
uv run python -m compare_firebird_diferent_os.main
```

**O que faz:**

- Abre conexão em cada servidor (Windows e Linux)
- Executa uma query de teste simples (`SELECT CURRENT_TIMESTAMP`)
- Exibe:
  - Tempo de conexão
  - Tempo de execução da query
  - Tempo total
  - Timestamp retornado de cada servidor

**Útil para:**
- Verificar conectividade antes do benchmark completo
- Debug rápido de problemas de conexão
- Validar credenciais

---

### 2. Benchmark completo (`benchmark.py`)

Executa múltiplas queries e gera estatísticas detalhadas + CSV.

**Com Docker:**
```bash
# Usando script auxiliar (recomendado)
./run-benchmark.sh

# Ou diretamente
docker compose up --build
```

**Sem Docker:**
```bash
uv run python -m compare_firebird_diferent_os.benchmark
```

**O que faz:**

1. Lê configurações `FB_BENCH_RUNS` e `FB_BENCH_QUERY` do `.env`
2. Para cada servidor (Windows e Linux):
   - Abre conexão
   - Executa a query N vezes (definido em `FB_BENCH_RUNS`)
   - Mede tempo de cada execução
3. Calcula estatísticas por servidor:
   - Média (mean)
   - Mínimo (min)
   - Máximo (max)
   - Desvio padrão (std)
4. Gera arquivo CSV com todas as medições:

**Formato do CSV:**

```text
firebird_benchmark_results.csv
```

Colunas:
```text
server;run_index;elapsed_seconds;query;runs
```

Exemplo:
```csv
server;run_index;elapsed_seconds;query;runs
Windows;1;0.045123;SELECT CURRENT_TIMESTAMP FROM RDB$DATABASE;20
Windows;2;0.043891;SELECT CURRENT_TIMESTAMP FROM RDB$DATABASE;20
Linux;1;0.038567;SELECT CURRENT_TIMESTAMP FROM RDB$DATABASE;20
Linux;2;0.039123;SELECT CURRENT_TIMESTAMP FROM RDB$DATABASE;20
...
```

Você pode abrir o CSV no Excel, LibreOffice, ou usar o script de análise.

---

### 3. Análise dos resultados (opcional - `analyze_results.py`)

Para análise estatística detalhada dos resultados:

**Com uv (recomendado):**
```bash
# Instalar pandas no ambiente uv
uv pip install pandas

# Executar análise
uv run python analyze_results.py
```

**Com pip:**
```bash
# Instalar pandas
pip install pandas

# Executar análise
python analyze_results.py
```

**O que o script faz:**
- Lê o arquivo `firebird_benchmark_results.csv`
- Calcula estatísticas detalhadas:
  - Média, mediana, mínimo, máximo
  - Desvio padrão e variância
  - Percentis
- Compara performance entre servidores
- Mostra diferença percentual
- Identifica qual servidor é mais rápido
- Sugere visualizações com matplotlib

**Exemplo de saída:**
```
📊 ANÁLISE DE RESULTADOS DO BENCHMARK FIREBIRD
================================================

🖥️  Windows
   Média:        0.045123 s
   Mediana:      0.044567 s
   Mínimo:       0.042891 s
   Máximo:       0.048234 s

🖥️  Linux
   Média:        0.038567 s
   Mediana:      0.038234 s
   Mínimo:       0.036891 s
   Máximo:       0.041123 s

⚖️  COMPARAÇÃO DIRETA
🏆 Servidor mais rápido: Linux
📊 Diferença percentual: 14.52%
```

---

## 🔧 Comandos Úteis

### Usando uv (execução local)

```bash
# Teste rápido
uv run python -m compare_firebird_diferent_os.main

# Benchmark completo
uv run python -m compare_firebird_diferent_os.benchmark

# Análise dos resultados
uv pip install pandas
uv run python analyze_results.py

# Atualizar dependências
uv sync --upgrade

# Adicionar nova dependência
uv add <package_name>
```

### Usando Docker

```bash
# Executar benchmark (com script auxiliar)
./run-benchmark.sh

# Executar benchmark (direto)
docker compose up --build

# Executar novamente sem rebuild
docker compose up

# Teste rápido de conectividade
docker compose run --rm benchmark uv run python -m compare_firebird_diferent_os.main

# Entrar no container para debug
docker compose run --rm benchmark sh

# Ver logs
docker compose logs benchmark

# Limpar tudo
docker compose down -v
```

---

## 📋 Workflows Típicos

### Workflow 1: Primeira execução (com Docker)

```bash
# 1. Clone o repositório
git clone https://github.com/andreagnoletto/compare-firebird-different-os.git
cd compare-firebird-different-os

# 2. Configure os servidores
cp .env.docker .env
nano .env  # ou vim, code, etc.

# 3. Execute o benchmark
./run-benchmark.sh

# 4. Analise os resultados
cat firebird_benchmark_results.csv
# ou abra no Excel/LibreOffice
```

### Workflow 2: Primeira execução (sem Docker)

```bash
# 1. Clone e configure
git clone https://github.com/andreagnoletto/compare-firebird-different-os.git
cd compare-firebird-different-os

# 2. Instale uv (se necessário)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Instale dependências
uv sync

# 4. Configure servidores
cp .env.example .env
nano .env

# 5. Teste conectividade
uv run python -m compare_firebird_diferent_os.main

# 6. Execute benchmark
uv run python -m compare_firebird_diferent_os.benchmark

# 7. Analise resultados
uv pip install pandas
uv run python analyze_results.py
```

### Workflow 3: Comparar antes/depois de mudanças

```bash
# 1. Execute benchmark antes da mudança
uv run python -m compare_firebird_diferent_os.benchmark
mv firebird_benchmark_results.csv results_before.csv

# 2. Faça mudanças no servidor (config, índices, etc.)

# 3. Execute benchmark depois
uv run python -m compare_firebird_diferent_os.benchmark
mv firebird_benchmark_results.csv results_after.csv

# 4. Compare resultados
# Abra ambos os CSVs no Excel ou use pandas para comparação
```

### Workflow 4: Benchmark com query customizada

```bash
# 1. Edite .env com sua query
nano .env

# Adicione/modifique:
# FB_BENCH_RUNS=50
# FB_BENCH_QUERY=SELECT COUNT(*) FROM CLIENTES WHERE ATIVO = 1

# 2. Execute benchmark
uv run python -m compare_firebird_diferent_os.benchmark

# 3. Experimente outras queries
# FB_BENCH_QUERY=SELECT * FROM VENDAS ORDER BY DATA DESC ROWS 1000
```

---

## 📂 Project structure

```text
compare-firebird-different-os/
├─ .env                              # Suas configurações (não commitar!)
├─ .env.example                      # Template de configuração
├─ .env.docker                       # Exemplo para Docker
├─ docker-compose.yml                # Orquestração do container cliente
├─ Dockerfile                        # Imagem Python com uv
├─ .dockerignore                     # Exclusões do build
├─ run-benchmark.sh                  # Script auxiliar (recomendado)
├─ analyze_results.py                # Script de análise estatística
├─ README.md                         # Documentação completa (você está aqui!)
├─ QUICKSTART.md                     # Guia de referência rápida ⚡
├─ TROUBLESHOOTING.md                # Guia de resolução de problemas
├─ pyproject.toml                    # Dependências Python
├─ firebird_benchmark_results.csv   # Resultados (gerado)
└─ src/
   ├─ README.md                      # Documentação técnica
   └─ compare_firebird_different_os/
      ├─ __init__.py
      ├─ main.py                     # Teste rápido de conectividade
      └─ benchmark.py                # Benchmark completo + estatísticas
```

**Principais arquivos:**

- **`QUICKSTART.md`** ⭐ - Guia de referência rápida para consulta
- **`run-benchmark.sh`** - Script que facilita a execução do Docker (verifica .env, testa conectividade)
- **`docker-compose.yml`** - Container cliente que conecta aos servidores externos
- **`.env`** - Configurações dos servidores Firebird (criar a partir do .env.example)
- **`main.py`** - Teste rápido de conectividade
- **`benchmark.py`** - Executa múltiplas queries e gera estatísticas + CSV
- **`analyze_results.py`** - Análise estatística detalhada dos resultados
- **`TROUBLESHOOTING.md`** - Soluções para problemas comuns

---

## 🔐 Segurança

- ⚠️ **Nunca** commite arquivos `.env` no repositório
- Use um usuário dedicado ao invés de `SYSDBA` em produção
- Certifique-se que apenas IPs confiáveis podem acessar a porta 3050 do Firebird
- Configure firewall adequadamente nos servidores
- Use senhas fortes e diferentes para cada ambiente

---

## 🧪 Dicas para Benchmarks Realistas

Para obter resultados significativos:

### Configuração de Rede
- Coloque os servidores Windows e Linux na **mesma rede física**, se possível
- Minimize latência de rede entre cliente e servidores
- Use conexões cabeadas ao invés de Wi-Fi para testes

### Queries Realistas
Use **queries do seu sistema real** em tabelas grandes:

```sql
-- Ao invés de:
SELECT CURRENT_TIMESTAMP FROM RDB$DATABASE

-- Use queries reais:
SELECT COUNT(*) FROM CLIENTES WHERE ATIVO = 1
SELECT * FROM VENDAS WHERE DATA > '2024-01-01' ORDER BY DATA DESC ROWS 1000
SELECT p.*, c.NOME FROM PEDIDOS p JOIN CLIENTES c ON p.CLIENTE_ID = c.ID
```

Configure no `.env`:
```dotenv
FB_BENCH_RUNS=50
FB_BENCH_QUERY=SELECT COUNT(*) FROM TABELA_GRANDE WHERE CONDICAO = 1
```

### Parâmetros do Firebird para Testar

Compare o impacto de diferentes configurações no `firebird.conf`:

```conf
DefaultDbCachePages = 2048      # vs 4096, 8192
TempCacheLimit = 67108864       # 64MB
TcpNoDelay = 1                  # Desabilita algoritmo de Nagle
CpuAffinity = 0,1,2,3           # Afinidade de CPU
```

### Tuning do Sistema Operacional

**Linux:**
```bash
# Swappiness
echo 10 > /proc/sys/vm/swappiness

# Dirty ratios
echo 10 > /proc/sys/vm/dirty_ratio
echo 5 > /proc/sys/vm/dirty_background_ratio

# I/O Scheduler
echo deadline > /sys/block/sda/queue/scheduler
```

**Windows:**
- Desabilitar indexação de busca no disco do banco
- Configurar antivírus para ignorar arquivos .fdb
- Ajustar power plan para "High Performance"

### Metodologia de Teste

1. **Baseline**: Execute benchmark antes de qualquer mudança
   ```bash
   uv run python -m compare_firebird_diferent_os.benchmark
   mv firebird_benchmark_results.csv baseline.csv
   ```

2. **Mudança**: Altere UMA configuração por vez

3. **Teste**: Execute benchmark novamente
   ```bash
   uv run python -m compare_firebird_diferent_os.benchmark
   mv firebird_benchmark_results.csv teste_mudanca1.csv
   ```

4. **Compare**: Analise diferenças
   ```bash
   # Compare CSVs no Excel ou use pandas
   ```

5. **Repita**: Teste outras configurações

---

## ❓ FAQ (Perguntas Frequentes)

### P: Preciso ter Docker instalado?
**R:** Não, você pode executar localmente com `uv`. Docker é opcional mas facilita a configuração.

### P: Funciona com Firebird 2.5?
**R:** Sim! O driver `fdb` suporta Firebird 2.5, 3.0 e 4.0.

### P: Posso comparar mais de 2 servidores?
**R:** Atualmente o código suporta 2 servidores (WIN e LIN). Para mais servidores, você precisaria modificar o código.

### P: Como faço para usar aliases ao invés de caminhos completos?
**R:** Configure o `aliases.conf` no servidor Firebird:
```conf
# /etc/firebird/aliases.conf (Linux)
# ou C:\Program Files\Firebird\aliases.conf (Windows)
mydb = /var/lib/firebird/data/production.fdb
```

Então no `.env`:
```dotenv
WIN_FB_DATABASE=mydb
```

### P: O benchmark está muito lento, o que fazer?
**R:** 
- Reduza `FB_BENCH_RUNS` no `.env` (ex: de 50 para 10)
- Use queries mais simples para testes iniciais
- Verifique latência de rede: `ping <IP_SERVIDOR>`

### P: Como exportar resultados para Excel?
**R:** O arquivo CSV já pode ser aberto diretamente no Excel. Se tiver problemas com separador:
1. Abra Excel
2. Dados → Texto para Colunas
3. Delimitado → Ponto e vírgula

### P: Posso rodar no Windows?
**R:** Sim! Tanto com Docker Desktop quanto com `uv` instalado no Windows.

### P: Os resultados variam muito entre execuções, é normal?
**R:** Alguma variação é normal devido a:
- Latência de rede variável
- Cache do Firebird
- Carga do sistema

Para resultados mais estáveis:
- Aumente `FB_BENCH_RUNS` (ex: 50 ou 100)
- Execute fora do horário de pico
- Use mediana ao invés de média para análise

### P: Como contribuir com o projeto?
**R:** 
1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Envie um Pull Request

Ideias de contribuição:
- Suporte para mais servidores
- Gráficos automáticos com matplotlib
- Testes de escrita (INSERT/UPDATE/DELETE)
- Benchmark de transações

---

## 🤝 Contribuindo

Contribuições são bem-vindas!

**Áreas para melhorias:**
- Adicionar mais modos de benchmark (conexão, transações, mixed read/write)
- Suporte para mais de dois servidores
- Geração automática de gráficos (matplotlib, plotly)
- Testes automatizados
- CI/CD com GitHub Actions
- Suporte para outros bancos (PostgreSQL, MySQL para comparação)

Sinta-se à vontade para abrir issues ou pull requests!

---

## 📄 Licença

Este projeto está sob a **Licença MIT**.  
Você pode usá-lo livremente para fins pessoais e comerciais.

---

## 🙏 Agradecimentos

- **fdb** - Firebird driver para Python
- **uv** - Gerenciador de pacotes Python ultrarrápido
- Comunidade Firebird

---

**Desenvolvido com ❤️ para facilitar comparações de performance Firebird**
