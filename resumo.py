import csv
import statistics

tempos_c1 = []
tempos_c2 = []

print("\n=== TABELA CONSOLIDADA DE RESULTADOS ===")
print(f"{'Condição':<12} | {'Rep':<4} | {'Trabalho Fixo':<15} | {'Wall Time (s)':<15} | {'CPU Time (s)':<15} | {'Trabalho/s'}")
print("-" * 85)

try:
    with open('resultados.csv', 'r') as f:
        reader = csv.DictReader(f)
        for linha in reader:
            cond = linha['Condicao']
            rep = linha['Repeticao']
            trab_fixo = linha['Trabalho']
            wall = float(linha['WallTime'])
            cpu = float(linha['CpuTime'])
            trab_seg = linha['TrabalhoPorSegundo']
            
            print(f"{cond[:10]:<12} | {rep:<4} | {trab_fixo:<15} | {wall:<15.4f} | {cpu:<15.4f} | {trab_seg}")
            
            if "C1" in cond:
                tempos_c1.append(wall)
            elif "C2" in cond:
                tempos_c2.append(wall)
                
    if tempos_c1 and tempos_c2:
        med_c1 = statistics.median(tempos_c1)
        med_c2 = statistics.median(tempos_c2)
        
        print("\n=== GRÁFICO COMPARATIVO (Wall Time - Mediana) ===")
        print("Note como a CPU restrita afeta o tempo real do relógio (Wall Time), ")
        print("devido ao Throttling imposto pelo cgroup no host.\n")
        
        max_val = max(med_c1, med_c2)
        bar_c1 = int((med_c1 / max_val) * 40)
        bar_c2 = int((med_c2 / max_val) * 40)
        
        print(f"C1 (0.5 CPU) | {'█' * bar_c1} {med_c1:.4f} s")
        print(f"C2 (1.0 CPU) | {'█' * bar_c2} {med_c2:.4f} s")
except FileNotFoundError:
    print("Erro: O arquivo resultados.csv não foi encontrado. Execute o run_experimentos.sh primeiro.")