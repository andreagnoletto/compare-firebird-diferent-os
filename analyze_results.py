#!/usr/bin/env python3
"""
Análise Estatística de Resultados do Benchmark Firebird

Este script implementa metodologia científica para análise de performance,
incluindo:
- Testes de normalidade (Shapiro-Wilk)
- Testes de significância estatística (t-test ou Mann-Whitney U)
- Cálculo de intervalo de confiança (95%)
- Análise de outliers
- Tamanho do efeito (Cohen's d)

Referências:
- Shapiro, S. S., & Wilk, M. B. (1965). An analysis of variance test for normality
- Student (1908). The probable error of a mean
- Mann, H. B., & Whitney, D. R. (1947). On a test of whether one of two random 
  variables is stochastically larger than the other
- Cohen, J. (1988). Statistical power analysis for the behavioral sciences
"""

import sys
from pathlib import Path
from typing import Tuple, Optional
import math

# Verificar se pandas e scipy estão instalados
try:
    import pandas as pd
    import statistics
    from scipy import stats
    import numpy as np
except ImportError as e:
    print("Este script requer pandas, scipy e numpy. Instale com:")
    print("  uv pip install pandas scipy numpy")
    print("  ou")
    print("  pip install pandas scipy numpy")
    sys.exit(1)


def calculate_cohens_d(group1: pd.Series, group2: pd.Series) -> float:
    """
    Calcula Cohen's d para medir o tamanho do efeito.
    
    Cohen's d = (mean1 - mean2) / pooled_std
    
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
    
    Retorna: (estatística, p-valor, é_normal)
    H0: Os dados seguem distribuição normal
    Se p > 0.05, não rejeitamos H0 (dados são normais)
    
    Shapiro & Wilk (1965)
    """
    if len(data) < 3:
        return 0, 0, False
    stat, p = stats.shapiro(data)
    return stat, p, p > 0.05


def statistical_test(group1: pd.Series, group2: pd.Series) -> Tuple[str, float, float, bool]:
    """
    Realiza teste estatístico apropriado.
    
    Se ambos grupos são normais: t-test independente (Student, 1908)
    Caso contrário: Mann-Whitney U test (Mann & Whitney, 1947)
    
    Retorna: (nome_teste, estatística, p-valor, há_diferença_significativa)
    """
    _, _, normal1 = test_normality(group1)
    _, _, normal2 = test_normality(group2)
    
    if normal1 and normal2:
        # t-test para amostras independentes
        stat, p = stats.ttest_ind(group1, group2)
        test_name = "t-test (Student, 1908)"
    else:
        # Mann-Whitney U test (não-paramétrico)
        stat, p = stats.mannwhitneyu(group1, group2, alternative='two-sided')
        test_name = "Mann-Whitney U (1947)"
    
    return test_name, stat, p, p < 0.05


def confidence_interval(data: pd.Series, confidence: float = 0.95) -> Tuple[float, float]:
    """
    Calcula intervalo de confiança para a média.
    
    Usa distribuição t de Student para amostras pequenas.
    """
    n = len(data)
    if n < 2:
        return data.mean(), data.mean()
    
    mean = data.mean()
    se = stats.sem(data)
    margin = se * stats.t.ppf((1 + confidence) / 2, n - 1)
    return mean - margin, mean + margin


def detect_outliers(data: pd.Series) -> Tuple[pd.Series, int]:
    """
    Detecta outliers usando método IQR (Tukey, 1977).
    
    Outliers: valores fora de [Q1 - 1.5*IQR, Q3 + 1.5*IQR]
    """
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = data[(data < lower_bound) | (data > upper_bound)]
    return outliers, len(outliers)


def analyze_results(csv_file: str = "firebird_benchmark_results.csv"):
    """Analisa o arquivo CSV de resultados do benchmark com metodologia científica"""
    
    csv_path = Path(csv_file)
    if not csv_path.exists():
        print(f"❌ Arquivo não encontrado: {csv_file}")
        print("Execute o benchmark primeiro:")
        print("  ./run-benchmark.sh")
        return
    
    # Ler CSV
    df = pd.read_csv(csv_path, sep=';')
    
    print("=" * 70)
    print("📊 ANÁLISE ESTATÍSTICA DE RESULTADOS - BENCHMARK FIREBIRD")
    print("Metodologia Científica com Testes de Significância")
    print("=" * 70)
    print()
    
    # Informações gerais
    print(f"📁 Arquivo: {csv_file}")
    print(f"📈 Total de execuções: {len(df)}")
    print(f"🖥️  Servidores testados: {df['server'].unique().tolist()}")
    print(f"🔍 Query executada: {df['query'].iloc[0]}")
    print(f"🔄 Execuções por servidor: {df['runs'].iloc[0]}")
    print()
    
    # Mostrar colunas disponíveis
    has_latency = 'latency_seconds' in df.columns
    has_server_time = 'elapsed_server_seconds' in df.columns
    has_stats = 'seq_reads' in df.columns
    
    if has_latency:
        print("✅ Dados de latência disponíveis")
    if has_server_time:
        print("✅ Tempo interno do servidor disponível")
    if has_stats:
        print("✅ Estatísticas de I/O disponíveis")
    print()
    
    # Estatísticas por servidor
    print("=" * 70)
    print("📊 ESTATÍSTICAS DESCRITIVAS POR SERVIDOR")
    print("=" * 70)
    print()
    
    for server in df['server'].unique():
        server_df = df[df['server'] == server]
        total_times = server_df['elapsed_total_seconds']
        
        # Detectar outliers
        outliers_total, n_outliers_total = detect_outliers(total_times)
        
        # Calcular intervalo de confiança
        ci_lower, ci_upper = confidence_interval(total_times)
        
        # Testar normalidade
        _, p_shapiro, is_normal = test_normality(total_times)
        
        print(f"🖥️  {server}")
        print(f"   Tempo Total (com rede):")
        print(f"      Média:        {total_times.mean():.6f} s")
        print(f"      IC 95%:       [{ci_lower:.6f}, {ci_upper:.6f}] s")
        print(f"      Mediana:      {total_times.median():.6f} s")
        print(f"      Mínimo:       {total_times.min():.6f} s")
        print(f"      Máximo:       {total_times.max():.6f} s")
        print(f"      Desvio Padrão: {total_times.std():.6f} s")
        print(f"      Coef. Variação: {(total_times.std() / total_times.mean() * 100):.2f}%")
        print(f"      Outliers:     {n_outliers_total} detectados (Tukey, 1977)")
        print(f"      Normalidade:  {'Normal' if is_normal else 'Não-normal'} (Shapiro-Wilk p={p_shapiro:.4f})")
        
        # Tempo do servidor (se disponível)
        if has_server_time and 'elapsed_server_seconds' in server_df.columns:
            server_times = server_df['elapsed_server_seconds'].replace('', pd.NA).dropna()
            if len(server_times) > 0:
                server_times = pd.to_numeric(server_times, errors='coerce').dropna()
                if len(server_times) > 0:
                    ci_srv_lower, ci_srv_upper = confidence_interval(server_times)
                    _, p_srv, is_normal_srv = test_normality(server_times)
                    outliers_srv, n_outliers_srv = detect_outliers(server_times)
                    
                    print(f"   Tempo Servidor (processamento interno):")
                    print(f"      Média:        {server_times.mean():.6f} s")
                    print(f"      IC 95%:       [{ci_srv_lower:.6f}, {ci_srv_upper:.6f}] s")
                    print(f"      Mediana:      {server_times.median():.6f} s")
                    print(f"      Mínimo:       {server_times.min():.6f} s")
                    print(f"      Máximo:       {server_times.max():.6f} s")
                    print(f"      Desvio Padrão: {server_times.std():.6f} s")
                    print(f"      Outliers:     {n_outliers_srv} detectados")
                    print(f"      Normalidade:  {'Normal' if is_normal_srv else 'Não-normal'} (p={p_srv:.4f})")
        
        # Latência (se disponível)
        if has_latency and 'latency_seconds' in server_df.columns:
            latencies = server_df['latency_seconds'].replace('', pd.NA).dropna()
            if len(latencies) > 0:
                latencies = pd.to_numeric(latencies, errors='coerce').dropna()
                if len(latencies) > 0:
                    print(f"   Latência de Rede:")
                    print(f"      Média:        {latencies.mean():.6f} s")
                    print(f"      Mediana:      {latencies.median():.6f} s")
                    print(f"      Mínimo:       {latencies.min():.6f} s")
                    print(f"      Máximo:       {latencies.max():.6f} s")
        
        # Estatísticas de I/O (se disponíveis)
        if has_stats:
            print(f"   Estatísticas de I/O (média):")
            for col in ['seq_reads', 'idx_reads', 'inserts', 'updates', 'deletes']:
                if col in server_df.columns:
                    values = server_df[col].replace('', pd.NA).dropna()
                    if len(values) > 0:
                        values = pd.to_numeric(values, errors='coerce').dropna()
                        if len(values) > 0 and values.sum() > 0:
                            print(f"      {col}: {values.mean():.2f}")
        print()
    
    # Comparação direta com testes estatísticos
    print("=" * 70)
    print("⚖️  COMPARAÇÃO ESTATÍSTICA ENTRE SERVIDORES")
    print("=" * 70)
    print()
    
    servers = df['server'].unique()
    if len(servers) == 2:
        server1_df = df[df['server'] == servers[0]]
        server2_df = df[df['server'] == servers[1]]
        
        # Comparação de tempo total
        server1_total = server1_df['elapsed_total_seconds']
        server2_total = server2_df['elapsed_total_seconds']
        
        mean1_total = server1_total.mean()
        mean2_total = server2_total.mean()
        
        diff_total = abs(mean1_total - mean2_total)
        pct_diff_total = (diff_total / min(mean1_total, mean2_total)) * 100
        
        faster_total = servers[0] if mean1_total < mean2_total else servers[1]
        slower_total = servers[1] if faster_total == servers[0] else servers[0]
        
        # Teste estatístico
        test_name_total, stat_total, p_total, is_sig_total = statistical_test(server1_total, server2_total)
        cohens_d_total = calculate_cohens_d(server1_total, server2_total)
        effect_size_total = interpret_cohens_d(cohens_d_total)
        
        print("📊 TEMPO TOTAL (com rede e latência):")
        print(f"   🏆 Mais rápido: {faster_total} - {min(mean1_total, mean2_total):.6f} s")
        print(f"   🐌 Mais lento:  {slower_total} - {max(mean1_total, mean2_total):.6f} s")
        print(f"   📊 Diferença:   {diff_total:.6f} s ({pct_diff_total:.2f}%)")
        print(f"   📈 Teste:       {test_name_total}")
        print(f"   📊 p-valor:     {p_total:.6f} {'(significativo)' if is_sig_total else '(não significativo)'}")
        print(f"   📏 Cohen's d:   {cohens_d_total:.4f} (efeito {effect_size_total})")
        print()
        
        # Comparação de tempo do servidor (se disponível)
        if has_server_time:
            server1_srv = pd.to_numeric(server1_df['elapsed_server_seconds'].replace('', pd.NA), errors='coerce').dropna()
            server2_srv = pd.to_numeric(server2_df['elapsed_server_seconds'].replace('', pd.NA), errors='coerce').dropna()
            
            if len(server1_srv) > 0 and len(server2_srv) > 0:
                mean1_srv = server1_srv.mean()
                mean2_srv = server2_srv.mean()
                
                diff_srv = abs(mean1_srv - mean2_srv)
                pct_diff_srv = (diff_srv / min(mean1_srv, mean2_srv)) * 100
                
                faster_srv = servers[0] if mean1_srv < mean2_srv else servers[1]
                slower_srv = servers[1] if faster_srv == servers[0] else servers[0]
                
                # Teste estatístico
                test_name_srv, stat_srv, p_srv, is_sig_srv = statistical_test(server1_srv, server2_srv)
                cohens_d_srv = calculate_cohens_d(server1_srv, server2_srv)
                effect_size_srv = interpret_cohens_d(cohens_d_srv)
                
                print("🔧 TEMPO DO SERVIDOR (processamento interno do Firebird):")
                print(f"   🏆 Mais rápido: {faster_srv} - {min(mean1_srv, mean2_srv):.6f} s")
                print(f"   🐌 Mais lento:  {slower_srv} - {max(mean1_srv, mean2_srv):.6f} s")
                print(f"   📊 Diferença:   {diff_srv:.6f} s ({pct_diff_srv:.2f}%)")
                print(f"   📈 Teste:       {test_name_srv}")
                print(f"   📊 p-valor:     {p_srv:.6f} {'(significativo α=0.05)' if is_sig_srv else '(não significativo α=0.05)'}")
                print(f"   📏 Cohen's d:   {cohens_d_srv:.4f} (efeito {effect_size_srv})")
                print()
        
        # Comparação de latência (se disponível)
        if has_latency:
            server1_lat = pd.to_numeric(server1_df['latency_seconds'].replace('', pd.NA), errors='coerce').dropna()
            server2_lat = pd.to_numeric(server2_df['latency_seconds'].replace('', pd.NA), errors='coerce').dropna()
            
            if len(server1_lat) > 0 and len(server2_lat) > 0:
                mean1_lat = server1_lat.mean()
                mean2_lat = server2_lat.mean()
                
                diff_lat = abs(mean1_lat - mean2_lat)
                
                lower_lat = servers[0] if mean1_lat < mean2_lat else servers[1]
                higher_lat = servers[1] if lower_lat == servers[0] else servers[0]
                
                # Teste estatístico
                test_name_lat, stat_lat, p_lat, is_sig_lat = statistical_test(server1_lat, server2_lat)
                cohens_d_lat = calculate_cohens_d(server1_lat, server2_lat)
                effect_size_lat = interpret_cohens_d(cohens_d_lat)
                
                print("🌐 LATÊNCIA DE REDE:")
                print(f"   🏆 Menor latência: {lower_lat} - {min(mean1_lat, mean2_lat):.6f} s")
                print(f"   📡 Maior latência: {higher_lat} - {max(mean1_lat, mean2_lat):.6f} s")
                print(f"   📊 Diferença:      {diff_lat:.6f} s")
                print(f"   📈 Teste:          {test_name_lat}")
                print(f"   📊 p-valor:        {p_lat:.6f} {'(significativo)' if is_sig_lat else '(não significativo)'}")
                print(f"   📏 Cohen's d:      {cohens_d_lat:.4f} (efeito {effect_size_lat})")
                print()
        
        # Interpretação científica
        print("=" * 70)
        print("🔬 INTERPRETAÇÃO CIENTÍFICA DOS RESULTADOS")
        print("=" * 70)
        print()
        
        if has_server_time and len(server1_srv) > 0 and len(server2_srv) > 0:
            print(f"📊 Significância Estatística (α = 0.05):")
            if is_sig_srv:
                print(f"   ✅ A diferença no tempo de processamento do servidor é")
                print(f"      ESTATISTICAMENTE SIGNIFICATIVA (p = {p_srv:.6f})")
                print(f"   ✅ Podemos rejeitar a hipótese nula (H0: μ₁ = μ₂)")
                print(f"   ✅ Conclusão: {faster_srv} é REALMENTE mais rápido que {slower_srv}")
            else:
                print(f"   ⚠️  A diferença no tempo de processamento do servidor")
                print(f"      NÃO É ESTATISTICAMENTE SIGNIFICATIVA (p = {p_srv:.6f})")
                print(f"   ⚠️  Não podemos rejeitar a hipótese nula (H0: μ₁ = μ₂)")
                print(f"   ⚠️  Conclusão: A diferença observada pode ser devido ao acaso")
            print()
            
            print(f"📏 Tamanho do Efeito (Cohen's d = {cohens_d_srv:.4f}):")
            if abs(cohens_d_srv) < 0.2:
                print(f"   → Efeito INSIGNIFICANTE (Cohen, 1988)")
                print(f"   → Diferença muito pequena, sem relevância prática")
            elif abs(cohens_d_srv) < 0.5:
                print(f"   → Efeito PEQUENO (Cohen, 1988)")
                print(f"   → Diferença detectável mas de impacto limitado")
            elif abs(cohens_d_srv) < 0.8:
                print(f"   → Efeito MÉDIO (Cohen, 1988)")
                print(f"   → Diferença substancial com relevância prática")
            else:
                print(f"   → Efeito GRANDE (Cohen, 1988)")
                print(f"   → Diferença muito substancial, altamente relevante")
            print()
            
            print(f"🎯 Recomendação:")
            if is_sig_srv and abs(cohens_d_srv) >= 0.5:
                print(f"   ✅ A diferença é tanto estatisticamente significativa quanto")
                print(f"      praticamente relevante. {faster_srv} apresenta performance")
                print(f"      superior com {pct_diff_srv:.1f}% de vantagem.")
                print(f"   ✅ Recomenda-se {faster_srv} para ambientes de produção.")
            elif is_sig_srv and abs(cohens_d_srv) < 0.5:
                print(f"   ⚠️  Embora estatisticamente significativa, a diferença")
                print(f"      ({pct_diff_srv:.1f}%) tem efeito {effect_size_srv}.")
                print(f"   ⚠️  Considere outros fatores (custo, manutenção, expertise)")
                print(f"      além da performance pura.")
            else:
                print(f"   ℹ️  A diferença observada ({pct_diff_srv:.1f}%) não é")
                print(f"      estatisticamente significativa.")
                print(f"   ℹ️  Ambos os servidores têm performance equivalente.")
                print(f"   ℹ️  Escolha pode ser baseada em outros critérios.")
        
        print()
        print("📚 REFERÊNCIAS METODOLÓGICAS:")
        print("   • Shapiro, S.S. & Wilk, M.B. (1965). An analysis of variance")
        print("     test for normality (complete samples)")
        print("   • Student (1908). The probable error of a mean")
        print("   • Mann, H.B. & Whitney, D.R. (1947). On a test of whether")
        print("     one of two random variables is stochastically larger")
        print("   • Cohen, J. (1988). Statistical power analysis for the")
        print("     behavioral sciences (2nd ed.)")
        print("   • Tukey, J.W. (1977). Exploratory Data Analysis")
        print()
                higher_lat = servers[1] if lower_lat == servers[0] else servers[0]
                
                print("🌐 LATÊNCIA DE REDE:")
                print(f"   🏆 Menor latência: {lower_lat} - {min(mean1_lat, mean2_lat):.6f} s")
                print(f"   📡 Maior latência: {higher_lat} - {max(mean1_lat, mean2_lat):.6f} s")
                print(f"   📊 Diferença:      {diff_lat:.6f} s")
                print()
        
        # Interpretação
        print("🔍 INTERPRETAÇÃO:")
        if has_server_time and len(server1_srv) > 0 and len(server2_srv) > 0:
            if pct_diff_srv < 5:
                print("   ✅ Performance do banco similar entre servidores (< 5%)")
            elif pct_diff_srv < 15:
                print("   ⚠️  Diferença moderada de performance do banco (5-15%)")
            else:
                print(f"   🔴 Diferença significativa! {faster_srv} processa {pct_diff_srv:.1f}% mais rápido")
        
        if pct_diff_total < 5:
            print("   ✅ Performance total similar (< 5%)")
        elif pct_diff_total < 15:
            print("   ⚠️  Diferença moderada na experiência do usuário (5-15%)")
        else:
            print(f"   🔴 {faster_total} oferece experiência {pct_diff_total:.1f}% mais rápida")
    
    print()
    
    # Tabela de estatísticas descritivas
    print("=" * 70)
    print("📋 TABELA DE ESTATÍSTICAS DESCRITIVAS")
    print("=" * 70)
    print()
    print("Tempo Total:")
    print(df.groupby('server')['elapsed_total_seconds'].describe())
    print()
    
    if has_server_time:
        server_times_df = df[['server', 'elapsed_server_seconds']].copy()
        server_times_df['elapsed_server_seconds'] = pd.to_numeric(
            server_times_df['elapsed_server_seconds'].replace('', pd.NA), 
            errors='coerce'
        )
        server_times_df = server_times_df.dropna()
        if len(server_times_df) > 0:
            print("Tempo do Servidor:")
            print(server_times_df.groupby('server')['elapsed_server_seconds'].describe())
            print()
    
    if has_latency:
        latency_df = df[['server', 'latency_seconds']].copy()
        latency_df['latency_seconds'] = pd.to_numeric(
            latency_df['latency_seconds'].replace('', pd.NA), 
            errors='coerce'
        )
        latency_df = latency_df.dropna()
        if len(latency_df) > 0:
            print("Latência:")
            print(latency_df.groupby('server')['latency_seconds'].describe())
            print()
    
    # Sugestão de visualização
    print("=" * 70)
    print("📈 DICAS DE VISUALIZAÇÃO")
    print("=" * 70)
    print()
    print("Para visualizar graficamente, você pode:")
    print()
    print("1. Importar em Excel/LibreOffice e criar gráficos")
    print()
    print("2. Usar Python com matplotlib:")
    print("   ```python")
    print("   import pandas as pd")
    print("   import matplotlib.pyplot as plt")
    print()
    print("   df = pd.read_csv('firebird_benchmark_results.csv', sep=';')")
    print("   ")
    print("   # Comparar tempos totais")
    print("   df.boxplot(by='server', column='elapsed_total_seconds')")
    print("   plt.ylabel('Tempo Total (segundos)')")
    print("   plt.title('Comparação de Performance - Tempo Total')")
    print("   plt.suptitle('')")
    print("   plt.show()")
    print("   ")
    print("   # Comparar tempos do servidor (sem rede)")
    print("   df_srv = df[df['elapsed_server_seconds'] != ''].copy()")
    print("   df_srv['elapsed_server_seconds'] = pd.to_numeric(df_srv['elapsed_server_seconds'])")
    print("   df_srv.boxplot(by='server', column='elapsed_server_seconds')")
    print("   plt.ylabel('Tempo Servidor (segundos)')")
    print("   plt.title('Comparação - Processamento Interno Firebird')")
    print("   plt.suptitle('')")
    print("   plt.show()")
    print("   ```")
    print()
    print("3. Usar ferramentas online como:")
    print("   - Google Sheets")
    print("   - Plotly Chart Studio")
    print()


if __name__ == "__main__":
    # Aceitar caminho do CSV como argumento
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "firebird_benchmark_results.csv"
    analyze_results(csv_file)
