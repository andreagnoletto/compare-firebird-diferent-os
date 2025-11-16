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
    
    # Estatísticas por servidor
    print("=" * 70)
    print("📊 ESTATÍSTICAS POR SERVIDOR")
    print("=" * 70)
    print()
    
    for server in df['server'].unique():
        server_data = df[df['server'] == server]['elapsed_seconds']
        
        print(f"🖥️  {server}")
        print(f"   Média:        {server_data.mean():.6f} s")
        print(f"   Mediana:      {server_data.median():.6f} s")
        print(f"   Mínimo:       {server_data.min():.6f} s")
        print(f"   Máximo:       {server_data.max():.6f} s")
        print(f"   Desvio Padrão: {server_data.std():.6f} s")
        print(f"   Variância:    {server_data.var():.6f}")
        print()
    
    # Comparação direta
    print("=" * 70)
    print("⚖️  COMPARAÇÃO DIRETA")
    print("=" * 70)
    print()
    
    servers = df['server'].unique()
    if len(servers) == 2:
        server1_data = df[df['server'] == servers[0]]['elapsed_seconds']
        server2_data = df[df['server'] == servers[1]]['elapsed_seconds']
        
        mean1 = server1_data.mean()
        mean2 = server2_data.mean()
        
        diff = abs(mean1 - mean2)
        pct_diff = (diff / min(mean1, mean2)) * 100
        
        faster = servers[0] if mean1 < mean2 else servers[1]
        slower = servers[1] if faster == servers[0] else servers[0]
        
        print(f"🏆 Servidor mais rápido: {faster}")
        print(f"   Tempo médio: {min(mean1, mean2):.6f} s")
        print()
        print(f"🐌 Servidor mais lento: {slower}")
        print(f"   Tempo médio: {max(mean1, mean2):.6f} s")
        print()
        print(f"📊 Diferença absoluta: {diff:.6f} s")
        print(f"📊 Diferença percentual: {pct_diff:.2f}%")
        print()
        
        # Interpretação
        if pct_diff < 5:
            print("✅ Performance similar entre os servidores (diferença < 5%)")
        elif pct_diff < 15:
            print("⚠️  Diferença moderada de performance (5-15%)")
        else:
            print(f"🔴 Diferença significativa! {faster} é {pct_diff:.1f}% mais rápido")
    
    print()
    
    # Tabela de estatísticas descritivas
    print("=" * 70)
    print("📋 TABELA DE ESTATÍSTICAS DESCRITIVAS")
    print("=" * 70)
    print()
    print(df.groupby('server')['elapsed_seconds'].describe())
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
    print("   df.boxplot(by='server', column='elapsed_seconds')")
    print("   plt.ylabel('Tempo (segundos)')")
    print("   plt.title('Comparação de Performance Firebird')")
    print("   plt.suptitle('')  # Remove título automático")
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
