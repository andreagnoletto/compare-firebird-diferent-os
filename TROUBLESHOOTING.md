# Troubleshooting - Docker Client Mode

Este guia ajuda a resolver problemas comuns ao usar o Docker para conectar a servidores Firebird externos.

## 🔍 Problema: Container não consegue conectar aos servidores

### Verificação 1: Teste de conectividade

```bash
# Teste se consegue fazer ping nos servidores
ping 192.168.1.10  # IP do servidor Windows
ping 192.168.1.20  # IP do servidor Linux

# Teste se a porta do Firebird está acessível
telnet 192.168.1.10 3050
# ou
nc -zv 192.168.1.10 3050
```

### Verificação 2: Firewall

Certifique-se que:
- A porta 3050 (ou a porta configurada) está liberada no firewall do servidor
- O servidor Firebird está configurado para aceitar conexões remotas
- No Windows: Verifique o Windows Firewall
- No Linux: Verifique iptables/ufw

```bash
# Linux - Liberar porta 3050
sudo ufw allow 3050/tcp

# Verificar regras
sudo ufw status
```

### Verificação 3: Configuração do Firebird

No arquivo `firebird.conf` do servidor, verifique:

```conf
# Deve permitir conexões remotas
RemoteBindAddress = 0.0.0.0

# Ou comentar a linha para aceitar de qualquer interface
#RemoteBindAddress = 
```

Reinicie o serviço Firebird após alterar:

```bash
# Linux
sudo systemctl restart firebird

# Windows (como administrador)
net stop FirebirdServerDefaultInstance
net start FirebirdServerDefaultInstance
```

---

## 🔍 Problema: Erro "Cannot attach to password database"

### Solução: Verificar credenciais

No arquivo `.env`, certifique-se que:

```dotenv
WIN_FB_USER=sysdba
WIN_FB_PASSWORD=sua_senha_correta
```

Teste a conexão manualmente:

```bash
# Do container Docker
docker compose run --rm benchmark sh

# Dentro do container, teste:
uv run python -c "import fdb; print(fdb.connect(host='192.168.1.10', database='/path/to/db.fdb', user='sysdba', password='masterkey'))"
```

---

## 🔍 Problema: "Database file appears corrupt"

### Verificação: Caminho do banco de dados

**Windows:**
```dotenv
WIN_FB_DATABASE=C:/databases/mydb.fdb
# ou usando barra invertida (escape)
WIN_FB_DATABASE=C:\\databases\\mydb.fdb
# ou usando alias (recomendado)
WIN_FB_DATABASE=mydb
```

**Linux:**
```dotenv
LIN_FB_DATABASE=/var/lib/firebird/data/mydb.fdb
# ou usando alias
LIN_FB_DATABASE=mydb
```

### Usando Aliases (Recomendado)

Configure o arquivo `aliases.conf` no servidor Firebird:

```conf
# aliases.conf
mydb = /var/lib/firebird/data/production.fdb
```

Então no `.env`:
```dotenv
LIN_FB_DATABASE=mydb
```

---

## 🔍 Problema: Container não encontra o arquivo .env

### Solução:

```bash
# Verificar se o .env existe
ls -la .env

# Se não existir, criar a partir do exemplo
cp .env.docker .env

# Editar com suas configurações
nano .env
```

---

## 🔍 Problema: Versão do Firebird incompatível

O driver `fdb` suporta Firebird 2.5, 3.0 e 4.0. Se tiver problemas:

### Verificar versão do Firebird no servidor

```sql
-- Execute esta query
SELECT rdb$get_context('SYSTEM', 'ENGINE_VERSION') FROM RDB$DATABASE;
```

### Atualizar driver fdb

Edite `pyproject.toml`:

```toml
dependencies = [
    "fdb>=2.0.4",  # ou versão específica
    "python-dotenv>=1.2.1",
]
```

Rebuild o container:
```bash
docker compose build --no-cache
```

---

## 🔍 Problema: Permissões no Linux

Se o container não conseguir escrever o CSV:

```bash
# Dar permissões na pasta
chmod 777 .

# Ou criar o arquivo vazio antes
touch firebird_benchmark_results.csv
chmod 666 firebird_benchmark_results.csv
```

---

## 🔍 Problema: Docker usa muita memória/CPU

### Limitar recursos do container

Edite `docker-compose.yml`:

```yaml
services:
  benchmark:
    # ... outras configurações ...
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          memory: 256M
```

---

## 🐛 Debug Avançado

### Executar container em modo interativo

```bash
# Entrar no container
docker compose run --rm benchmark sh

# Testar comandos manualmente
uv run python -c "import fdb; print(fdb.__version__)"
uv run python -m compare_firebird_diferent_os.main
uv run python -m compare_firebird_diferent_os.benchmark

# Ver variáveis de ambiente
env | grep FB
```

### Ver logs completos

```bash
# Executar com logs detalhados
docker compose up --build 2>&1 | tee benchmark.log

# Ver logs do container
docker compose logs benchmark
```

### Testar conectividade de dentro do container

```bash
docker compose run --rm benchmark sh

# Dentro do container:
ping -c 3 192.168.1.10
nc -zv 192.168.1.10 3050

# Testar Python
uv run python << 'EOF'
import fdb
import os

host = os.getenv('WIN_FB_HOST')
port = int(os.getenv('WIN_FB_PORT', '3050'))
database = os.getenv('WIN_FB_DATABASE')
user = os.getenv('WIN_FB_USER')
password = os.getenv('WIN_FB_PASSWORD')

print(f"Tentando conectar em {host}:{port}")
print(f"Database: {database}")
print(f"User: {user}")

try:
    conn = fdb.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )
    print("✓ Conexão bem-sucedida!")
    conn.close()
except Exception as e:
    print(f"✗ Erro: {e}")
EOF
```

---

## 📞 Ainda com problemas?

1. Verifique se consegue conectar usando outra ferramenta (FlameRobin, DBeaver, IBExpert)
2. Teste conexão local no servidor antes de tentar remoto
3. Verifique logs do Firebird: `/var/log/firebird/` (Linux) ou Event Viewer (Windows)
4. Abra uma issue no GitHub com:
   - Versão do Firebird
   - Sistema operacional dos servidores
   - Arquivo `.env` (sem senhas!)
   - Logs de erro completos
