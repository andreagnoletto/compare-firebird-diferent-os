import csv
import os
import statistics
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

import fdb
from dotenv import load_dotenv


@dataclass
class FbConfig:
    name: str
    host: str
    port: int
    database: str
    user: str
    password: str


@dataclass
class BenchmarkResult:
    elapsed_time: float
    server_execution_time: Optional[float] = None
    plan_info: Optional[str] = None
    records_fetched: Optional[int] = None


def load_configs() -> Dict[str, FbConfig]:
    load_dotenv()

    win = FbConfig(
        name="Windows",
        host=os.getenv("WIN_FB_HOST", ""),
        port=int(os.getenv("WIN_FB_PORT", "3050")),
        database=os.getenv("WIN_FB_DATABASE", ""),
        user=os.getenv("WIN_FB_USER", ""),
        password=os.getenv("WIN_FB_PASSWORD", ""),
    )

    lin = FbConfig(
        name="Linux",
        host=os.getenv("LIN_FB_HOST", ""),
        port=int(os.getenv("LIN_FB_PORT", "3050")),
        database=os.getenv("LIN_FB_DATABASE", ""),
        user=os.getenv("LIN_FB_USER", ""),
        password=os.getenv("LIN_FB_PASSWORD", ""),
    )

    for cfg in (win, lin):
        missing = [
            field
            for field, value in [
                ("host", cfg.host),
                ("database", cfg.database),
                ("user", cfg.user),
                ("password", cfg.password),
            ]
            if not value
        ]
        if missing:
            raise ValueError(
                f"Variáveis ausentes para conexão {cfg.name}: {', '.join(missing)}"
            )

    return {"windows": win, "linux": lin}


def open_connection(cfg: FbConfig) -> fdb.Connection:
    return fdb.connect(
        host=cfg.host,
        port=cfg.port,
        database=cfg.database,
        user=cfg.user,
        password=cfg.password,
        charset="UTF8",
    )


def run_benchmark_for_server(
    cfg: FbConfig, query: str, runs: int
) -> Tuple[List[float], List[Optional[Dict[str, Any]]]]:
    """Executa a mesma query N vezes numa conexão única e mede o tempo de cada execução."""
    print(f"\n== Benchmark em {cfg.name} ==")
    print(f"Host: {cfg.host}, DB: {cfg.database}")
    print(f"Execuções: {runs}")
    print(f"Query: {query}\n")

    conn = open_connection(cfg)
    cur = conn.cursor()
    
    # Cursor separado para monitoramento
    mon_cur = conn.cursor()

    times: List[float] = []
    stats_list: List[Optional[Dict[str, Any]]] = []

    for i in range(1, runs + 1):
        # Captura estatísticas do servidor
        server_info: Dict[str, Any] = {}
        
        try:
            # Obtém o plano de execução
            cur.execute(f"SET PLANONLY")
            cur.execute(query)
            plan = cur.plan
            cur.execute(f"SET PLANONLY OFF")
            if plan:
                server_info['plan'] = plan
        except Exception as e:
            server_info['plan_error'] = str(e)
        
        # Captura estatísticas ANTES da execução
        stats_before = None
        try:
            mon_cur.execute("""
                SELECT MON$ATTACHMENT_ID 
                FROM MON$ATTACHMENTS 
                WHERE MON$ATTACHMENT_ID = CURRENT_CONNECTION
            """)
            attachment_id = mon_cur.fetchone()[0]
            
            mon_cur.execute(f"""
                SELECT 
                    SUM(MON$RECORD_SEQ_READS) as SEQ_READS,
                    SUM(MON$RECORD_IDX_READS) as IDX_READS,
                    SUM(MON$RECORD_INSERTS) as INSERTS,
                    SUM(MON$RECORD_UPDATES) as UPDATES,
                    SUM(MON$RECORD_DELETES) as DELETES,
                    SUM(MON$RECORD_BACKOUTS) as BACKOUTS,
                    SUM(MON$RECORD_PURGES) as PURGES,
                    SUM(MON$RECORD_EXPUNGES) as EXPUNGES
                FROM MON$IO_STATS
                WHERE MON$STAT_GROUP = 1 
                AND MON$STAT_ID = {attachment_id}
            """)
            stats_before = mon_cur.fetchone()
        except Exception:
            pass
        
        # Mede tempo total (cliente + servidor + rede + latência)
        t0 = time.perf_counter()
        t_server_start = time.perf_counter()
        cur.execute(query)
        row = cur.fetchone()
        t_server_end = time.perf_counter()
        t1 = time.perf_counter()

        elapsed_total = t1 - t0
        elapsed_server = t_server_end - t_server_start
        times.append(elapsed_total)
        
        server_info['elapsed_total'] = elapsed_total
        server_info['elapsed_server'] = elapsed_server
        
        # Captura estatísticas DEPOIS da execução
        if stats_before:
            try:
                mon_cur.execute(f"""
                    SELECT 
                        SUM(MON$RECORD_SEQ_READS) as SEQ_READS,
                        SUM(MON$RECORD_IDX_READS) as IDX_READS,
                        SUM(MON$RECORD_INSERTS) as INSERTS,
                        SUM(MON$RECORD_UPDATES) as UPDATES,
                        SUM(MON$RECORD_DELETES) as DELETES,
                        SUM(MON$RECORD_BACKOUTS) as BACKOUTS,
                        SUM(MON$RECORD_PURGES) as PURGES,
                        SUM(MON$RECORD_EXPUNGES) as EXPUNGES
                    FROM MON$IO_STATS
                    WHERE MON$STAT_GROUP = 1 
                    AND MON$STAT_ID = {attachment_id}
                """)
                stats_after = mon_cur.fetchone()
                
                # Calcula diferenças
                if stats_before and stats_after:
                    server_info['seq_reads'] = stats_after[0] - stats_before[0]
                    server_info['idx_reads'] = stats_after[1] - stats_before[1]
                    server_info['inserts'] = stats_after[2] - stats_before[2]
                    server_info['updates'] = stats_after[3] - stats_before[3]
                    server_info['deletes'] = stats_after[4] - stats_before[4]
            except Exception:
                pass
        
        # Tenta obter informações adicionais do cursor
        try:
            if hasattr(cur, 'rowcount') and cur.rowcount >= 0:
                server_info['rowcount'] = cur.rowcount
        except:
            pass
            
        stats_list.append(server_info if server_info else None)
        
        latency = elapsed_total - elapsed_server
        print(f"[{cfg.name}] Execução {i}/{runs}: total={elapsed_total:.6f}s, servidor={elapsed_server:.6f}s, latência={latency:.6f}s | retorno={row}")

    conn.close()
    return times, stats_list


def save_csv(
    filename: str,
    results: Dict[str, Tuple[List[float], List[Optional[Dict[str, Any]]]]],
    query: str,
    runs: int,
) -> Path:
    path = Path(filename).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([
            "server", "run_index", "elapsed_total_seconds", "elapsed_server_seconds", 
            "latency_seconds", "seq_reads", "idx_reads", "inserts", "updates", "deletes",
            "plan", "rowcount", "query", "runs"
        ])
        for server, (times, stats_list) in results.items():
            for idx, (t, stats) in enumerate(zip(times, stats_list), start=1):
                elapsed_total = stats.get('elapsed_total', t) if stats else t
                elapsed_server = stats.get('elapsed_server', '') if stats else ''
                latency = (elapsed_total - elapsed_server) if (stats and 'elapsed_server' in stats) else ''
                
                seq_reads = stats.get('seq_reads', '') if stats else ''
                idx_reads = stats.get('idx_reads', '') if stats else ''
                inserts = stats.get('inserts', '') if stats else ''
                updates = stats.get('updates', '') if stats else ''
                deletes = stats.get('deletes', '') if stats else ''
                
                plan = stats.get('plan', '') if stats else ''
                rowcount = stats.get('rowcount', '') if stats else ''
                
                writer.writerow([
                    server, idx, f"{elapsed_total:.6f}", 
                    f"{elapsed_server:.6f}" if elapsed_server != '' else '',
                    f"{latency:.6f}" if latency != '' else '',
                    seq_reads, idx_reads, inserts, updates, deletes,
                    plan, rowcount, query, runs
                ])

    return path


def print_stats(label: str, times: List[float]) -> None:
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


def main() -> None:
    configs = load_configs()

    runs = int(os.getenv("FB_BENCH_RUNS", "20"))
    query = os.getenv(
        "FB_BENCH_QUERY", "SELECT CURRENT_TIMESTAMP FROM RDB$DATABASE"
    )

    all_results: Dict[str, Tuple[List[float], List[Optional[Dict[str, Any]]]]] = {}

    for key, cfg in configs.items():
        try:
            times, stats = run_benchmark_for_server(cfg, query=query, runs=runs)
            all_results[cfg.name] = (times, stats)
        except Exception as e:
            print(f"\nERRO ao executar benchmark em {cfg.name}: {e}")

    print("\n==== Estatísticas gerais ====")
    for server_name, (times, _) in all_results.items():
        print_stats(server_name, times)

    if all_results:
        csv_path = save_csv(
            filename="firebird_benchmark_results.csv",
            results=all_results,
            query=query,
            runs=runs,
        )
        print(f"\nResultados detalhados salvos em: {csv_path}")


if __name__ == "__main__":
    main()
