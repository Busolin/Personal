import numpy as np
import multiprocessing as mp
import time
import random
import argparse
import copy
import matplotlib.pyplot as plt
import psutil


# Essa função salva em um arquivo txt todas as matrizes com as soluções
def salvar_solucoes(solucoes, nome):
    with open(nome, "w") as file:
        for idx, solucao in enumerate(solucoes):
            file.write(f"Solução {idx + 1}:\n\n")
            for linha in solucao:
                file.write(" ".join("R" if x else "." for x in linha) + "\n")
            file.write("\n--------------------\n\n")

# Gera um tabuleiro bidimensional (n x n) na qual n = numero de rainhas
# Além disso todos os valores do tabuleiro são 0
def gerar_tabuleiro(n_rainhas):
    tabuleiro = np.zeros((n_rainhas, n_rainhas), dtype=int)
    return tabuleiro

# Como o objetivo é encontrar todas as soluções o código adiciona rainhas aos poucos
# Sendo assim só precisamos verificar se houve um ataque até a coluna da ultima rainha adicionada
def verifica_ataque(tabuleiro, linha, coluna, n_rainhas):
    # Verifica se há ataques na horizontal
    for i in range(coluna):
        if tabuleiro[linha][i] == 1:
            return False
            
    # Verifica a diagonal a esquerda (não precisamos verificar a direita)
    # Pelo modo que foi construida a solução
    for i in range(1, coluna + 1):
        # Verifica se há ataques na diagonal superior esquerda
        if linha - i >= 0 and coluna - i >= 0 and tabuleiro[linha - i][coluna - i] == 1:
            return False
        # Verifica se há ataques na diagonal inferior esquerda
        if linha + i < n_rainhas and coluna - i >= 0 and tabuleiro[linha + i][coluna - i] == 1:
            return False
            
    return True

# O problema é resolvido por recursão, a ideia é percorrer a rainha através da linhas da primeira da primeira coluna
# e percorrendo nas linhas nas outras colunas para verificar se é possível adicionar a rainha sem sofrer ataques
def resolve_n_rainhas_seq(tabuleiro, coluna, n_rainhas, solucoes):
    # Quando coluna for maior ou igual ao numero de rainhas significa que todas as rainhas foram colocadas
    # Com isso eu adiciono a solução a lista de soluções
    if coluna >= n_rainhas:
        solucoes.append(copy.deepcopy(tabuleiro))
        return
    # Caso contrário ele percorre toda linha tentando adicionar uma rainha
    # Caso consiga ele chama a função resolve_n_rainhas_seq novamente na próxima coluna
    for i in range(n_rainhas):
        if verifica_ataque(tabuleiro, i, coluna, n_rainhas):
            tabuleiro[i][coluna] = 1
            resolve_n_rainhas_seq(tabuleiro, coluna + 1, n_rainhas, solucoes)
            # tabuleiro[i][coluna] = 0 garante que o programa encontre as outras soluções
            tabuleiro[i][coluna] = 0

# Função apenas cria o tabuleiro e a lista de soluções
# e chama a função que resolve o problema sequencialmente 
def soluciona_n_rainhas_seq(n_rainhas):
    tabuleiro = gerar_tabuleiro(n_rainhas)
    solucoes = []
    resolve_n_rainhas_seq(tabuleiro, 0, n_rainhas, solucoes)
    return solucoes


# A ideia para resolver em paralelo foi que cada processo assumisse uma linha do tabuleiro
# Então além de colocar a rainha na primeira linha da primeira coluna e encontrar todas as soluções
# E depois passar para a proxima linha, o paralelo executa cada linha paralelamente.
def resolve_n_rainhas_paralelo(linha, n_rainhas):
    tabuleiro = gerar_tabuleiro(n_rainhas)
    solucoes = []
    tabuleiro[linha][0] = 1 # Posiciona a primeira rainha na linha especificada
    resolve_n_rainhas_seq(tabuleiro, 1, n_rainhas, solucoes)
    return solucoes

# Função chamada para resolver o n rainhas paralelamente
def soluciona_n_rainhas_paralelo(n_rainhas):
    # Cria uma pool de processos igual o número de rainhas
    with mp.Pool(processes=n_rainhas) as pool:
        # Distribui o trabalho entre os processos no pool e coleta os resultados
        resultados = pool.starmap(resolve_n_rainhas_paralelo, [(linha, n_rainhas) for linha in range(n_rainhas)])
    solucoes = [solucao for sublist in resultados for solucao in sublist]
    return solucoes

# Função para medir o tempo de execução
def medir_tempo(n_rainhas, paralelo=False):
    start_time = time.time()
    if paralelo:
        soluciona_n_rainhas_paralelo(n_rainhas)
    else:
        soluciona_n_rainhas_seq(n_rainhas)
    end_time = time.time()
    return end_time - start_time

# Função para comparar os tempos e criar um grafico
# Na qual mostra a partir de que momento o paralelo é mais rapido
def plot_compara_tempo(maximo_rainhas):
    n_rainhas_range = range(1, maximo_rainhas + 1)
    tempos_sequenciais = []
    tempos_paralelos = []

    # Faz para até um valor maximo de rainhas coleta o tempo do sequencial e do paralelo
    for n_rainhas in n_rainhas_range:
        tempo_sequencial = medir_tempo(n_rainhas)
        tempo_paralelo = medir_tempo(n_rainhas, paralelo=True)

        tempos_sequenciais.append(tempo_sequencial)
        tempos_paralelos.append(tempo_paralelo)

    # Encontra o ponto onde o paralelo começa a ser mais rapido
    tempo_sequencial_np = np.array(tempos_sequenciais)
    tempo_paralelo_np = np.array(tempos_paralelos)
    diferencial = tempo_sequencial_np - tempo_paralelo_np
    ponto_mudanca = np.where(diferencial > 0)[0]

    # Verifica se há mesmo esse ponto
    if len(ponto_mudanca) > 0:
        ponto_mudanca = ponto_mudanca[0] + 1  # +1 porque o índice começa do 0
    else:
        ponto_mudanca = None

    # Plota o grafico
    plt.figure(figsize=(10, 6))
    plt.plot(n_rainhas_range, tempos_sequenciais, label='Sequencial', marker='o')
    plt.plot(n_rainhas_range, tempos_paralelos, label='Paralelo', marker='o')
    if ponto_mudanca:
        plt.axvline(x=ponto_mudanca, color='r', linestyle='--', label='Mudança de Performance')
        plt.annotate(f'{ponto_mudanca} rainhas',
                     xy=(ponto_mudanca, min(tempos_sequenciais[-1], tempos_paralelos[-1])),
                     xytext=(ponto_mudanca+1, min(tempos_sequenciais[-1], tempos_paralelos[-1]) + 0.1),
                     arrowprops=dict(facecolor='red', shrink=0.05))

    plt.xlabel('Número de Rainhas')
    plt.ylabel('Tempo de Execução (segundos)')
    plt.title('Comparação de Tempos: Sequencial vs Paralelo')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'comparacao_sequencial_multiprocessos_{maximo_rainhas}_rainhas.png', dpi=1200)


# Além de comparar apenas o tempo de execução como multiprocessos criar varias processos podemos monitorar uso da memória e da cpu
def medir_recursos(n_rainhas, paralelo=False):
    # Medir o uso inicial de CPU e memória
    cpu_start = psutil.cpu_percent(interval=1)  
    memoria_start = psutil.virtual_memory().used
    
    start_time = time.time()
    
    if paralelo:
        soluciona_n_rainhas_paralelo(n_rainhas)
    else:
        soluciona_n_rainhas_seq(n_rainhas)
    
    end_time = time.time()
    
    # Medir o uso final de CPU e memória
    cpu_end = psutil.cpu_percent(interval=1)  
    memoria_end = psutil.virtual_memory().used
    
    tempo_execucao = end_time - start_time
    
    # Calcular o uso de recursos
    cpu_uso = cpu_end - cpu_start
    memoria_uso = (memoria_end - memoria_start) / (1024 * 1024)  
    
    return tempo_execucao, cpu_uso, memoria_uso

def plot_recursos(maximo_rainhas):
    n_rainhas_range = range(1, maximo_rainhas + 1)
    tempos_sequenciais = []
    tempos_paralelos = []
    cpu_sequencial = []
    cpu_paralelo = []
    memoria_sequencial = []
    memoria_paralelo = []

    for n_rainhas in n_rainhas_range:
        tempo_sequencial, cpu_uso_sequencial, memoria_uso_sequencial = medir_recursos(n_rainhas, paralelo=False)
        tempo_paralelo, cpu_uso_paralelo, memoria_uso_paralelo = medir_recursos(n_rainhas, paralelo=True)
        
        tempos_sequenciais.append(tempo_sequencial)
        tempos_paralelos.append(tempo_paralelo)
        cpu_sequencial.append(cpu_uso_sequencial)
        cpu_paralelo.append(cpu_uso_paralelo)
        memoria_sequencial.append(memoria_uso_sequencial)
        memoria_paralelo.append(memoria_uso_paralelo)

    plt.figure(figsize=(14, 8))

    plt.subplot(2, 2, 1)
    plt.plot(n_rainhas_range, tempos_sequenciais, label='Sequencial', marker='o', color='b')
    plt.plot(n_rainhas_range, tempos_paralelos, label='Paralelo', marker='o', color='r')
    plt.xlabel('Número de Rainhas')
    plt.ylabel('Tempo de Execução (segundos)')
    plt.title('Tempo de Execução vs Número de Rainhas')
    plt.legend()
    plt.grid(True)

    plt.subplot(2, 2, 2)
    plt.plot(n_rainhas_range, cpu_sequencial, label='Sequencial', marker='o', color='b')
    plt.plot(n_rainhas_range, cpu_paralelo, label='Paralelo', marker='o', color='r')
    plt.xlabel('Número de Rainhas')
    plt.ylabel('Uso da CPU (%)')
    plt.title('Uso da CPU vs Número de Rainhas')
    plt.legend()
    plt.grid(True)

    plt.subplot(2, 2, 3)
    plt.plot(n_rainhas_range, memoria_sequencial, label='Sequencial', marker='o', color='b')
    plt.plot(n_rainhas_range, memoria_paralelo, label='Paralelo', marker='o', color='r')
    plt.xlabel('Número de Rainhas')
    plt.ylabel('Uso da Memória (MB)')
    plt.title('Uso da Memória vs Número de Rainhas')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'recursos_{maximo_rainhas}_rainhas.png', dpi=1200)

# Apenas para mostrar uma das solucoes (mostrar todas seria inviavel para valores elevados)
def print_uma_solucao(solucoes):
    indice = random.randint(0, len(solucoes)-1)
    solucao = solucoes[indice]
    print("Uma solução possível: \n")
    for linha in solucao:
        print(' '.join('R' if x else '.' for x in linha))
    print('-' * (len(solucao) * 2 - 1))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script projeto n rainhas")
    parser.add_argument('--rainhas', type=int, help="Numero rainhas (int)", required=True)
    parser.add_argument('--plot', type=bool, help="Plotar Gráfico (True ou False)", default=False)
    parser.add_argument('--save', type=bool, help="Salvar as solucoes (True ou False)", default=False)
    parser.add_argument('--extra', type=bool, help="Adicione explicações extras (True ou False)", default=False)
    args = parser.parse_args()
    numero_rainhas = args.rainhas
    plot = args.plot
    save = args.save
    extra = args.extra

    solucoes_paralelos = soluciona_n_rainhas_paralelo(numero_rainhas)
    solucoes_sequenciais = soluciona_n_rainhas_seq(numero_rainhas)

    print_uma_solucao(solucoes_paralelos)
    print_uma_solucao(solucoes_sequenciais)

    if extra:
        plot_recursos(numero_rainhas)

    elif plot:
        plot_compara_tempo(numero_rainhas)

    if save:
        salvar_solucoes(solucoes_paralelos, f"solucoes_{numero_rainhas}_rainhas_paralelo.txt")
        salvar_solucoes(solucoes_sequenciais,  f"solucoes_{numero_rainhas}_rainhas_sequencial.txt")