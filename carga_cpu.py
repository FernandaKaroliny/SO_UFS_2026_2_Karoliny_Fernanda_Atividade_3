import os
import time
import hashlib

def executar_carga_deterministica(iteracoes):
    # Trabalho matemático fixo (soma e multiplicação)
    trabalho = 0
    for i in range(iteracoes):
        trabalho += (i * 2) - 1
        
    # Checksum para provar correção
    checksum = hashlib.md5(str(trabalho).encode()).hexdigest()[:8]
    return trabalho, checksum

if __name__ == "__main__":
    # Coleta parâmetros das variáveis de ambiente (passadas pelo bash)
    it = int(os.environ.get("ITERACOES", 20000000))
    cond = os.environ.get("CONDICAO", "C_Teste")
    rep = os.environ.get("REPETICAO", "0")
    
    # Captura os tempos iniciais
    start_wall = time.time()
    start_cpu = time.process_time()
    
    # Executa o processamento pesado
    resultado, checksum = executar_carga_deterministica(it)
    
    # Captura os tempos finais
    end_wall = time.time()
    end_cpu = time.process_time()
    
    wall_time = end_wall - start_wall
    cpu_time = end_cpu - start_cpu
    trabalho_por_seg = it / wall_time if wall_time > 0 else 0
    
    # Imprime os resultados no formato CSV
    print(f"{cond},{rep},{it},{checksum},OK,{wall_time:.4f},{cpu_time:.4f},{trabalho_por_seg:.2f}")