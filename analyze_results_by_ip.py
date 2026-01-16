#!/usr/bin/env python3
"""
Análise Estatística de Resultados do Benchmark - Por IP/Servidor

Este script implementa metodologia científica para análise de performance
com foco em comparação por IP/servidor (não por plataforma/OS).

Metodologia:
- Testes de normalidade (Shapiro-Wilk)
- Testes de significância estatística (t-test ou Mann-Whitney U)
- Cálculo de intervalo de confiança (95%)
- Análise de outliers (Tukey IQR)
- Tamanho do efeito (Cohen's d)
- Comparações pareadas entre todos os servidores

Referências:
- Shapiro, S. S., & Wilk, M. B. (1965). An analysis of variance test for normality
- Student (1908). The probable error of a mean
- Mann, H. B., & Whitney, D. R. (1947). On a test of whether one of two random 
  variables is stochastically larger than the other
- Cohen, J. (1988). Statistical power analysis for the behavioral sciences
"""

import sys
from pathlib import Path
from typing import Tuple, List, Dict, Any
from itertools import combinations
import math

# Verificar dependências
try:
    import pandas as pd
    import statistics
    from scipy import stats
    import numpy as np
except ImportError as e:
    print("Este script requer pandas, scipy e numpy. Instale com:")
    print("  uv pip install pandas scipy numpy")
    sys.exit(1)


def calculate_cohens_d(group1: pd.Series, group2: pd.Series) -> float:
    """
    Calcula Cohen's d para medir o tamanho do efeito.
    
    Interpretação (Cohen, 1988):
    - |d| < 0.2: efeito insignificante
    - 0.2 ≤ |d| < 0.5: efeito pequeno
    - 0.5 ≤ |d| < 0.8: efeito médio
    - |d| ≥ 0.8: efeito grande
    """
    n1, n2 = len(group1), len(group2)
    var1, var2 = group1.var(), group2.var()
    pooled_std = math.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    return (group1.mean() - group2.mean()) / pooled_std if pooled_std > 0 else 0


def interpret_cohens_d(d: float) -> str:
    """Interpreta o tamanho do efeito segundo Cohen (1988)"""
    abs_d = abs(d)
    if abs_d < 0.2:
        return "insignificante"
    elif abs_d < 0.5:
        return "pequeno"
    elif abs_d < 0.8:
        return "médio"
    else:
        return "grande"


def test_normality(data: pd.Series) -> Tuple[float, float, bool]:
    """
    Testa normalidade usando Shapiro-Wilk.
    
    H0: Os dados seguem distribuição normal
    Se p > 0.05, não rejeitamos H0 (dados são normais)
    """
    if len(data) < 3:
        return 0, 0, False
    # Shapiro-Wilk tem limite de 5000 amostras
    sample = data.sample(min(5000, len(data)), random_state=42) if len(data) > 5000 else data
    stat, p = stats.shapiro(sample)
    return stat, p, p > 0.05


def statistical_test(group1: pd.Series, group2: pd.Series) -> Tuple[str, float, float, bool]:
    """
    Realiza teste estatístico apropriado.
    
    Se ambos grupos são normais: t-test independente
    Caso contrário: Mann-Whitney U test
    """
    _, _, normal1 = test_normality(group1)
    _, _, normal2 = test_normality(group2)
    
    if normal1 and normal2:
        stat, p = stats.ttest_ind(group1, group2)
        test_name = "t-test (Student, 1908)"
    else:
        stat, p = stats.mannwhitneyu(group1, group2, alternative='two-sided')
        test_name = "Mann-Whitney U (1947)"
    
    return test_name, stat, p, p < 0.05


def confidence_interval(data: pd.Series, confidence: float = 0.95) -> Tuple[float, float]:
    """Calcula intervalo de confiança para a média."""
    n = len(data)
    if n < 2:
        return data.mean(), data.mean()
    
    mean = data.mean()
    se = stats.sem(data)
    margin = se * stats.t.ppf((1 + confidence) / 2, n - 1)
    return mean - margin, mean + margin


def detect_outliers(data: pd.Series) -> Tuple[pd.Series, int]:
    """Detecta outliers usando método IQR (Tukey, 1977)."""
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = data[(data < lower_bound) | (data > upper_bound)]
    return outliers, len(outliers)


def analyze_results_by_ip(csv_file: str = "benchmark_results.csv"):
    """Analisa resultados com foco em comparação por IP/servidor."""
    
    csv_path = Path(csv_file)
    if not csv_path.exists():
        print(f"❌ Arquivo não encontrado: {csv_file}")
        print("Execute o benchmark primeiro:")
        print("  uv run python -m src.compare_firebird_diferent_os.main_new")
        return
    
    # Ler CSV
    df = pd.read_csv(csv_path, sep=';')
    
    print("=" * 80)
    print("📊 ANÁLISE ESTATÍSTICA DE BENCHMARK - COMPARAÇÃO POR IP/SERVIDOR")
    print("   Metodologia Científica com Testes de Significância")
    print("=" * 80)
    print()
    
    # Informações gerais
    print(f"📁 Arquivo: {csv_file}")
    print(f"📈 Total de execuções: {len(df)}")
    
    # Usar server_name como identificador (coluna correta do CSV)
    server_col = 'server_name' if 'server_name' in df.columns else 'server'
    
    # Extrair IPs únicos
    servers = df[server_col].unique()
    print(f"🖥️  Servidores testados ({len(servers)} IPs):")
    for s in servers:
        count = len(df[df[server_col] == s])
        print(f"      • {s}: {count} execuções")
    print()
    
    # Verificar colunas disponíveis
    has_latency = 'latency_seconds' in df.columns
    has_server_time = 'elapsed_server_seconds' in df.columns
    
    # ========== ESTATÍSTICAS DESCRITIVAS POR IP ==========
    print("=" * 80)
    print("📊 ESTATÍSTICAS DESCRITIVAS POR IP")
    print("=" * 80)
    print()
    
    server_stats = []
    
    for server in servers:
        server_df = df[df[server_col] == server]
        total_times = server_df['elapsed_total_seconds']
        
        # Calcular estatísticas
        outliers, n_outliers = detect_outliers(total_times)
        ci_lower, ci_upper = confidence_interval(total_times)
        _, p_shapiro, is_normal = test_normality(total_times)
        
        stats_dict = {
            'server': server,
            'n': len(total_times),
            'mean': total_times.mean(),
            'median': total_times.median(),
            'std': total_times.std(),
            'min': total_times.min(),
            'max': total_times.max(),
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'cv': (total_times.std() / total_times.mean() * 100),
            'outliers': n_outliers,
            'is_normal': is_normal,
            'p_shapiro': p_shapiro,
            'data': total_times
        }
        server_stats.append(stats_dict)
        
        print(f"🖥️  IP: {server}")
        print(f"   ├─ Execuções:    {stats_dict['n']}")
        print(f"   ├─ Média:        {stats_dict['mean']*1000:.2f} ms")
        print(f"   ├─ IC 95%:       [{ci_lower*1000:.2f}, {ci_upper*1000:.2f}] ms")
        print(f"   ├─ Mediana:      {stats_dict['median']*1000:.2f} ms")
        print(f"   ├─ Mínimo:       {stats_dict['min']*1000:.2f} ms")
        print(f"   ├─ Máximo:       {stats_dict['max']*1000:.2f} ms")
        print(f"   ├─ Desvio:       {stats_dict['std']*1000:.2f} ms")
        print(f"   ├─ CV:           {stats_dict['cv']:.1f}%")
        print(f"   ├─ Outliers:     {n_outliers}")
        print(f"   └─ Normalidade:  {'Normal' if is_normal else 'Não-normal'} (p={p_shapiro:.4f})")
        print()
    
    # Ordenar por média (mais rápido primeiro)
    server_stats.sort(key=lambda x: x['mean'])
    
    # ========== RANKING DE PERFORMANCE ==========
    print("=" * 80)
    print("🏆 RANKING DE PERFORMANCE (por tempo médio)")
    print("=" * 80)
    print()
    
    medals = ["🥇", "🥈", "🥉"] + [f"#{i}" for i in range(4, 11)]
    
    for i, stat in enumerate(server_stats):
        medal = medals[i] if i < len(medals) else f"#{i+1}"
        diff_vs_best = ""
        if i > 0:
            pct = ((stat['mean'] - server_stats[0]['mean']) / server_stats[0]['mean']) * 100
            diff_vs_best = f" (+{pct:.1f}% vs melhor)"
        
        print(f"   {medal} {stat['server']}: {stat['mean']*1000:.2f} ms{diff_vs_best}")
    
    print()
    
    # ========== COMPARAÇÕES PAREADAS ==========
    print("=" * 80)
    print("⚖️  COMPARAÇÕES PAREADAS ENTRE IPs")
    print("=" * 80)
    print()
    
    comparisons = []
    
    for (s1, s2) in combinations(servers, 2):
        data1 = df[df[server_col] == s1]['elapsed_total_seconds']
        data2 = df[df[server_col] == s2]['elapsed_total_seconds']
        
        mean1, mean2 = data1.mean(), data2.mean()
        diff = abs(mean1 - mean2)
        pct_diff = (diff / min(mean1, mean2)) * 100
        
        faster = s1 if mean1 < mean2 else s2
        slower = s2 if faster == s1 else s1
        
        test_name, stat, p_value, is_sig = statistical_test(data1, data2)
        cohens_d = calculate_cohens_d(data1, data2)
        effect_size = interpret_cohens_d(cohens_d)
        
        comp = {
            'server1': s1,
            'server2': s2,
            'faster': faster,
            'slower': slower,
            'mean1_ms': mean1 * 1000,
            'mean2_ms': mean2 * 1000,
            'diff_ms': diff * 1000,
            'pct_diff': pct_diff,
            'test_name': test_name,
            'p_value': p_value,
            'is_significant': is_sig,
            'cohens_d': cohens_d,
            'effect_size': effect_size
        }
        comparisons.append(comp)
        
        sig_icon = "✅" if is_sig else "⚠️"
        
        print(f"📌 {s1} vs {s2}")
        print(f"   ├─ Mais rápido: {faster} ({min(mean1, mean2)*1000:.2f} ms)")
        print(f"   ├─ Mais lento:  {slower} ({max(mean1, mean2)*1000:.2f} ms)")
        print(f"   ├─ Diferença:   {diff*1000:.2f} ms ({pct_diff:.1f}%)")
        print(f"   ├─ Teste:       {test_name}")
        print(f"   ├─ p-valor:     {p_value:.6f} {sig_icon}")
        print(f"   └─ Cohen's d:   {abs(cohens_d):.4f} (efeito {effect_size})")
        print()
    
    # ========== MATRIZ DE COMPARAÇÃO ==========
    print("=" * 80)
    print("📋 MATRIZ DE COMPARAÇÃO (% diferença)")
    print("=" * 80)
    print()
    
    # Criar matriz
    col_width = max(15, max(len(s) for s in servers) + 2)
    
    # Cabeçalho
    header = "IP".ljust(col_width) + " │ "
    header += " │ ".join(s[-col_width+2:].center(col_width-2) for s in servers)
    print(header)
    print("─" * len(header))
    
    for s1 in servers:
        row = s1[-col_width:].ljust(col_width) + " │ "
        cells = []
        for s2 in servers:
            if s1 == s2:
                cells.append("-".center(col_width-2))
            else:
                m1 = df[df[server_col] == s1]['elapsed_total_seconds'].mean()
                m2 = df[df[server_col] == s2]['elapsed_total_seconds'].mean()
                if m1 < m2:
                    pct = ((m2 - m1) / m1) * 100
                    cells.append(f"+{pct:.1f}%".center(col_width-2))
                else:
                    pct = ((m1 - m2) / m2) * 100
                    cells.append(f"-{pct:.1f}%".center(col_width-2))
        row += " │ ".join(cells)
        print(row)
    
    print()
    print("   Legenda: +X% = linha é X% mais RÁPIDA que coluna")
    print("            -X% = linha é X% mais LENTA que coluna")
    print()
    
    # ========== INTERPRETAÇÃO CIENTÍFICA ==========
    print("=" * 80)
    print("🔬 INTERPRETAÇÃO CIENTÍFICA DOS RESULTADOS")
    print("=" * 80)
    print()
    
    best = server_stats[0]
    worst = server_stats[-1]
    
    # Comparação melhor vs pior
    best_data = df[df[server_col] == best['server']]['elapsed_total_seconds']
    worst_data = df[df[server_col] == worst['server']]['elapsed_total_seconds']
    
    _, _, p_bw, is_sig_bw = statistical_test(best_data, worst_data)
    cohens_d_bw = calculate_cohens_d(best_data, worst_data)
    pct_diff_bw = ((worst['mean'] - best['mean']) / best['mean']) * 100
    
    print(f"📊 Análise: {best['server']} (melhor) vs {worst['server']} (pior)")
    print()
    
    if is_sig_bw:
        print(f"   ✅ DIFERENÇA ESTATISTICAMENTE SIGNIFICATIVA (p = {p_bw:.6f})")
        print(f"   ✅ {best['server']} é comprovadamente mais rápido")
    else:
        print(f"   ⚠️  Diferença NÃO é estatisticamente significativa (p = {p_bw:.6f})")
        print(f"   ⚠️  A diferença observada pode ser devido ao acaso")
    print()
    
    effect = interpret_cohens_d(cohens_d_bw)
    print(f"📏 Tamanho do Efeito: Cohen's d = {abs(cohens_d_bw):.4f} ({effect})")
    
    if abs(cohens_d_bw) < 0.2:
        print("   → Efeito INSIGNIFICANTE - diferença sem relevância prática")
    elif abs(cohens_d_bw) < 0.5:
        print("   → Efeito PEQUENO - diferença detectável mas limitada")
    elif abs(cohens_d_bw) < 0.8:
        print("   → Efeito MÉDIO - diferença substancial e relevante")
    else:
        print("   → Efeito GRANDE - diferença muito substancial")
    print()
    
    # ========== RECOMENDAÇÃO FINAL ==========
    print("=" * 80)
    print("🎯 RECOMENDAÇÃO FINAL")
    print("=" * 80)
    print()
    
    if is_sig_bw and abs(cohens_d_bw) >= 0.5:
        print(f"   ✅ RECOMENDADO: {best['server']}")
        print(f"   ")
        print(f"   Performance {pct_diff_bw:.1f}% superior ao servidor mais lento,")
        print(f"   com diferença estatisticamente significativa e efeito {effect}.")
        print()
        print(f"   Tempo médio: {best['mean']*1000:.2f} ms")
        print(f"   IC 95%: [{best['ci_lower']*1000:.2f}, {best['ci_upper']*1000:.2f}] ms")
    elif is_sig_bw:
        print(f"   ⚠️  {best['server']} tem a melhor performance média")
        print(f"   ")
        print(f"   Diferença de {pct_diff_bw:.1f}% é estatisticamente significativa,")
        print(f"   porém o efeito prático é {effect}.")
        print()
        print(f"   Considere também: custo, localização, manutenção.")
    else:
        print(f"   ℹ️  Performance equivalente entre servidores")
        print(f"   ")
        print(f"   A diferença de {pct_diff_bw:.1f}% não é estatisticamente significativa.")
        print(f"   Escolha baseada em outros critérios (custo, localização, etc.)")
    
    print()
    
    # ========== RESUMO DAS DIFERENÇAS SIGNIFICATIVAS ==========
    sig_comps = [c for c in comparisons if c['is_significant']]
    
    if sig_comps:
        print("📋 Diferenças Estatisticamente Significativas:")
        for c in sorted(sig_comps, key=lambda x: -x['pct_diff']):
            print(f"   • {c['faster']} > {c['slower']}: {c['pct_diff']:.1f}% mais rápido (p={c['p_value']:.4f}, d={abs(c['cohens_d']):.2f})")
    else:
        print("📋 Nenhuma diferença estatisticamente significativa entre os servidores.")
    print()
    
    # ========== TABELA RESUMO ==========
    print("=" * 80)
    print("📋 TABELA RESUMO (em milissegundos)")
    print("=" * 80)
    print()
    
    summary_df = pd.DataFrame([{
        'IP': s['server'],
        'Média (ms)': f"{s['mean']*1000:.2f}",
        'Mediana (ms)': f"{s['median']*1000:.2f}",
        'Desvio (ms)': f"{s['std']*1000:.2f}",
        'Min (ms)': f"{s['min']*1000:.2f}",
        'Max (ms)': f"{s['max']*1000:.2f}",
        'CV (%)': f"{s['cv']:.1f}"
    } for s in server_stats])
    
    print(summary_df.to_string(index=False))
    print()
    
    # ========== REFERÊNCIAS ==========
    print("=" * 80)
    print("📚 REFERÊNCIAS METODOLÓGICAS")
    print("=" * 80)
    print()
    print("   • Shapiro, S.S. & Wilk, M.B. (1965). An analysis of variance")
    print("     test for normality (complete samples)")
    print("   • Student (1908). The probable error of a mean")
    print("   • Mann, H.B. & Whitney, D.R. (1947). On a test of whether")
    print("     one of two random variables is stochastically larger")
    print("   • Cohen, J. (1988). Statistical power analysis for the")
    print("     behavioral sciences (2nd ed.)")
    print("   • Tukey, J.W. (1977). Exploratory Data Analysis")
    print()


if __name__ == "__main__":
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "benchmark_results.csv"
    analyze_results_by_ip(csv_file)
