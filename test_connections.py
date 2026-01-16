#!/usr/bin/env python3
"""
Test database connections for all configured servers.

This script validates that all database servers configured in .env are
accessible and reports their versions and connection status.
"""

import sys
from typing import Dict, Any, Optional

from src.compare_firebird_diferent_os.config import load_database_configs
from src.compare_firebird_diferent_os.database import DatabaseConnectionFactory


def get_database_version(db_type: str, connection: Any) -> Optional[str]:
    """
    Get database version string.
    
    Args:
        db_type: Database type ('firebird', 'mysql', 'postgresql', 'mariadb')
        connection: DatabaseConnection instance
    
    Returns:
        Version string or None if unavailable
    """
    version_queries = {
        'firebird': "SELECT rdb$get_context('SYSTEM', 'ENGINE_VERSION') FROM RDB$DATABASE",
        'mysql': "SELECT VERSION()",
        'postgresql': "SELECT version()",
        'mariadb': "SELECT VERSION()",
    }
    
    query = version_queries.get(db_type)
    if not query:
        return None
    
    try:
        connection.execute_query(query)
        result = connection.fetchone()
        return result[0] if result else None
    except Exception as e:
        return f"Error: {str(e)}"


def test_connection(config) -> Dict[str, Any]:
    """
    Test a single database connection.
    
    Args:
        config: DatabaseConfig instance
    
    Returns:
        Dictionary with test results
    """
    result = {
        'name': config.name,
        'db_type': config.db_type,
        'os_type': config.os_type,
        'host': config.host,
        'port': config.port,
        'database': config.database,
        'status': 'unknown',
        'version': None,
        'error': None,
    }
    
    try:
        # Create connection
        connection = DatabaseConnectionFactory.create(config)
        connection.connect()
        
        # Test simple query (Firebird-compatible)
        test_query = "SELECT 1 FROM RDB$DATABASE" if config.db_type == 'firebird' else "SELECT 1"
        connection.execute_query(test_query)
        test_result = connection.fetchone()
        
        if test_result:
            result['status'] = 'success'
            
            # Get version
            version = get_database_version(config.db_type, connection)
            result['version'] = version
        else:
            result['status'] = 'failed'
            result['error'] = 'Query returned no results'
        
        connection.close()
        
    except Exception as e:
        result['status'] = 'failed'
        result['error'] = str(e)
    
    return result


def main() -> None:
    """Main execution."""
    print("=" * 80)
    print("🔌 TESTE DE CONEXÕES - Multi-Database Benchmark")
    print("=" * 80)
    
    try:
        # Load configurations
        print("\n📋 Carregando configurações...")
        configs = load_database_configs()
        
        print(f"✅ {len(configs)} servidor(es) encontrado(s)\n")
        
        # Test each connection
        results = []
        for i, config in enumerate(configs, 1):
            print(f"\n[{i}/{len(configs)}] Testando: {config.name}")
            print(f"    Tipo: {config.db_type.upper()}")
            print(f"    OS: {config.os_type.upper()}")
            print(f"    Host: {config.host}:{config.port}")
            print(f"    Database: {config.database}")
            print("    Status: ", end="", flush=True)
            
            result = test_connection(config)
            results.append(result)
            
            if result['status'] == 'success':
                print("✅ CONECTADO")
                if result['version']:
                    print(f"    Versão: {result['version']}")
            else:
                print("❌ FALHOU")
                if result['error']:
                    print(f"    Erro: {result['error']}")
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 RESUMO")
        print("=" * 80)
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        failed_count = len(results) - success_count
        
        print(f"\n  Total: {len(results)} servidor(es)")
        print(f"  ✅ Sucesso: {success_count}")
        print(f"  ❌ Falha: {failed_count}")
        
        if failed_count > 0:
            print("\n⚠️  Servidores com falha:")
            for result in results:
                if result['status'] != 'success':
                    print(f"  - {result['name']}: {result['error']}")
        
        print("\n" + "=" * 80)
        
        # Exit with appropriate code
        sys.exit(0 if failed_count == 0 else 1)
        
    except ValueError as e:
        print(f"\n❌ Erro de configuração: {e}")
        print("\n💡 Verifique seu arquivo .env")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
