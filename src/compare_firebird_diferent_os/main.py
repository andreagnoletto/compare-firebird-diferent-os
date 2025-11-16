import os
import time
from typing import Dict, Any

import fdb
from dotenv import load_dotenv


def load_config() -> Dict[str, Dict[str, Any]]:
    """Carrega variáveis de ambiente para as duas conexões."""
    load_dotenv()

    windows_cfg = {
        "name": "Windows",
        "host": os.getenv("WIN_FB_HOST"),
        "port": int(os.getenv("WIN_FB_PORT", "3050")),
        "database": os.getenv("WIN_FB_DATABASE"),
        "user": os.getenv("WIN_FB_USER"),
        "password": os.getenv("WIN_FB_PASSWORD"),
    }

    linux_cfg = {
        "name": "Linux",
        "host": os.getenv("LIN_FB_HOST"),
        "port": int(os.getenv("LIN_FB_PORT", "3050")),
        "database": os.getenv("LIN_FB_DATABASE"),
        "user": os.getenv("LIN_FB_USER"),
        "password": os.getenv("LIN_FB_PASSWORD"),
    }

    for cfg in (windows_cfg, linux_cfg):
        missing = [k for k, v in cfg.items() if (v is None or v == "") and k != "port"]
        if missing:
            raise ValueError(
                f"Variáveis ausentes para conexão {cfg['name']}: {', '.join(missing)}"
            )

    return {"windows": windows_cfg, "linux": linux_cfg}


def open_connection(cfg: Dict[str, Any]) -> fdb.Connection:
    """Abre uma conexão Firebird com base em um dicionário de config."""
    return fdb.connect(
        host=cfg["host"],
        port=cfg["port"],
        database=cfg["database"],
        user=cfg["user"],
        password=cfg["password"],
        charset="UTF8",
    )


def test_connection(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Abre conexão, executa uma query simples e mede tempo."""
    dsn = f"{cfg['host']}/{cfg['port']}:{cfg['database']}"
    print(f"\n== Testando conexão com {cfg['name']} ==")
    print(f"DSN: {dsn}")

    t0 = time.perf_counter()

    conn = open_connection(cfg)
    t_connect = time.perf_counter()
    print(f"Conexão estabelecida em {t_connect - t0:.4f} s")

    cur = conn.cursor()
    cur.execute("SELECT CURRENT_TIMESTAMP FROM RDB$DATABASE")
    row = cur.fetchone()
    t_query = time.perf_counter()

    print(f"Query simples executada em {t_query - t_connect:.4f} s")
    print(f"CURRENT_TIMESTAMP em {cfg['name']}: {row[0]}")

    conn.close()
    t_end = time.perf_counter()
    total = t_end - t0

    print(f"Tempo total (abrir + query + fechar): {total:.4f} s")

    return {
        "name": cfg["name"],
        "dsn": dsn,
        "t_connect": t_connect - t0,
        "t_query": t_query - t_connect,
        "t_total": total,
    }


def main() -> None:
    configs = load_config()

    results = []
    for key in ("windows", "linux"):
        try:
            res = test_connection(configs[key])
            results.append(res)
        except Exception as e:
            print(f"\nERRO ao testar conexão {configs[key]['name']}: {e}")

    if len(results) == 2:
        print("\n==== Comparação resumida ====")
        for r in results:
            print(
                f"{r['name']}: "
                f"conexão={r['t_connect']:.4f}s, "
                f"query={r['t_query']:.4f}s, "
                f"total={r['t_total']:.4f}s"
            )


if __name__ == "__main__":
    main()
