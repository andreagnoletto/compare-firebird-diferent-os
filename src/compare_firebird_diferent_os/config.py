"""
Configuration loading for multi-database benchmarking.

This module provides flexible configuration loading supporting both:
1. Legacy format: WIN_FB_* and LIN_FB_* environment variables (backward compatible)
2. New format: SERVER{N}_* environment variables for unlimited servers
"""

import os
from typing import Dict, List, Optional

from dotenv import load_dotenv

from .database import DatabaseConfig


def load_database_configs() -> List[DatabaseConfig]:
    """
    Load database configurations from environment variables.
    
    Supports two formats:
    
    1. Legacy format (Firebird only, backward compatible):
       WIN_FB_HOST, WIN_FB_PORT, WIN_FB_DATABASE, WIN_FB_USER, WIN_FB_PASSWORD
       LIN_FB_HOST, LIN_FB_PORT, LIN_FB_DATABASE, LIN_FB_USER, LIN_FB_PASSWORD
    
    2. New format (multi-database):
       SERVER1_TYPE, SERVER1_OS, SERVER1_NAME, SERVER1_HOST, SERVER1_PORT, ...
       SERVER2_TYPE, SERVER2_OS, SERVER2_NAME, SERVER2_HOST, SERVER2_PORT, ...
       ...up to SERVER10
    
    Returns:
        List of DatabaseConfig objects
    
    Raises:
        ValueError: If no valid configurations are found
    """
    load_dotenv()
    
    configs: List[DatabaseConfig] = []
    
    # Try new format first (SERVER{N}_*)
    for i in range(1, 11):  # Support up to 10 servers
        prefix = f"SERVER{i}_"
        
        db_type = os.getenv(f"{prefix}TYPE", "").strip().lower()
        if not db_type:
            continue  # Skip if no type defined
        
        os_type = os.getenv(f"{prefix}OS", "").strip().lower()
        name = os.getenv(f"{prefix}NAME", "").strip()
        host = os.getenv(f"{prefix}HOST", "").strip()
        port_str = os.getenv(f"{prefix}PORT", "").strip()
        database = os.getenv(f"{prefix}DATABASE", "").strip()
        user = os.getenv(f"{prefix}USER", "").strip()
        password = os.getenv(f"{prefix}PASSWORD", "").strip()
        charset = os.getenv(f"{prefix}CHARSET", "UTF8").strip()
        
        # Default port based on database type
        default_ports = {
            'firebird': 3050,
            'mysql': 3306,
            'postgresql': 5432,
            'mariadb': 3306,
        }
        
        try:
            port = int(port_str) if port_str else default_ports.get(db_type, 3050)
        except ValueError:
            port = default_ports.get(db_type, 3050)
        
        # Default name if not provided
        if not name:
            name = f"{db_type.capitalize()} {os_type.capitalize()} #{i}"
        
        # Default OS type if not provided
        if not os_type:
            os_type = "linux"  # Default to linux
        
        # Create config (validation happens in DatabaseConfig.__post_init__)
        try:
            config = DatabaseConfig(
                db_type=db_type,
                os_type=os_type,
                name=name,
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
                charset=charset,
            )
            configs.append(config)
        except ValueError as e:
            print(f"⚠️  Aviso: Configuração SERVER{i} inválida: {e}")
            continue
    
    # If no configs found with new format, try legacy format
    if not configs:
        configs = _load_legacy_configs()
    
    if not configs:
        raise ValueError(
            "Nenhuma configuração de banco de dados encontrada.\n"
            "Configure usando formato SERVER{N}_* no arquivo .env\n"
            "Exemplo: SERVER1_TYPE=firebird, SERVER1_HOST=..., etc."
        )
    
    return configs


def _load_legacy_configs() -> List[DatabaseConfig]:
    """
    Load legacy Firebird configurations (backward compatibility).
    
    Returns:
        List of DatabaseConfig objects from legacy WIN_FB_* and LIN_FB_* variables
    """
    configs: List[DatabaseConfig] = []
    
    # Windows Firebird
    win_host = os.getenv("WIN_FB_HOST", "").strip()
    if win_host:
        try:
            config = DatabaseConfig(
                db_type="firebird",
                os_type="windows",
                name="Windows",
                host=win_host,
                port=int(os.getenv("WIN_FB_PORT", "3050")),
                database=os.getenv("WIN_FB_DATABASE", "").strip(),
                user=os.getenv("WIN_FB_USER", "").strip(),
                password=os.getenv("WIN_FB_PASSWORD", "").strip(),
                charset="UTF8",
            )
            configs.append(config)
        except (ValueError, TypeError) as e:
            print(f"⚠️  Aviso: Configuração Windows Firebird inválida: {e}")
    
    # Linux Firebird
    lin_host = os.getenv("LIN_FB_HOST", "").strip()
    if lin_host:
        try:
            config = DatabaseConfig(
                db_type="firebird",
                os_type="linux",
                name="Linux",
                host=lin_host,
                port=int(os.getenv("LIN_FB_PORT", "3050")),
                database=os.getenv("LIN_FB_DATABASE", "").strip(),
                user=os.getenv("LIN_FB_USER", "").strip(),
                password=os.getenv("LIN_FB_PASSWORD", "").strip(),
                charset="UTF8",
            )
            configs.append(config)
        except (ValueError, TypeError) as e:
            print(f"⚠️  Aviso: Configuração Linux Firebird inválida: {e}")
    
    return configs


def get_benchmark_params() -> Dict[str, any]:
    """
    Get benchmark parameters from environment variables.
    
    Returns:
        Dictionary with 'runs', 'query', 'concurrent', and 'max_workers' keys
    """
    load_dotenv()
    
    # Parse concurrent setting
    concurrent_val = os.getenv("FB_BENCH_CONCURRENT", "0").strip()
    try:
        max_workers = int(concurrent_val)
        concurrent = max_workers > 0
    except ValueError:
        concurrent = False
        max_workers = 10
    
    return {
        'runs': int(os.getenv("FB_BENCH_RUNS", "20")),
        'query': os.getenv("FB_BENCH_QUERY", "SELECT 1"),
        'concurrent': concurrent,
        'max_workers': max_workers if concurrent else 10,
    }


def get_server_specific_query(server_index: int) -> Optional[str]:
    """
    Get server-specific query override.
    
    Args:
        server_index: Server number (1-based)
    
    Returns:
        Query string if defined, None otherwise
    """
    return os.getenv(f"SERVER{server_index}_QUERY", None)
