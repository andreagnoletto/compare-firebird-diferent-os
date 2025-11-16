# Source Code Documentation

Este diretório contém o código-fonte do projeto de benchmark Firebird.

## Estrutura

```
src/compare_firebird_diferent_os/
├── __init__.py          # Marca o pacote Python
├── main.py              # Teste rápido de conectividade
└── benchmark.py         # Benchmark completo com estatísticas
```

## Módulos

### `main.py` - Teste Rápido de Conectividade

Script simples para verificar se consegue conectar aos servidores Firebird e executar uma query básica.

**Uso:**
```bash
uv run python -m compare_firebird_diferent_os.main
```

**O que faz:**
1. Carrega configurações do `.env`
2. Conecta em cada servidor (Windows e Linux)
3. Executa `SELECT CURRENT_TIMESTAMP FROM RDB$DATABASE`
4. Mede tempo de conexão e execução
5. Exibe resultado no console

**Útil para:**
- Verificar conectividade antes de rodar benchmark completo
- Debug rápido de problemas de conexão
- Testar credenciais

---

### `benchmark.py` - Benchmark Completo

Script principal que executa múltiplas queries e gera estatísticas detalhadas.

**Uso:**
```bash
uv run python -m compare_firebird_diferent_os.benchmark
```

**O que faz:**
1. Carrega configurações do `.env` (incluindo `FB_BENCH_RUNS` e `FB_BENCH_QUERY`)
2. Para cada servidor:
   - Abre uma conexão
   - Executa a query N vezes (definido em `FB_BENCH_RUNS`)
   - Mede tempo de cada execução
   - Calcula estatísticas (média, mínimo, máximo, desvio padrão)
3. Gera arquivo CSV com todos os dados: `firebird_benchmark_results.csv`
4. Exibe comparação lado a lado no console

**Estrutura do CSV:**
```
server,run_index,elapsed_seconds,query,runs
Windows,1,0.045123,SELECT CURRENT_TIMESTAMP FROM RDB$DATABASE,20
Windows,2,0.043891,SELECT CURRENT_TIMESTAMP FROM RDB$DATABASE,20
...
```

**Útil para:**
- Comparar performance entre servidores
- Medir impacto de configurações do Firebird
- Identificar variações de latência
- Gerar dados para análise em Excel/Python

---

## Configuração

Ambos os scripts usam variáveis de ambiente do arquivo `.env`:

```dotenv
# Servidor 1
WIN_FB_HOST=192.168.1.10
WIN_FB_PORT=3050
WIN_FB_DATABASE=C:/databases/mydb.fdb
WIN_FB_USER=sysdba
WIN_FB_PASSWORD=masterkey

# Servidor 2
LIN_FB_HOST=192.168.1.20
LIN_FB_PORT=3050
LIN_FB_DATABASE=/var/lib/firebird/data/mydb.fdb
LIN_FB_USER=sysdba
LIN_FB_PASSWORD=masterkey

# Benchmark (apenas benchmark.py)
FB_BENCH_RUNS=20
FB_BENCH_QUERY=SELECT CURRENT_TIMESTAMP FROM RDB$DATABASE
```

---

## Dependências

- **fdb**: Driver Firebird para Python
  - Suporta Firebird 2.5, 3.0, 4.0
  - Conexão via protocolo TCP/IP
  - Charset UTF-8 por padrão

- **python-dotenv**: Carregamento de variáveis de ambiente
  - Lê arquivo `.env`
  - Mantém credenciais fora do código

---

## Executando Localmente (sem Docker)

### 1. Instalar uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Instalar dependências

```bash
uv sync
```

### 3. Configurar .env

```bash
cp .env.example .env
nano .env
```

### 4. Executar

```bash
# Teste rápido
uv run python -m compare_firebird_diferent_os.main

# Benchmark completo
uv run python -m compare_firebird_diferent_os.benchmark
```

---

## Modificando o Código

### Alterar Query do Benchmark

Edite `.env`:
```dotenv
FB_BENCH_QUERY=SELECT COUNT(*) FROM CLIENTES WHERE ATIVO = 1
```

Ou edite diretamente `benchmark.py`:
```python
query = os.getenv("FB_BENCH_QUERY", "SELECT CURRENT_TIMESTAMP FROM RDB$DATABASE")
```

### Adicionar Mais Servidores

Atualmente suporta 2 servidores. Para adicionar mais:

1. Adicione variáveis no `.env`:
```dotenv
SRV3_FB_HOST=192.168.1.30
SRV3_FB_PORT=3050
SRV3_FB_DATABASE=...
```

2. Modifique `benchmark.py` para ler essas configurações
3. Adicione no loop de execução

---

## Análise de Resultados

### Com Python/Pandas

```python
import pandas as pd

# Ler CSV
df = pd.read_csv('firebird_benchmark_results.csv', sep=';')

# Estatísticas por servidor
print(df.groupby('server')['elapsed_seconds'].describe())

# Visualizar
import matplotlib.pyplot as plt
df.boxplot(by='server', column='elapsed_seconds')
plt.show()
```

### Com Excel

1. Abra `firebird_benchmark_results.csv`
2. Dados → Texto para Colunas → Delimitado → Ponto e vírgula
3. Crie tabela dinâmica para análise
4. Gráficos de comparação

---

## Troubleshooting

Veja [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) na raiz do projeto.

### Erro comum: "Cannot attach to password database"

- Verifique usuário e senha no `.env`
- Teste com `isql` ou FlameRobin primeiro
- Certifique-se que o servidor aceita conexões remotas

### Erro: "network connection error"

- Verifique conectividade: `ping <IP_SERVIDOR>`
- Teste porta: `telnet <IP_SERVIDOR> 3050`
- Verifique firewall

### CSV não gerado

- Verifique permissões de escrita no diretório
- Execute com `sudo` se necessário (não recomendado)
- Veja logs de erro no console
