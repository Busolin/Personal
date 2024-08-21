import numpy as np
import random
import multiprocessing as mp
import time
import argparse

def gera_tabuleiro(numero_rainhas):
    tabuleiro = np.zeros((numero_rainhas, numero_rainhas), dtype=int)
    for coluna in range(numero_rainhas):
        linha_rainha = random.randint(0, numero_rainhas-1)
        tabuleiro[linha_rainha, coluna] = 1
    return tabuleiro

def verifica_ataques(tabuleiro, linha, coluna, numero_rainhas):
    numero_ataques = 0
    # Linha
    for i in range(numero_rainhas):
        if (tabuleiro[linha][i] == 1 and i != coluna):
            numero_ataques += 1
            
    # Verifica ataques nas diagonais
    for i in range(1, numero_rainhas):
        if linha - i >= 0 and coluna - i >= 0 and tabuleiro[linha - i][coluna - i] == 1:
            numero_ataques += 1
        if linha + i < numero_rainhas and coluna + i < numero_rainhas and tabuleiro[linha + i][coluna + i] == 1:
            numero_ataques += 1
        
        if linha + i < numero_rainhas and coluna - i >= 0 and tabuleiro[linha + i][coluna - i] == 1:
            numero_ataques += 1
        if linha - i >= 0 and coluna + i < numero_rainhas and tabuleiro[linha - i][coluna + i] == 1:
            numero_ataques += 1
            
    return numero_ataques

def verifica_ataques_totais(tabuleiro, numero_rainhas):
    numero_ataques = 0
    for linha in range(numero_rainhas):
        for coluna in range(numero_rainhas):
            if tabuleiro[linha][coluna] == 1:
                numero_ataques += verifica_ataques(tabuleiro, linha, coluna, numero_rainhas)
    return numero_ataques


def solucao_n_rainhas(tabuleiro, numero_rainhas):
    numero_total_ataques = verifica_ataques_totais(tabuleiro, numero_rainhas)
    melhor_tabuleiro = np.copy(tabuleiro)
    while numero_total_ataques > 0:
        ataque_atual = numero_total_ataques
        
        # Percorre todas as linhas e colunas, quando encontrar encontrar uma rainha, tenta mudar de linha
        for linha in range(numero_rainhas):
            for coluna in range(numero_rainhas):
                if melhor_tabuleiro[linha][coluna] == 1:
                    ataques_antes = verifica_ataques(melhor_tabuleiro, linha, coluna, numero_rainhas)
                    for muda_linha in range(numero_rainhas):
                        if muda_linha != linha:
                            novo_tabuleiro = np.copy(melhor_tabuleiro)
                            novo_tabuleiro[linha][coluna] = 0
                            novo_tabuleiro[muda_linha][coluna] = 1
                            ataques_depois = verifica_ataques(novo_tabuleiro, muda_linha, coluna, numero_rainhas)
                            
                            if ataques_depois < ataques_antes:
                                melhor_tabuleiro = np.copy(novo_tabuleiro)
                                numero_total_ataques = verifica_ataques_totais(melhor_tabuleiro, numero_rainhas)
                                break
                                
        if ataque_atual == numero_total_ataques:
            break
            
    return tabuleiro, melhor_tabuleiro, numero_total_ataques

# Resolução Paralelizada
def solucao_n_rainhas_paralelo(numero_rainhas, numero_tabuleiros):
    tabuleiros_iniciais = [gera_tabuleiro(numero_rainhas) for _ in range(numero_tabuleiros)]

    # Gerando a Pool de processos, na qual cada processo vai receber um tabuleiro inicial para resolver
    with mp.Pool(processes=mp.cpu_count()) as pool:
        resultados = pool.starmap(solucao_n_rainhas, [(tabuleiro, numero_rainhas) for tabuleiro in tabuleiros_iniciais])

    tabuleiro, melhor_tabuleiro, menor_ataque = min(resultados, key = lambda x: x[2])
    print("Tabuleiro original:")
    print(tabuleiro)
    print("Numero de Ataques:")
    print(verifica_ataques_totais(tabuleiro, numero_rainhas))
    print("Tabuleiro Depois:")
    print(melhor_tabuleiro)
    print("Numero de Ataques:")
    print(menor_ataque)
    
    return melhor_tabuleiro


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script projeto n rainhas")
    parser.add_argument('--rainhas', type=int, help="Numero rainhas", required=True)
    parser.add_argument('--processos', type=int, help="Numero processos", required=True)
    args = parser.parse_args()

    numero_rainhas = args.rainhas
    num_tabuleiros = args.processos
    print("Resolvendo n-rainhas sem sistemas distribuidos: ")
    inicio = time.time()
    tabuleiros = []
    for i in range(num_tabuleiros):
        tabuleiro = gera_tabuleiro(numero_rainhas)
        tabuleiro, melhor_tabuleiro, numero_ataques = solucao_n_rainhas(tabuleiro, numero_rainhas)
        tabuleiros.append([tabuleiro, melhor_tabuleiro, numero_ataques])
    tabuleiro, melhor_tabuleiro, menor_ataque = min(tabuleiros, key = lambda x: x[2])
    fim = time.time()
    print("Tabuleiro antes: ")
    print(tabuleiro)
    print(f"Numero de ataques : {verifica_ataques_totais(tabuleiro, numero_rainhas)}")
    print("Tabuleiro depois:")
    print(melhor_tabuleiro)
    print(f"Numero de ataques : {numero_ataques}")
    print(f"Tempo de execucao {fim - inicio}")
    print('-'*20)
    print("Resolvendo Usando sistemas distribuidos: ")
    inicio = time.time()
    solucao_n_rainhas_paralelo(numero_rainhas, num_tabuleiros)
    fim = time.time()
    print(f"Tempo de execucao {fim - inicio}")