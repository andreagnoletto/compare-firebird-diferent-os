# Guia de Uso Rápido

## 🎯 Objetivo
Comparar performance entre dois servidores Firebird (ex: Windows vs Linux) executando benchmarks de queries.

---

## 🚀 Início Rápido

### Método 1: Docker (Recomendado)
```bash
cp .env.docker .env && nano .env && ./run-benchmark.sh
```

### Método 2: Local (uv)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
cp .env.example .env && nano .env
uv run python -m compare_firebird_diferent_os.benchmark
```

---

## 📁 Arquivos Principais

| Arquivo | Descrição | Quando Usar |
|---------|-----------|-------------|
| `run-benchmark.sh` | Script auxiliar Docker | Primeira escolha para Docker |
| `docker-compose.yml` | Configuração Docker | Execução containerizada |
| `.env` | Configurações (criar!) | **SEMPRE antes de executar** |
| `src/.../main.py` | Teste de conectividade | Verificar se conecta aos servidores |
| `src/.../benchmark.py` | Benchmark completo | Gerar estatísticas e CSV |
| `analyze_results.py` | Análise estatística | Análise detalhada após benchmark |
| `TROUBLESHOOTING.md` | Solução de problemas | Quando algo não funciona |

---

## ⚙️ Configuração Mínima (.env)

```dotenv
# Servidor 1
WIN_FB_HOST=192.168.1.10
WIN_FB_DATABASE=C:/databases/mydb.fdb
WIN_FB_USER=sysdba
WIN_FB_PASSWORD=masterkey

# Servidor 2
LIN_FB_HOST=192.168.1.20
LIN_FB_DATABASE=/var/lib/firebird/data/mydb.fdb
LIN_FB_USER=sysdba
LIN_FB_PASSWORD=masterkey

# Benchmark
FB_BENCH_RUNS=20
FB_BENCH_QUERY=SELECT CURRENT_TIMESTAMP FROM RDB$DATABASE
```

---

## 🔧 Comandos Essenciais

### Docker
```bash
./run-benchmark.sh                    # Executar tudo (com verificações)
docker compose up --build             # Executar direto
docker compose run --rm benchmark sh  # Debug interativo
```

### Local (uv)
```bash
uv run python -m compare_firebird_diferent_os.main       # Teste rápido
uv run python -m compare_firebird_diferent_os.benchmark  # Benchmark
uv run python analyze_results.py                         # Análise
```

---

## 📊 Fluxo de Trabalho Típico

```
1. Configurar .env
   ↓
2. Testar conectividade (main.py)
   ↓
3. Executar benchmark (benchmark.py)
   ↓
4. Analisar resultados (analyze_results.py ou Excel)
   ↓
5. Fazer ajustes nos servidores
   ↓
6. Repetir benchmark e comparar
```

---

## 🐛 Problemas Comuns

| Problema | Solução Rápida |
|----------|----------------|
| Não conecta ao servidor | `ping <IP>` e verificar porta 3050 |
| Senha incorreta | Verificar `.env` e testar com isql/FlameRobin |
| CSV não gerado | Verificar permissões de escrita |
| Docker não acessa servidor | Usar `network_mode: host` no compose |

📖 Ver [TROUBLESHOOTING.md](TROUBLESHOOTING.md) para detalhes

---

## 📈 Resultados

### Arquivo CSV
```csv
server;run_index;elapsed_seconds;query;runs
Windows;1;0.045123;SELECT...;20
Linux;1;0.038567;SELECT...;20
```

### Análise
- Abrir no Excel/LibreOffice
- Usar `analyze_results.py` para estatísticas
- Criar gráficos comparativos

---

## 🎓 Próximos Passos

1. **Queries Personalizadas**: Edite `FB_BENCH_QUERY` com queries reais do seu sistema
2. **Tunning**: Ajuste `firebird.conf` e compare antes/depois
3. **Automatização**: Configure cron/scheduled task para benchmarks periódicos
4. **Visualização**: Use matplotlib/plotly para gráficos

---

## 📚 Documentação Completa

- [README.md](README.md) - Documentação completa
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Resolução de problemas
- [src/README.md](src/README.md) - Detalhes técnicos do código

---

## 🆘 Suporte

- 📧 Issues: https://github.com/andreagnoletto/compare-firebird-different-os/issues
- 📖 Wiki: (em breve)
- 💬 Discussões: (em breve)

---

**Última atualização:** Novembro 2025
