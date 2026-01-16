"""
Extensões multi-database para análise de resultados.

Este módulo adiciona funcionalidades de agrupamento e comparação por db_type e os_type
mantendo toda a metodologia científica do análise original.
"""

import pandas as pd
from typing import List, Dict, Tuple, Optional


def group_by_database_and_os(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Agrupa resultados por tipo de banco e sistema operacional.
    
    Args:
        df: DataFrame com resultados do benchmark
    
    Returns:
        Dictionary mapeando grupos para DataFrames filtrados
    """
    groups = {}
    
    # Verificar se temos colunas multi-DB
    has_db_type = 'db_type' in df.columns
    has_os_type = 'os_type' in df.columns
    
    if not has_db_type:
        # Formato legado - apenas por server name
        for server in df['server_name'].unique() if 'server_name' in df.columns else df['server'].unique():
            groups[server] = df[df.get('server_name', df.get('server')) == server]
        return groups
    
    # Novos agrupamentos
    
    # 1. Por tipo de banco de dados
    for db_type in df['db_type'].unique():
        key = f"DB: {db_type.upper()}"
        groups[key] = df[df['db_type'] == db_type]
    
    # 2. Por sistema operacional
    if has_os_type:
        for os_type in df['os_type'].unique():
            key = f"OS: {os_type.upper()}"
            groups[key] = df[df['os_type'] == os_type]
    
    # 3. Por combinação db_type + os_type
    if has_os_type:
        for db_type in df['db_type'].unique():
            for os_type in df['os_type'].unique():
                subset = df[(df['db_type'] == db_type) & (df['os_type'] == os_type)]
                if len(subset) > 0:
                    key = f"{db_type.upper()} @ {os_type.upper()}"
                    groups[key] = subset
    
    return groups


def get_comparison_pairs(df: pd.DataFrame) -> List[Tuple[str, pd.DataFrame, pd.DataFrame]]:
    """
    Gera pares de comparação interessantes para análise estatística.
    
    Returns:
        Lista de tuplas (nome_comparação, grupo1_df, grupo2_df)
    """
    pairs = []
    
    has_db_type = 'db_type' in df.columns
    has_os_type = 'os_type' in df.columns
    
    if not has_db_type:
        # Formato legado - comparar servers únicos
        servers = df['server_name'].unique() if 'server_name' in df.columns else df['server'].unique()
        if len(servers) == 2:
            pairs.append((
                f"{servers[0]} vs {servers[1]}",
                df[df.get('server_name', df.get('server')) == servers[0]],
                df[df.get('server_name', df.get('server')) == servers[1]]
            ))
        return pairs
    
    # Comparações multi-DB
    
    # 1. Mesmo DB em OS diferentes
    if has_os_type:
        for db_type in df['db_type'].unique():
            os_types = df[df['db_type'] == db_type]['os_type'].unique()
            if len(os_types) == 2:
                os1, os2 = os_types[0], os_types[1]
                pairs.append((
                    f"{db_type.upper()}: {os1.upper()} vs {os2.upper()}",
                    df[(df['db_type'] == db_type) & (df['os_type'] == os1)],
                    df[(df['db_type'] == db_type) & (df['os_type'] == os2)]
                ))
    
    # 2. DBs diferentes no mesmo OS
    if has_os_type:
        for os_type in df['os_type'].unique():
            db_types = df[df['os_type'] == os_type]['db_type'].unique()
            for i in range(len(db_types)):
                for j in range(i + 1, len(db_types)):
                    db1, db2 = db_types[i], db_types[j]
                    pairs.append((
                        f"{os_type.upper()}: {db1.upper()} vs {db2.upper()}",
                        df[(df['db_type'] == db1) & (df['os_type'] == os_type)],
                        df[(df['db_type'] == db2) & (df['os_type'] == os_type)]
                    ))
    
    # 3. Comparação geral entre tipos de DB (agregando todos OS)
    db_types = df['db_type'].unique()
    if len(db_types) >= 2:
        for i in range(len(db_types)):
            for j in range(i + 1, len(db_types)):
                db1, db2 = db_types[i], db_types[j]
                pairs.append((
                    f"Overall: {db1.upper()} vs {db2.upper()}",
                    df[df['db_type'] == db1],
                    df[df['db_type'] == db2]
                ))
    
    return pairs


def print_cross_database_summary(df: pd.DataFrame):
    """Imprime resumo de análise cross-database."""
    
    has_db_type = 'db_type' in df.columns
    has_os_type = 'os_type' in df.columns
    
    if not has_db_type:
        print("ℹ️  Dados em formato legado (sem db_type/os_type)")
        return
    
    print("\n" + "=" * 70)
    print("🔍 RESUMO CROSS-DATABASE")
    print("=" * 70)
    print()
    
    # Contagem por DB type
    print("📊 Distribuição por tipo de banco de dados:")
    db_counts = df.groupby('db_type').size()
    for db_type, count in db_counts.items():
        servers = df[df['db_type'] == db_type]['server_name'].unique() if 'server_name' in df.columns else []
        print(f"   {db_type.upper()}: {count} execuções")
        if len(servers) > 0:
            print(f"      Servidores: {', '.join(servers)}")
    print()
    
    # Contagem por OS
    if has_os_type:
        print("💻 Distribuição por sistema operacional:")
        os_counts = df.groupby('os_type').size()
        for os_type, count in os_counts.items():
            print(f"   {os_type.upper()}: {count} execuções")
        print()
    
    # Matrix de combinações
    if has_os_type:
        print("🎯 Matriz DB x OS:")
        matrix = df.groupby(['db_type', 'os_type']).size().unstack(fill_value=0)
        print(matrix)
        print()
    
    # Performance rankings (média tempo total)
    print("🏆 Ranking de Performance (tempo médio total):")
    if 'server_name' in df.columns:
        ranking = df.groupby('server_name')['elapsed_total_seconds'].mean().sort_values()
    else:
        ranking = df.groupby(['db_type', 'os_type'])['elapsed_total_seconds'].mean().sort_values()
    
    for i, (name, time) in enumerate(ranking.items(), 1):
        if isinstance(name, tuple):
            display_name = f"{name[0].upper()} @ {name[1].upper()}"
        else:
            display_name = name
        print(f"   {i}. {display_name}: {time:.6f} s")
    print()
