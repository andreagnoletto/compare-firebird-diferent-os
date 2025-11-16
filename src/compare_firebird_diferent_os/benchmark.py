import csv
import os
import statistics
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List

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
) -> List[float]:
    """Executa a mesma query N vezes numa conexão única e mede o tempo de cada execução."""
    print(f"\n== Benchmark em {cfg.name} ==")
    print(f"Host: {cfg.host}, DB: {cfg.database}")
    print(f"Execuções: {runs}")
    print(f"Query: {query}\n")

    conn = open_connection(cfg)
    cur = conn.cursor()

    times: List[float] = []

    for i in range(1, runs + 1):
        t0 = time.perf_counter()
        cur.execute(query)
        # Em geral para benchmark simples basta um fetchone.
        row = cur.fetchone()
        t1 = time.perf_counter()

        elapsed = t1 - t0
        times.append(elapsed)
        print(f"[{cfg.name}] Execução {i}/{runs}: {elapsed:.6f} s | retorno={row}")

    conn.close()
    return times


def save_csv(
    filename: str,
    results: Dict[str, List[float]],
    query: str,
    runs: int,
) -> Path:
    path = Path(filename).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["server", "run_index", "elapsed_seconds", "query", "runs"])
        for server, times in results.items():
            for idx, t in enumerate(times, start=1):
                writer.writerow([server, idx, f"{t:.6f}", query, runs])

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

    all_results: Dict[str, List[float]] = {}

    for key, cfg in configs.items():
        try:
            times = run_benchmark_for_server(cfg, query=query, runs=runs)
            all_results[cfg.name] = times
        except Exception as e:
            print(f"\nERRO ao executar benchmark em {cfg.name}: {e}")

    print("\n==== Estatísticas gerais ====")
    for server_name, times in all_results.items():
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
