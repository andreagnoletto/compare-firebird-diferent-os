#!/usr/bin/env python3
"""
Exemplo de análise dos resultados do benchmark
Este script demonstra como processar o CSV gerado pelo benchmark
"""

import sys
from pathlib import Path

# Verificar se pandas está instalado
try:
    import pandas as pd
    import statistics
except ImportError:
    print("Este script requer pandas. Instale com:")
    print("  pip install pandas")
    sys.exit(1)


def analyze_results(csv_file: str = "firebird_benchmark_results.csv"):
    """Analisa o arquivo CSV de resultados do benchmark"""
    
    csv_path = Path(csv_file)
    if not csv_path.exists():
        print(f"❌ Arquivo não encontrado: {csv_file}")
        print("Execute o benchmark primeiro:")
        print("  ./run-benchmark.sh")
        return
    
    # Ler CSV
    df = pd.read_csv(csv_path, sep=';')
    
    print("=" * 70)
    print("📊 ANÁLISE DE RESULTADOS DO BENCHMARK FIREBIRD")
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
    print("📊 ESTATÍSTICAS POR SERVIDOR")
    print("=" * 70)
    print()
    
    for server in df['server'].unique():
        server_df = df[df['server'] == server]
        total_times = server_df['elapsed_total_seconds']
        
        print(f"🖥️  {server}")
        print(f"   Tempo Total (com rede):")
        print(f"      Média:        {total_times.mean():.6f} s")
        print(f"      Mediana:      {total_times.median():.6f} s")
        print(f"      Mínimo:       {total_times.min():.6f} s")
        print(f"      Máximo:       {total_times.max():.6f} s")
        print(f"      Desvio Padrão: {total_times.std():.6f} s")
        
        # Tempo do servidor (se disponível)
        if has_server_time and 'elapsed_server_seconds' in server_df.columns:
            server_times = server_df['elapsed_server_seconds'].replace('', pd.NA).dropna()
            if len(server_times) > 0:
                server_times = pd.to_numeric(server_times, errors='coerce').dropna()
                if len(server_times) > 0:
                    print(f"   Tempo Servidor (processamento interno):")
                    print(f"      Média:        {server_times.mean():.6f} s")
                    print(f"      Mediana:      {server_times.median():.6f} s")
                    print(f"      Mínimo:       {server_times.min():.6f} s")
                    print(f"      Máximo:       {server_times.max():.6f} s")
        
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
    
    # Comparação direta
    print("=" * 70)
    print("⚖️  COMPARAÇÃO DIRETA")
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
        
        print("📊 TEMPO TOTAL (com rede e latência):")
        print(f"   🏆 Mais rápido: {faster_total} - {min(mean1_total, mean2_total):.6f} s")
        print(f"   🐌 Mais lento:  {slower_total} - {max(mean1_total, mean2_total):.6f} s")
        print(f"   📊 Diferença:   {diff_total:.6f} s ({pct_diff_total:.2f}%)")
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
                
                print("🔧 TEMPO DO SERVIDOR (processamento interno do Firebird):")
                print(f"   🏆 Mais rápido: {faster_srv} - {min(mean1_srv, mean2_srv):.6f} s")
                print(f"   🐌 Mais lento:  {slower_srv} - {max(mean1_srv, mean2_srv):.6f} s")
                print(f"   📊 Diferença:   {diff_srv:.6f} s ({pct_diff_srv:.2f}%)")
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
