#!/usr/bin/env python3
"""
Script de validação da implementação multi-database.

Verifica se todos os módulos foram criados corretamente e podem ser importados.
"""

import sys
from pathlib import Path

def validate_imports():
    """Valida que todos os módulos podem ser importados."""
    print("🔍 Validando implementação multi-database...\n")
    
    errors = []
    warnings = []
    
    # 1. Validar classes base
    print("1️⃣  Verificando classes base...")
    try:
        from src.compare_firebird_diferent_os.database import (
            DatabaseConfig,
            DatabaseConnection,
            DatabaseConnectionFactory
        )
        print("   ✅ database/__init__.py OK")
    except Exception as e:
        errors.append(f"database/__init__.py: {e}")
        print(f"   ❌ database/__init__.py: {e}")
    
    try:
        from src.compare_firebird_diferent_os.collectors import (
            StatisticsCollector,
            StatisticsCollectorFactory
        )
        print("   ✅ collectors/__init__.py OK")
    except Exception as e:
        errors.append(f"collectors/__init__.py: {e}")
        print(f"   ❌ collectors/__init__.py: {e}")
    
    # 2. Validar implementações de banco de dados
    print("\n2️⃣  Verificando implementações de banco de dados...")
    
    databases = ['firebird', 'mysql', 'postgresql', 'mariadb']
    for db in databases:
        try:
            module = __import__(
                f'src.compare_firebird_diferent_os.database.{db}',
                fromlist=['']
            )
            print(f"   ✅ database/{db}.py OK")
        except Exception as e:
            # MySQL/PostgreSQL/MariaDB podem falhar se os drivers não estiverem instalados
            # mas isso é esperado em alguns ambientes
            if db in ['mysql', 'postgresql', 'mariadb']:
                warnings.append(f"database/{db}.py: {e} (driver pode não estar instalado)")
                print(f"   ⚠️  database/{db}.py: driver pode não estar instalado")
            else:
                errors.append(f"database/{db}.py: {e}")
                print(f"   ❌ database/{db}.py: {e}")
    
    # 3. Validar coletores de estatísticas
    print("\n3️⃣  Verificando coletores de estatísticas...")
    
    for db in databases:
        try:
            module = __import__(
                f'src.compare_firebird_diferent_os.collectors.{db}',
                fromlist=['']
            )
            print(f"   ✅ collectors/{db}.py OK")
        except Exception as e:
            if db in ['mysql', 'postgresql', 'mariadb']:
                warnings.append(f"collectors/{db}.py: {e}")
                print(f"   ⚠️  collectors/{db}.py: {e}")
            else:
                errors.append(f"collectors/{db}.py: {e}")
                print(f"   ❌ collectors/{db}.py: {e}")
    
    # 4. Validar módulos principais
    print("\n4️⃣  Verificando módulos principais...")
    
    try:
        from src.compare_firebird_diferent_os import config
        print("   ✅ config.py OK")
    except Exception as e:
        errors.append(f"config.py: {e}")
        print(f"   ❌ config.py: {e}")
    
    try:
        from src.compare_firebird_diferent_os import benchmark_new
        print("   ✅ benchmark_new.py OK")
    except Exception as e:
        errors.append(f"benchmark_new.py: {e}")
        print(f"   ❌ benchmark_new.py: {e}")
    
    try:
        from src.compare_firebird_diferent_os import main_new
        print("   ✅ main_new.py OK")
    except Exception as e:
        errors.append(f"main_new.py: {e}")
        print(f"   ❌ main_new.py: {e}")
    
    # 5. Validar arquivos de documentação
    print("\n5️⃣  Verificando documentação...")
    
    docs = [
        'MULTI_DB_GUIDE.md',
        'IMPLEMENTATION_SUMMARY.md',
        '.env.example',
        'test_connections.py',
        'analyze_multi_db.py'
    ]
    
    for doc in docs:
        if Path(doc).exists():
            print(f"   ✅ {doc} OK")
        else:
            errors.append(f"{doc}: arquivo não encontrado")
            print(f"   ❌ {doc}: não encontrado")
    
    # 6. Resumo
    print("\n" + "=" * 70)
    print("📊 RESUMO DA VALIDAÇÃO")
    print("=" * 70)
    
    if not errors and not warnings:
        print("\n✅ Implementação 100% OK!")
        print("   Todos os módulos foram criados e podem ser importados.")
        return 0
    
    if warnings:
        print(f"\n⚠️  {len(warnings)} aviso(s):")
        for warning in warnings:
            print(f"   - {warning}")
        print("\n   Isso é esperado se os drivers MySQL/PostgreSQL/MariaDB")
        print("   ainda não foram instalados. Execute: uv sync")
    
    if errors:
        print(f"\n❌ {len(errors)} erro(s) encontrado(s):")
        for error in errors:
            print(f"   - {error}")
        return 1
    
    return 0


def validate_structure():
    """Valida estrutura de diretórios."""
    print("\n6️⃣  Verificando estrutura de diretórios...")
    
    dirs = [
        'src/compare_firebird_diferent_os/database',
        'src/compare_firebird_diferent_os/collectors',
    ]
    
    all_ok = True
    for dir_path in dirs:
        if Path(dir_path).exists():
            print(f"   ✅ {dir_path}/ OK")
        else:
            print(f"   ❌ {dir_path}/ não encontrado")
            all_ok = False
    
    return all_ok


if __name__ == "__main__":
    print("🚀 Multi-Database Benchmark - Validação de Implementação\n")
    
    structure_ok = validate_structure()
    import_result = validate_imports()
    
    print("\n" + "=" * 70)
    
    if structure_ok and import_result == 0:
        print("✅ VALIDAÇÃO COMPLETA - Sistema pronto para uso!")
        print("\n📖 Próximos passos:")
        print("   1. Configure seu .env (veja .env.example)")
        print("   2. Teste conexões: uv run python test_connections.py")
        print("   3. Execute benchmark: uv run python -m compare_firebird_diferent_os.main_new")
        sys.exit(0)
    else:
        print("⚠️  Validação com avisos - Verifique as mensagens acima")
        sys.exit(0 if import_result == 0 else 1)
