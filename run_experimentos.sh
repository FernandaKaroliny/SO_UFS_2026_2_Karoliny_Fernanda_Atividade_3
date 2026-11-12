#!/bin/bash

ITERACOES=${ITERACOES:-20000000}
ARQUIVO_SAIDA="resultados.csv"

# Cria o cabeçalho do arquivo CSV
echo "Condicao,Repeticao,Trabalho,Checksum,Status,WallTime,CpuTime,TrabalhoPorSegundo" > $ARQUIVO_SAIDA

echo "Iniciando experimento de Cgroups com $ITERACOES iterações..."

for i in {1..3}; do
    echo "--- Repetição $i/3 ---"
    
    # Condição C1: 0.5 CPU
    echo "[C1] Contêiner com 0.5 CPU e 256MiB RAM..."
    docker run --rm \
        --cpus="0.5" --memory="256m" --memory-swap="256m" --pids-limit="64" \
        -e CONDICAO="C1_0.5CPU" -e REPETICAO="$i" -e ITERACOES="$ITERACOES" \
        -v "$PWD:/app" -w /app \
        $IMAGEM_LAB python carga_cpu.py >> $ARQUIVO_SAIDA
        
    # Condição C2: 1.0 CPU
    echo "[C2] Contêiner com 1.0 CPU e 256MiB RAM..."
    docker run --rm \
        --cpus="1.0" --memory="256m" --memory-swap="256m" --pids-limit="64" \
        -e CONDICAO="C2_1.0CPU" -e REPETICAO="$i" -e ITERACOES="$ITERACOES" \
        -v "$PWD:/app" -w /app \
        $IMAGEM_LAB python carga_cpu.py >> $ARQUIVO_SAIDA
done

echo "Experimento concluído! Os dados brutos foram salvos em $ARQUIVO_SAIDA."