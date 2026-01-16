"""
Main entry point for multi-database benchmarking.

This script loads database configurations and runs benchmarks across multiple
SQL database systems (Firebird, MySQL, PostgreSQL, MariaDB).
"""

import sys

from .config import load_database_configs, get_benchmark_params
from .benchmark_new import run_benchmark


def main() -> None:
    """Main benchmark execution."""
    try:
        # Load database configurations
        print("📋 Carregando configurações...")
        configs = load_database_configs()
        
        print(f"\n✅ {len(configs)} servidor(es) configurado(s):")
        for i, config in enumerate(configs, 1):
            print(f"  {i}. {config.name} ({config.db_type}/{config.os_type}) @ {config.host}")
        
        # Get benchmark parameters
        params = get_benchmark_params()
        runs = params['runs']
        query = params['query']
        concurrent = params['concurrent']
        max_workers = params['max_workers']
        
        print(f"\n🎯 Parâmetros do benchmark:")
        print(f"  Execuções por servidor: {runs}")
        print(f"  Query: {query}")
        print(f"  Concorrência: {'SIM' if concurrent else 'NÃO'}")
        if concurrent:
            print(f"  Threads paralelas: {max_workers}")
        
        # Run benchmarks
        print(f"\n🚀 Iniciando benchmarks...\n")
        print("=" * 80)
        
        run_benchmark(
            configs=configs,
            query=query,
            runs=runs,
            output_file="benchmark_results.csv",
            concurrent=concurrent,
            max_workers=max_workers
        )
        
        print("\n" + "=" * 80)
        print("\n✅ Benchmark concluído!")
        print("\n💡 Para análise estatística detalhada, execute:")
        print("   uv run python analyze_results.py")
        
    except ValueError as e:
        print(f"\n❌ Erro de configuração: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Benchmark interrompido pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
