# SO_UFS_2026_2_Karoliny_Fernanda_Atividade_3

# Laboratório Prático de Isolamento e Contingenciamento em Linux (Atividade 3 - SO)

Este repositório contém os scripts, instruções de execução e evidências para o laboratório prático da **Atividade 3 da disciplina de Sistemas Operacionais (UFS)**. 

O objetivo do projeto é demonstrar, em nível de Kernel Linux, os mecanismos de isolamento de visão (**Namespaces**) e contingentamento de hardware (**Cgroups v2**), estabelecendo a diferenciação prática entre contêineres operando sobre um kernel compartilhado e máquinas virtuais independentes.


## Vídeo da atividade
* Link para o vídeo da apresentação: https://drive.google.com/drive/folders/1niM_SXtS85kj1x9OfWG4e2ZfFv6cdhWh?usp=drive_link

---

## 🛠️ 1. Pré-requisitos e Ambiente

Para reproduzir fielmente os experimentos deste repositório, o ambiente deve atender às seguintes especificações:

- **Sistema Operacional:** Linux (recomenda-se Fedora Linux 39+ ou distribuições com Cgroup v2 nativo).
- **Gerenciador de Cgroups:** `cgroup v2` ativo e delegado ao `systemd`.
- **Motor de Conteinerização:** Docker Engine 25.0+ (ou Docker Desktop/CE).
- **Linguagem / Runtimes:** Python 3.10+ (instalado no host e imagem `python:3.12-slim` no Docker).
- **Privilégios:** Acesso de usuário ao grupo `docker` ou privilégios de `sudo`.

### Verificação Rápida do Ambiente
Abra o terminal do host e confirme a presença do Cgroup v2 e do Docker:

```bash
# Verificar a versão do cgroup (Deve retornar cgroup2fs)
stat -fc %T /sys/fs/cgroup

# Verificar se o Docker Engine está ativo com driver systemd
docker info | grep -i cgroup
```

---

## 📂 2. Estrutura do Repositório

```text
.
├── carga_cpu.py           # Script determinístico de carga computacional e medição de tempos
├── run_experimentos.sh    # Script de automação das rodadas C1 (0.5 CPU) e C2 (1.0 CPU)
├── resumo.py              # Script de consolidação e exibição de gráfico em ASCII
├── resultados.csv         # Registro empírico gerado após as 6 execuções dos cgroups
└── README.md              # Documentação e guia de execução
```

---

## 🚀 3. Passo a Passo para Execução dos Experimentos

---

### 🔹 PARTE A: Verificação da Infraestrutura

Certifique-se de que a imagem oficial do Python necessária para os testes esteja baixada localmente:

```bash
docker pull python:3.12-slim
```

---

### 🔹 PARTE B: Evidências de Isolamento por Namespaces

Nesta etapa, demonstraremos como os namespaces do kernel particionam a visibilidade de processos (PID), sistema de arquivos (Mount) e rede (Network).

1. **Instanciar dois contêineres isolados em segundo plano:**

```bash
docker run -d --name lab_cont_A python:3.12-slim sleep infinity
docker run -d --name lab_cont_B python:3.12-slim sleep infinity
```

2. **Verificar os PIDs no espaço de nomes do Host vs Interno:**

```bash
# Obter PID do Contêiner A no Kernel do Host
PID_A=$(docker inspect -f '{{.State.Pid}}' lab_cont_A)
echo "PID no Host (Contêiner A): $PID_A"

# Obter PID do Contêiner B no Kernel do Host
PID_B=$(docker inspect -f '{{.State.Pid}}' lab_cont_B)
echo "PID no Host (Contêiner B): $PID_B"

# Verificar o PID interno do processo sleep dentro do Contêiner A (deve retornar PID 1)
docker exec lab_cont_A ps aux
```

3. **Inspecionar os handles dos Namespaces via `/proc` no Host:**

```bash
echo "=== NAMESPACES DO CONTÊINER A ==="
ls -l /proc/$PID_A/ns/ | grep -E "(pid|mnt|net)"

echo "=== NAMESPACES DO CONTÊINER B ==="
ls -l /proc/$PID_B/ns/ | grep -E "(pid|mnt|net)"
```

*Interpretação:* Observe que os identificadores numéricos `pid:[...]`, `mnt:[...]` e `net:[...]` serão diferentes entre os dois contêineres, comprovando o isolamento de visão exercido pelo kernel.

4. **Limpeza dos contêineres de teste:**

```bash
docker rm -f lab_cont_A lab_cont_B
```

---

### 🔹 PARTE C: Experimento de Contingenciamento por Cgroups (CPU & Memory)

Nesta etapa, utilizaremos a suíte de scripts em Python/Bash para aplicar restrições rígidas de CPU e observar o fenômeno de *throttling*.

#### Arquivos da Suíte de Testes:

1. **`carga_cpu.py`**
2. **`run_experimentos.sh`**
3. **`resumo.py`**


#### Passo a Passo da Execução da Carga:

1. Dê permissão de execução ao script Bash:
   ```bash
   chmod +x run_experimentos.sh
   ```

2. Execute o orquestrador do teste:
   ```bash
   ./run_experimentos.sh
   ```

3. Exiba o resumo analítico e o gráfico comparativo no terminal:
   ```bash
   python3 resumo.py
   ```

---

### 🔹 PARTE D: Demonstração de Mount e Menor Privilégio

Demostração prática da isolamento no VFS com a flag de apenas leitura (`:ro`), execução com usuário sem privilégios e corte de capabilities do kernel.

1. **Criar o diretório sintético de testes no Host:**
   ```bash
   mkdir -p ./dados_demo
   echo "Documento sintetico" > ./dados_demo/texto.txt
   ```

2. **Teste 1: Leitura Permitida (Princípio do Menor Privilégio)**
   ```bash
   docker run --rm \
     --user 1000:1000 \
     --cap-drop=ALL \
     --security-opt="no-new-privileges:true" \
     -v "$(pwd)/dados_demo:/dados:ro" \
     python:3.12-slim \
     cat /dados/texto.txt
   ```
   *Resultado Esperado:* Imprime `Documento sintetico`.

3. **Teste 2: Tentativa de Escrita Bloqueada (Negação via Read-Only Mount)**
   ```bash
   docker run --rm \
     --user 1000:1000 \
     --cap-drop=ALL \
     --security-opt="no-new-privileges:true" \
     -v "$(pwd)/dados_demo:/dados:ro" \
     python:3.12-slim \
     sh -c 'echo "Invasao" > /dados/novo_arquivo.txt'
   ```
   *Resultado Esperado:* Bloqueio imediato com a mensagem `sh: 1: cannot create /dados/novo_arquivo.txt: Read-only file system`.

4. **Limpeza do ambiente:**
   ```bash
   rm -rf ./dados_demo
   ```

---

## 📊 4. Interpretação dos Resultados Obtidos

- **Namespaces:** Provam que os contêineres possuem visões distintas da árvore de processos (PIDs), permitindo que múltiplos contêineres tenham seu próprio `PID 1` sem conflitar com o kernel do host.
- **Cgroups (Throttling):** A restrição de `0.5 CPU` reduz o rendimento pela metade (infla o *Wall Time* para ~5.1s enquanto o *CPU Time* permanece constante em ~2.6s). Isso ocorre porque o cgroup v2 suspende a execução do contêiner a cada janela de ciclo temporal (esgotamento da quota em `cpu.max`), sem reservar um núcleo físico isolado.
- **Mount & Privilégios:** A combinação da flag `:ro` no ponto de montagem VFS com o corte de capabilities impede a gravação não autorizada no sistema de arquivos do host, demonstrando a defesa em camadas.

---
