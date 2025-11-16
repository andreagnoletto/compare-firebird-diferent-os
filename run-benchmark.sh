#!/bin/bash

# Script para executar benchmarks do Firebird usando Docker

set -e

echo "🔥 Firebird Benchmark Runner"
echo "============================"
echo ""

# Verificar se .env existe
if [ ! -f .env ]; then
    echo "⚠️  Arquivo .env não encontrado!"
    echo ""
    echo "Criando .env a partir de .env.docker..."
    cp .env.docker .env
    echo "✅ Arquivo .env criado!"
    echo ""
    echo "📝 Por favor, edite o arquivo .env com as configurações dos seus servidores:"
    echo "   - WIN_FB_HOST, WIN_FB_PORT, WIN_FB_DATABASE, WIN_FB_USER, WIN_FB_PASSWORD"
    echo "   - LIN_FB_HOST, LIN_FB_PORT, LIN_FB_DATABASE, LIN_FB_USER, LIN_FB_PASSWORD"
    echo ""
    read -p "Pressione Enter após configurar o .env para continuar..."
fi

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando!"
    echo "   Por favor, inicie o Docker e tente novamente."
    exit 1
fi

echo "🔧 Verificando configuração..."
echo ""

# Mostrar configuração (sem senhas)
echo "Servidor 1:"
grep "^WIN_FB_HOST=" .env | sed 's/WIN_FB_HOST=/  Host: /'
grep "^WIN_FB_PORT=" .env | sed 's/WIN_FB_PORT=/  Porta: /'
grep "^WIN_FB_DATABASE=" .env | sed 's/WIN_FB_DATABASE=/  Database: /'
echo ""

echo "Servidor 2:"
grep "^LIN_FB_HOST=" .env | sed 's/LIN_FB_HOST=/  Host: /'
grep "^LIN_FB_PORT=" .env | sed 's/LIN_FB_PORT=/  Porta: /'
grep "^LIN_FB_DATABASE=" .env | sed 's/LIN_FB_DATABASE=/  Database: /'
echo ""

read -p "🚀 Executar benchmarks? (Enter para continuar, Ctrl+C para cancelar) "

echo ""
echo "🏗️  Construindo imagem Docker..."
docker compose build

echo ""
echo "▶️  Executando benchmarks..."
echo ""
docker compose up

echo ""
echo "✅ Benchmark concluído!"
if [ -f firebird_benchmark_results.csv ]; then
    echo "📊 Resultados salvos em: firebird_benchmark_results.csv"
    echo ""
    echo "Primeiras linhas do resultado:"
    head -n 10 firebird_benchmark_results.csv
fi
