"""
Multi-database benchmark module.

Provides benchmarking capabilities for multiple SQL databases (Firebird, MySQL,
PostgreSQL, MariaDB) across different operating systems with scientific statistical
analysis.

Supports concurrent execution with multiple threads for improved performance.
"""

import csv
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

from .database import DatabaseConfig, DatabaseConnectionFactory
from .collectors import StatisticsCollectorFactory


def _execute_single_query(
    config: DatabaseConfig, 
    query: str, 
    run_number: int,
    total_runs: int
) -> Tuple[float, Optional[Dict[str, Any]]]:
    """
    Execute uma única query (usada para execução concorrente).
    
    Args:
        config: Database configuration
        query: SQL query to execute
        run_number: Número da execução (1-based)
        total_runs: Total de execuções
    
    Returns:
        Tuple of (elapsed_time, stats_dict)
    """
    try:
        # Create new connection for this thread
        connection = DatabaseConnectionFactory.create(config)
        connection.connect()
        
        # Create statistics collector
        stats_collector = StatisticsCollectorFactory.create(config.db_type, connection)
        
        server_info: Dict[str, Any] = {}
        
        # Get execution plan (apenas na primeira execução para não sobrecarregar)
        if run_number == 1:
            try:
                plan = stats_collector.get_execution_plan(query)
                if plan:
                    server_info['plan'] = plan
            except Exception as e:
                server_info['plan_error'] = str(e)
        
        # Capture statistics BEFORE
        try:
            stats_collector.capture_before()
        except Exception:
            pass
        
        # Measure time
        t0 = time.perf_counter()
        t_server_start = time.perf_counter()
        
        connection.execute_query(query)
        row = connection.fetchone()
        
        t_server_end = time.perf_counter()
        t1 = time.perf_counter()

        elapsed_total = t1 - t0
        elapsed_server = t_server_end - t_server_start
        
        server_info['elapsed_total'] = elapsed_total
        server_info['elapsed_server'] = elapsed_server
        server_info['latency'] = elapsed_total - elapsed_server
        
        # Capture statistics AFTER
        try:
            stats_collector.capture_after()
            io_stats = stats_collector.get_io_stats()
            server_info.update(io_stats)
        except Exception:
            pass
        
        # Get rowcount
        try:
            cursor = connection.cursor
            if hasattr(cursor, 'rowcount') and cursor.rowcount >= 0:
                server_info['rowcount'] = cursor.rowcount
        except:
            pass
        
        connection.close()
        
        # Print progress
        print(
            f"[{config.name}] ✓ {run_number}/{total_runs}: "
            f"{elapsed_total:.6f}s"
        )
        
        return elapsed_total, server_info
        
    except Exception as e:
        print(f"[{config.name}] ✗ {run_number}/{total_runs}: Erro - {e}")
        return 0.0, None


def run_benchmark_for_server_concurrent(
    config: DatabaseConfig, 
    query: str, 
    runs: int,
    max_workers: int = 10
) -> Tuple[List[float], List[Optional[Dict[str, Any]]]]:
    """
    Execute query N vezes com execução CONCORRENTE (múltiplas threads).
    
    Args:
        config: Database configuration
        query: SQL query to execute
        runs: Number of times to execute the query
        max_workers: Número máximo de threads paralelas (padrão: 10)
    
    Returns:
        Tuple of (times list, stats list)
    """
    print(f"\n== Benchmark CONCORRENTE em {config.name} ==")
    print(f"Tipo: {config.db_type.upper()}, OS: {config.os_type.upper()}")
    print(f"Host: {config.host}, DB: {config.database}")
    print(f"Execuções: {runs} (max {max_workers} threads paralelas)")
    print(f"Query: {query}\n")

    times: List[float] = []
    stats_list: List[Optional[Dict[str, Any]]] = []
    
    # Execute com ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit todas as tarefas
        futures = {
            executor.submit(_execute_single_query, config, query, i, runs): i 
            for i in range(1, runs + 1)
        }
        
        # Coletar resultados conforme completam
        results_dict = {}
        for future in as_completed(futures):
            run_num = futures[future]
            try:
                elapsed_time, stats = future.result()
                results_dict[run_num] = (elapsed_time, stats)
            except Exception as e:
                print(f"[{config.name}] Erro na execução {run_num}: {e}")
                results_dict[run_num] = (0.0, None)
    
    # Ordenar resultados pela ordem de execução original
    for i in range(1, runs + 1):
        if i in results_dict:
            elapsed_time, stats = results_dict[i]
            times.append(elapsed_time)
            stats_list.append(stats)
    
    print(f"\n✅ Benchmark concorrente concluído: {len(times)}/{runs} execuções bem-sucedidas\n")
    
    return times, stats_list


def run_benchmark_for_server(
    config: DatabaseConfig, query: str, runs: int
) -> Tuple[List[float], List[Optional[Dict[str, Any]]]]:
    """
    Execute the same query N times on a single connection and measure execution time.
    
    Args:
        config: Database configuration
        query: SQL query to execute
        runs: Number of times to execute the query
    
    Returns:
        Tuple of (times list, stats list)
    """
    print(f"\n== Benchmark em {config.name} ==")
    print(f"Tipo: {config.db_type.upper()}, OS: {config.os_type.upper()}")
    print(f"Host: {config.host}, DB: {config.database}")
    print(f"Execuções: {runs}")
    print(f"Query: {query}\n")

    # Create database connection using factory
    connection = DatabaseConnectionFactory.create(config)
    connection.connect()
    
    # Create statistics collector using factory
    stats_collector = StatisticsCollectorFactory.create(config.db_type, connection)

    times: List[float] = []
    stats_list: List[Optional[Dict[str, Any]]] = []

    for i in range(1, runs + 1):
        # Collect statistics for this execution
        server_info: Dict[str, Any] = {}
        
        # Get execution plan (without actually running the query)
        try:
            plan = stats_collector.get_execution_plan(query)
            if plan:
                server_info['plan'] = plan
        except Exception as e:
            server_info['plan_error'] = str(e)
        
        # Capture statistics BEFORE execution
        try:
            stats_collector.capture_before()
        except Exception:
            pass
        
        # Measure total time (client + server + network)
        t0 = time.perf_counter()
        t_server_start = time.perf_counter()
        
        connection.execute_query(query)
        row = connection.fetchone()
        
        t_server_end = time.perf_counter()
        t1 = time.perf_counter()

        elapsed_total = t1 - t0
        elapsed_server = t_server_end - t_server_start
        times.append(elapsed_total)
        
        server_info['elapsed_total'] = elapsed_total
        server_info['elapsed_server'] = elapsed_server
        server_info['latency'] = elapsed_total - elapsed_server
        
        # Capture statistics AFTER execution
        try:
            stats_collector.capture_after()
            io_stats = stats_collector.get_io_stats()
            server_info.update(io_stats)
        except Exception:
            pass
        
        # Get rowcount if available
        try:
            cursor = connection.cursor
            if hasattr(cursor, 'rowcount') and cursor.rowcount >= 0:
                server_info['rowcount'] = cursor.rowcount
        except:
            pass
            
        stats_list.append(server_info if server_info else None)
        
        latency = elapsed_total - elapsed_server
        print(
            f"[{config.name}] Execução {i}/{runs}: "
            f"total={elapsed_total:.6f}s, servidor={elapsed_server:.6f}s, "
            f"latência={latency:.6f}s | retorno={row}"
        )
        
        # Reset collector for next iteration
        stats_collector.reset()

    connection.close()
    return times, stats_list


def save_csv(
    filename: str,
    results: Dict[str, Tuple[DatabaseConfig, List[float], List[Optional[Dict[str, Any]]]]],
    query: str,
    runs: int,
) -> Path:
    """
    Save benchmark results to CSV file.
    
    Args:
        filename: Output CSV filename
        results: Dictionary mapping server name to (config, times, stats)
        query: Query that was executed
        runs: Number of runs performed
    
    Returns:
        Path to the saved CSV file
    """
    path = Path(filename).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        
        # Extended header with db_type and os_type
        writer.writerow([
            "db_type", "os_type", "server_name", "run_index", 
            "elapsed_total_seconds", "elapsed_server_seconds", 
            "latency_seconds", "seq_reads", "idx_reads", "inserts", "updates", "deletes",
            "plan", "rowcount", "query", "runs"
        ])
        
        for server_name, (config, times, stats_list) in results.items():
            for idx, (t, stats) in enumerate(zip(times, stats_list), start=1):
                elapsed_total = stats.get('elapsed_total', t) if stats else t
                elapsed_server = stats.get('elapsed_server', '') if stats else ''
                latency = stats.get('latency', '') if stats else ''
                
                seq_reads = stats.get('seq_reads', '') if stats else ''
                idx_reads = stats.get('idx_reads', '') if stats else ''
                inserts = stats.get('inserts', '') if stats else ''
                updates = stats.get('updates', '') if stats else ''
                deletes = stats.get('deletes', '') if stats else ''
                
                plan = stats.get('plan', '') if stats else ''
                rowcount = stats.get('rowcount', '') if stats else ''
                
                writer.writerow([
                    config.db_type,
                    config.os_type,
                    server_name,
                    idx,
                    f"{elapsed_total:.6f}",
                    f"{elapsed_server:.6f}" if elapsed_server != '' else '',
                    f"{latency:.6f}" if latency != '' else '',
                    seq_reads, idx_reads, inserts, updates, deletes,
                    plan, rowcount, query, runs
                ])

    return path


def print_stats(label: str, times: List[float]) -> None:
    """
    Print statistical summary of benchmark times.
    
    Args:
        label: Label for the benchmark (e.g., server name)
        times: List of execution times
    """
    if not times:
        print(f"{label}: sem dados.")
        return

    mean = statistics.fmean(times)
    min_t = min(times)
    max_t = max(times)

    print(
        f"{label}: média={mean:.6f}s, mínimo={min_t:.6f}s, máximo={max_t:.6f}s, "
        f"execuções={len(times)}"
    )


def run_benchmark(
    configs: List[DatabaseConfig],
    query: str,
    runs: int,
    output_file: str = "benchmark_results.csv",
    concurrent: bool = False,
    max_workers: int = 10
) -> Dict[str, Tuple[DatabaseConfig, List[float], List[Optional[Dict[str, Any]]]]]:
    """
    Run benchmarks on multiple database servers.
    
    Args:
        configs: List of database configurations
        query: SQL query to execute
        runs: Number of times to execute the query per server
        output_file: Output CSV filename
        concurrent: Se True, executa queries em paralelo (padrão: False)
        max_workers: Número máximo de threads paralelas quando concurrent=True (padrão: 10)
    
    Returns:
        Dictionary mapping server name to (config, times, stats)
    """
    all_results: Dict[str, Tuple[DatabaseConfig, List[float], List[Optional[Dict[str, Any]]]]] = {}

    for config in configs:
        try:
            if concurrent:
                times, stats = run_benchmark_for_server_concurrent(
                    config, query=query, runs=runs, max_workers=max_workers
                )
            else:
                times, stats = run_benchmark_for_server(config, query=query, runs=runs)
            all_results[config.name] = (config, times, stats)
        except Exception as e:
            print(f"\n❌ ERRO ao executar benchmark em {config.name}: {e}")
            import traceback
            traceback.print_exc()

    # Print general statistics
    print("\n==== Estatísticas gerais ====")
    for server_name, (config, times, _) in all_results.items():
        print_stats(f"{server_name} ({config.db_type}/{config.os_type})", times)

    # Save results to CSV
    if all_results:
        csv_path = save_csv(
            filename=output_file,
            results=all_results,
            query=query,
            runs=runs,
        )
        print(f"\n✅ Resultados detalhados salvos em: {csv_path}")
    
    return all_results
