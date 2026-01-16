# 🎯 Guia Multi-Database Benchmark

## 📋 Índice

- [Introdução](#introdução)
- [Arquitetura](#arquitetura)
- [Configuração](#configuração)
- [Mapeamento de Métricas](#mapeamento-de-métricas)
- [Interpretação de Resultados](#interpretação-de-resultados)
- [Exemplos de Uso](#exemplos-de-uso)
- [Limitações e Considerações](#limitações-e-considerações)

---

## 🎨 Introdução

Este sistema permite **comparar a performance** de diferentes SGBDs (Sistemas Gerenciadores de Banco de Dados) rodando em diferentes sistemas operacionais usando **metodologia científica rigorosa**.

### Bancos Suportados

- **Firebird** 2.5, 3.0, 4.0
- **MySQL** 5.7, 8.0+
- **PostgreSQL** 12, 13, 14, 15, 16
- **MariaDB** 10.x, 11.x

### Sistemas Operacionais

- **Windows** (Server 2019/2022, Windows 10/11)
- **Linux** (Ubuntu, Debian, CentOS, etc.)

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    Benchmark Client                          │
│                   (Python 3.12+)                             │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         DatabaseConnectionFactory                     │  │
│  │  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐             │  │
│  │  │  FB  │  │ MySQL│  │  PG  │  │Maria │             │  │
│  │  └──────┘  └──────┘  └──────┘  └──────┘             │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       StatisticsCollectorFactory                      │  │
│  │  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐             │  │
│  │  │ MON$ │  │EXPLAIN│  │EXPLAIN│  │EXPLAIN│            │  │
│  │  │Tables│  │+STATUS│  │ANALYZE│  │+STATUS│            │  │
│  │  └──────┘  └──────┘  └──────┘  └──────┘             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Firebird   │  │    MySQL     │  │  PostgreSQL  │
│   Windows    │  │    Linux     │  │    Linux     │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Componentes Principais

1. **DatabaseConfig**: Configuração com `db_type`, `os_type`, credenciais
2. **DatabaseConnection**: Abstração de conexão (ABC)
3. **StatisticsCollector**: Coleta de métricas específicas por DB (ABC)
4. **Factories**: Criação de instâncias apropriadas por tipo de banco

---

## ⚙️ Configuração

### Formato Novo (Multi-Database)

```dotenv
# Servidor 1 - Firebird Windows
SERVER1_TYPE=firebird
SERVER1_OS=windows
SERVER1_NAME=Firebird Win
SERVER1_HOST=192.168.10.31
SERVER1_PORT=3051
SERVER1_DATABASE=C:\Dados\clinica.fdb
SERVER1_USER=sysdba
SERVER1_PASSWORD=masterkey

# Servidor 2 - MySQL Linux
SERVER2_TYPE=mysql
SERVER2_OS=linux
SERVER2_NAME=MySQL Linux
SERVER2_HOST=192.168.10.32
SERVER2_PORT=3306
SERVER2_DATABASE=clinica
SERVER2_USER=root
SERVER2_PASSWORD=senha123

# Servidor 3 - PostgreSQL Linux
SERVER3_TYPE=postgresql
SERVER3_OS=linux
SERVER3_NAME=PostgreSQL Linux
SERVER3_HOST=192.168.10.33
SERVER3_PORT=5432
SERVER3_DATABASE=clinica
SERVER3_USER=postgres
SERVER3_PASSWORD=senha456
```

### Parâmetros Opcionais

```dotenv
SERVER1_CHARSET=UTF8              # Charset (padrão: UTF8)
SERVER1_QUERY=SELECT COUNT(*)...  # Query específica (sobrescreve global)
```

### Parâmetros Globais

```dotenv
FB_BENCH_RUNS=100                 # Número de execuções
FB_BENCH_QUERY=SELECT 1           # Query padrão
```

---

## 📊 Mapeamento de Métricas

### Métricas Universais

Estas métricas são **comparáveis entre todos** os bancos:

| Métrica | Descrição | Fonte |
|---------|-----------|-------|
| `elapsed_total` | Tempo total (cliente) | `time.perf_counter()` |
| `elapsed_server` | Tempo servidor* | Medido no lado do Python |
| `latency` | Latência de rede | `elapsed_total - elapsed_server` |
| `rowcount` | Linhas retornadas | `cursor.rowcount` |
| `plan` | Plano de execução | DB-specific |

*Aproximação: pode incluir overhead de driver

### Métricas de I/O (Mapeadas)

Estas métricas são **aproximadamente equivalentes**:

#### Sequential Reads (`seq_reads`)

| Banco | Métrica Original | Descrição |
|-------|------------------|-----------|
| **Firebird** | `MON$RECORD_SEQ_READS` | Leituras sequenciais de registros |
| **MySQL** | `Handler_read_rnd_next` | Leituras sequenciais na tabela |
| **PostgreSQL** | `tup_returned` | Tuplas retornadas (aproximação) |
| **MariaDB** | `Handler_read_rnd_next` | Idêntico ao MySQL |

#### Index Reads (`idx_reads`)

| Banco | Métrica Original | Descrição |
|-------|------------------|-----------|
| **Firebird** | `MON$RECORD_IDX_READS` | Leituras via índice |
| **MySQL** | `Handler_read_key` + `Handler_read_next` | Operações de índice |
| **PostgreSQL** | `tup_fetched` | Tuplas buscadas via índice |
| **MariaDB** | `Handler_read_key` + `Handler_read_next` | Idêntico ao MySQL |

#### Inserts/Updates/Deletes

| Banco | Métrica Original | Descrição |
|-------|------------------|-----------|
| **Firebird** | `MON$RECORD_INSERTS/UPDATES/DELETES` | Operações DML |
| **MySQL** | `Handler_write/update/delete` | Operações de modificação |
| **PostgreSQL** | `tup_inserted/updated/deleted` | Tuplas modificadas |
| **MariaDB** | `Handler_write/update/delete` | Idêntico ao MySQL |

### Métricas Específicas

Estas métricas são **exclusivas** de cada banco:

#### Firebird Only

- `backouts`: Versões de registro descartadas
- `purges`: Registros removidos do garbage collection
- `expunges`: Registros permanentemente removidos

#### PostgreSQL Only

- `blks_read`: Blocos lidos do disco
- `blks_hit`: Blocos encontrados no cache
- Cache hit ratio: `blks_hit / (blks_read + blks_hit)`

#### MySQL/MariaDB Only

- Query cache statistics (se habilitado)
- Handler counters específicos

---

## 📈 Interpretação de Resultados

### CSV Output

```csv
db_type;os_type;server_name;run_index;elapsed_total_seconds;elapsed_server_seconds;latency_seconds;seq_reads;idx_reads;...
firebird;windows;Firebird Win;1;0.045123;0.042891;0.002232;0;5;0;0;0;PLAN...
mysql;linux;MySQL Linux;1;0.032456;0.030123;0.002333;12;3;0;0;0;id SELECT_TYPE...
postgresql;linux;PostgreSQL Linux;1;0.028789;0.026456;0.002333;1;0;0;0;0;Seq Scan...
```

### Comparações Válidas

#### ✅ Comparações Recomendadas

1. **Mesmo DB, OS diferentes**
   - Firebird Windows vs Firebird Linux
   - Avalia impacto do sistema operacional
   - Métricas totalmente comparáveis

2. **DBs diferentes, mesmo OS**
   - MySQL vs PostgreSQL (ambos Linux)
   - Avalia performance relativa entre engines
   - Considerar diferenças de implementação

3. **Query portável em todos DBs**
   - `SELECT 1` ou `SELECT COUNT(*)`
   - Mesma tabela/dados em todos bancos
   - Estrutura de índices equivalente

#### ⚠️ Comparações com Ressalvas

1. **DBs diferentes, queries diferentes**
   - Dialeto SQL pode variar
   - Otimizações específicas
   - Resultados podem não ser comparáveis

2. **Métricas específicas cross-database**
   - `backouts` Firebird vs `blks_hit` PostgreSQL
   - Conceitos fundamentalmente diferentes
   - Comparação não faz sentido

### Análise Estatística

O sistema aplica **metodologia científica rigorosa**:

```
1. Teste de Normalidade
   └─> Shapiro-Wilk (1965)
       └─> p > 0.05: distribuição normal

2. Teste de Significância
   ├─> Ambos normais: t-test (Student, 1908)
   └─> Não normal: Mann-Whitney U (1947)
       └─> p < 0.05: diferença significativa

3. Tamanho do Efeito
   └─> Cohen's d (1988)
       ├─> |d| < 0.2: insignificante
       ├─> 0.2 ≤ |d| < 0.5: pequeno
       ├─> 0.5 ≤ |d| < 0.8: médio
       └─> |d| ≥ 0.8: grande

4. Intervalo de Confiança
   └─> 95% CI usando t de Student

5. Detecção de Outliers
   └─> Método IQR (Tukey, 1977)
```

---

## 💡 Exemplos de Uso

### Exemplo 1: Comparar Firebird em Windows vs Linux

```dotenv
SERVER1_TYPE=firebird
SERVER1_OS=windows
SERVER1_HOST=192.168.1.10
SERVER1_DATABASE=C:\DB\clinica.fdb

SERVER2_TYPE=firebird
SERVER2_OS=linux
SERVER2_HOST=192.168.1.20
SERVER2_DATABASE=/var/db/clinica.fdb

FB_BENCH_QUERY=SELECT COUNT(*) FROM pacientes
FB_BENCH_RUNS=100
```

**Interpretação**:
- Mesma engine, mesma query, mesmos dados
- Diferença = impacto do sistema operacional
- Métricas de I/O diretamente comparáveis

### Exemplo 2: Comparar MySQL vs PostgreSQL no Linux

```dotenv
SERVER1_TYPE=mysql
SERVER1_OS=linux
SERVER1_HOST=192.168.1.30
SERVER1_DATABASE=clinica

SERVER2_TYPE=postgresql
SERVER2_OS=linux
SERVER2_HOST=192.168.1.40
SERVER2_DATABASE=clinica

FB_BENCH_QUERY=SELECT COUNT(*) FROM pacientes WHERE ativo = 1
FB_BENCH_RUNS=100
```

**Interpretação**:
- Engines diferentes, mesmo OS
- Diferença = implementação do engine + otimizações
- `seq_reads` e `idx_reads` são aproximações
- Planos de execução podem ser muito diferentes

### Exemplo 3: Benchmark Completo (4 Bancos, 2 OS)

```dotenv
# Firebird Windows + Linux
SERVER1_TYPE=firebird
SERVER1_OS=windows
SERVER2_TYPE=firebird
SERVER2_OS=linux

# MySQL Windows + Linux
SERVER3_TYPE=mysql
SERVER3_OS=windows
SERVER4_TYPE=mysql
SERVER4_OS=linux

# PostgreSQL Windows + Linux
SERVER5_TYPE=postgresql
SERVER5_OS=windows
SERVER6_TYPE=postgresql
SERVER6_OS=linux

# MariaDB Windows + Linux
SERVER7_TYPE=mariadb
SERVER7_OS=windows
SERVER8_TYPE=mariadb
SERVER8_OS=linux

FB_BENCH_QUERY=SELECT COUNT(*) FROM agenda
FB_BENCH_RUNS=200
```

**Análises Possíveis**:
1. Impacto do OS por banco (FB Win vs FB Linux)
2. Comparação entre bancos no mesmo OS
3. Ranking geral de performance
4. Consistência de resultados (outliers)

---

## ⚠️ Limitações e Considerações

### Queries Portáveis

**✅ Recomendado**:
```sql
SELECT 1
SELECT COUNT(*) FROM tabela
SELECT * FROM tabela LIMIT 100
SELECT col FROM information_schema.tables
```

**❌ Evitar**:
```sql
-- Firebird específico
SELECT CURRENT_TIMESTAMP FROM RDB$DATABASE

-- MySQL/MariaDB específico
SELECT CONNECTION_ID()

-- PostgreSQL específico
SELECT pg_backend_pid()
```

### Diferenças de Implementação

1. **Planos de Execução**
   - Formato varia drasticamente
   - Não comparar textos literalmente
   - Focar em tipos de operação (seq scan, index scan)

2. **Transações**
   - Firebird: MVCC sempre ativo
   - MySQL InnoDB: MVCC
   - PostgreSQL: MVCC
   - MariaDB: depende do engine

3. **Cache**
   - Cada banco tem estratégias diferentes
   - Executar warm-up antes do benchmark
   - Considerar tamanho do buffer pool

### Boas Práticas

1. **Dados Equivalentes**
   - Mesmos dados em todos os bancos
   - Índices equivalentes
   - Estatísticas atualizadas

2. **Isolamento**
   - Bancos em servidores dedicados
   - Sem outras aplicações rodando
   - Mesma configuração de hardware

3. **Repetições**
   - Mínimo 20 execuções (melhor 100+)
   - Verificar outliers
   - Considerar warmup

4. **Documentação**
   - Registrar versões dos bancos
   - Configurações (buffer pool, etc.)
   - Hardware (CPU, RAM, disco)

---

## 🔬 Metodologia Científica

### Processo de Benchmark

```
1. Preparação
   ├─> Configurar .env
   ├─> Validar conectividade (test_connections.py)
   └─> Verificar dados equivalentes

2. Execução
   ├─> Warm-up (primeiras execuções descartadas)
   ├─> N execuções (100+)
   └─> Captura de métricas

3. Análise
   ├─> Estatísticas descritivas
   ├─> Testes de normalidade
   ├─> Testes de significância
   ├─> Tamanho do efeito
   └─> Detecção de outliers

4. Interpretação
   ├─> Considerar contexto (hardware, dados, etc.)
   ├─> Avaliar significância prática vs estatística
   └─> Documentar conclusões
```

### Significância Estatística vs Prática

- **p < 0.05**: diferença estatisticamente significativa
- **Cohen's d > 0.8**: diferença com grande efeito prático
- Ambos são necessários para conclusões sólidas

**Exemplo**:
```
MySQL vs PostgreSQL:
- Média MySQL: 0.0450s
- Média PostgreSQL: 0.0455s
- Diferença: 0.0005s (1.1%)
- p-valor: 0.001 (significativo)
- Cohen's d: 0.15 (efeito insignificante)

Interpretação: A diferença é estatisticamente detectável,
mas praticamente irrelevante (< 1ms, efeito pequeno).
```

---

## 📚 Referências

- Shapiro, S. S., & Wilk, M. B. (1965). An analysis of variance test for normality
- Student (1908). The probable error of a mean
- Mann, H. B., & Whitney, D. R. (1947). On a test of whether one of two random variables is stochastically larger than the other
- Cohen, J. (1988). Statistical power analysis for the behavioral sciences
- Tukey, J. W. (1977). Exploratory Data Analysis

---

## 🤝 Contribuindo

Para adicionar suporte a novos bancos de dados:

1. Criar `database/{novo_db}.py` implementando `DatabaseConnection`
2. Criar `collectors/{novo_db}.py` implementando `StatisticsCollector`
3. Mapear métricas para padrão universal
4. Atualizar documentação
5. Adicionar testes

---

**Versão**: 2.0.0 (Multi-Database Support)  
**Data**: Novembro 2025
