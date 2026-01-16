# Firebird Benchmark Toolkit

Ferramenta Python para **benchmark e comparação de performance** de servidores Firebird, com análise estatística rigorosa por IP/servidor.

## 🚀 Funcionalidades

- ✅ **Benchmark concorrente** - ThreadPoolExecutor com 10 threads
- ✅ **Múltiplos servidores** - Compare até 10 servidores simultaneamente
- ✅ **Análise por IP** - Identifique qual configuração é mais rápida
- ✅ **Metodologia científica** - Testes estatísticos (Shapiro-Wilk, Mann-Whitney U, Cohen's d)
- ✅ **Detecção de outliers** - Método IQR (Tukey, 1977)

---

## ⚡ Quick Start

### 1. Instalar dependências

```bash
# Windows PowerShell
irm https://astral.sh/uv/install.ps1 | iex

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Instalar dependências do projeto
uv sync
```

### 2. Configurar servidores (.env)

```bash
cp .env.example .env
```

Exemplo de `.env`:

```dotenv
# ===== SERVIDOR 1 =====
SERVER1_TYPE=firebird
SERVER1_OS=linux
SERVER1_HOST=192.168.10.32
SERVER1_PORT=3050
SERVER1_DATABASE=/path/to/database.fdb
SERVER1_USER=SYSDBA
SERVER1_PASSWORD=masterkey
SERVER1_CHARSET=UTF8

# ===== SERVIDOR 2 =====
SERVER2_TYPE=firebird
SERVER2_OS=linux
SERVER2_HOST=192.168.10.93
SERVER2_PORT=3050
SERVER2_DATABASE=/path/to/database.fdb
SERVER2_USER=SYSDBA
SERVER2_PASSWORD=masterkey
SERVER2_CHARSET=UTF8

# ===== SERVIDOR 3 =====
SERVER3_TYPE=firebird
SERVER3_OS=linux
SERVER3_HOST=192.168.10.94
SERVER3_PORT=3050
SERVER3_DATABASE=/path/to/database.fdb
SERVER3_USER=SYSDBA
SERVER3_PASSWORD=masterkey
SERVER3_CHARSET=UTF8

# ===== PARÂMETROS DO BENCHMARK =====
FB_BENCH_RUNS=10000
FB_BENCH_CONCURRENT=10
FB_BENCH_QUERY=SELECT CURRENT_TIMESTAMP FROM RDB$DATABASE
```

### 3. Testar conexões

```bash
uv run python test_connections.py
```

Saída esperada:
```
🔌 TESTE DE CONEXÕES - Multi-Database Benchmark
✅ 3 servidor(es) encontrado(s)

[1/3] Testando: Firebird 192.168.10.32
    Status: ✅ CONECTADO
    Versão: LI-V3.0.11.33703 Firebird 3.0
```

### 4. Executar benchmark

```bash
uv run python -m src.compare_firebird_diferent_os.main_new
```

Parâmetros:
- **10.000 queries** por servidor (configurável via `FB_BENCH_RUNS`)
- **10 threads** concorrentes (configurável via `FB_BENCH_CONCURRENT`)
- Resultados salvos em `benchmark_results.csv`

### 5. Analisar resultados

```bash
uv run python analyze_results_by_ip.py benchmark_results.csv
```

Exemplo de saída:
```
================================================================================
🏆 RANKING DE PERFORMANCE (por tempo médio)
================================================================================

   🥇 Firebird 192.168.10.94: 4.43 ms
   🥈 Firebird 192.168.10.93: 5.37 ms (+21.4% vs melhor)
   🥉 Firebird 192.168.10.32: 8.75 ms (+97.7% vs melhor)

================================================================================
🎯 RECOMENDAÇÃO FINAL
================================================================================

   ✅ RECOMENDADO: Firebird 192.168.10.94

   Performance 97.7% superior ao servidor mais lento,
   com diferença estatisticamente significativa e efeito grande.
```

---

## 📁 Estrutura do Projeto

```
├── .env                          # Configuração dos servidores
├── benchmark_results.csv         # Resultados do benchmark
├── analyze_results_by_ip.py      # Análise estatística por IP
├── test_connections.py           # Testar conexões
└── src/compare_firebird_diferent_os/
    ├── main_new.py               # Entry point do benchmark
    ├── benchmark_new.py          # Lógica do benchmark concorrente
    └── config.py                 # Carregamento de configurações
```

---

## 🔬 Metodologia Científica

| Teste | Descrição | Referência |
|-------|-----------|------------|
| **Shapiro-Wilk** | Teste de normalidade | Shapiro & Wilk (1965) |
| **Mann-Whitney U** | Comparação não-paramétrica | Mann & Whitney (1947) |
| **Cohen's d** | Tamanho do efeito | Cohen (1988) |
| **IQR** | Detecção de outliers | Tukey (1977) |
| **IC 95%** | Intervalo de confiança | Student (1908) |

### Interpretação de Cohen's d

| Valor | Interpretação |
|-------|---------------|
| < 0.2 | Insignificante |
| 0.2 - 0.5 | Pequeno |
| 0.5 - 0.8 | Médio |
| > 0.8 | **Grande** |

---

## 🛠️ Comandos Úteis

```bash
# Testar conexões
uv run python test_connections.py

# Executar benchmark
uv run python -m src.compare_firebird_diferent_os.main_new

# Analisar resultados
uv run python analyze_results_by_ip.py benchmark_results.csv

# Atualizar dependências
uv sync --upgrade
```

---

## 📚 Referências

- Shapiro, S.S. & Wilk, M.B. (1965). *An analysis of variance test for normality*
- Mann, H.B. & Whitney, D.R. (1947). *On a test of whether one of two random variables is stochastically larger*
- Cohen, J. (1988). *Statistical power analysis for the behavioral sciences*
- Tukey, J.W. (1977). *Exploratory Data Analysis*

---

## 📄 Licença

MIT License
