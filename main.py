# Importando as bibliotecas necessárias
import numpy as np # Biblioteca para manipulação de arrays
import random # Biblioteca para geração de números aleatórios
import multiprocessing as mp # Biblioteca para processamento paralelo
import time # Biblioteca para cálculo de tempo
import math # Biblioteca para cálculos matemáticos
import argparse # Biblioteca para passagem de argumentos

#Função para gerar um tabuleiro inicial com rainhas aleatórias
def gera_tabuleiro(numero_rainhas):
    tabuleiro = np.zeros((numero_rainhas, numero_rainhas), dtype=int) # Cria um tabuleiro com zeros
    for coluna in range(numero_rainhas): # Para cada coluna, coloca uma rainha aleatória
        linha_rainha = random.randint(0, numero_rainhas-1) # Gera uma posição aleatória para a rainha na coluna
        tabuleiro[linha_rainha, coluna] = 1 # Coloca a rainha na posição gerada
    return tabuleiro # Retorna o tabuleiro com as rainhas

# Função para verificar a quantidade de ataques que uma rainha sofre
def verifica_ataques(tabuleiro, linha, coluna, numero_rainhas):
    numero_ataques = 0
    # Verifica ataques na mesma linha
    for i in range(numero_rainhas):
        if (tabuleiro[linha][i] == 1 and i != coluna): # Se a rainha estiver na mesma linha e não for a mesma rainha 
            numero_ataques += 1 # Incrementa o número de ataques
            
    # Verifica ataques nas diagonais
    for i in range(1, numero_rainhas):
        if linha - i >= 0 and coluna - i >= 0 and tabuleiro[linha - i][coluna - i] == 1: # Verifica a diagonal superior esquerda 
            numero_ataques += 1 # Incrementa o número de ataques
        if linha + i < numero_rainhas and coluna + i < numero_rainhas and tabuleiro[linha + i][coluna + i] == 1: # Verifica a diagonal inferior direita
            numero_ataques += 1 # Incrementa o número de ataques
        
        if linha + i < numero_rainhas and coluna - i >= 0 and tabuleiro[linha + i][coluna - i] == 1: # Verifica a diagonal inferior esquerda
            numero_ataques += 1 # Incrementa o número de ataques
        if linha - i >= 0 and coluna + i < numero_rainhas and tabuleiro[linha - i][coluna + i] == 1: # Verifica a diagonal superior direita
            numero_ataques += 1 # Incrementa o número de ataques
            
    return numero_ataques # Retorna o número de ataques que a rainha

# Função para verificar o número total de ataques no tabuleiro
def verifica_ataques_totais(tabuleiro, numero_rainhas):
    numero_ataques = 0
    for linha in range(numero_rainhas): # Percorre todas as linhas
        for coluna in range(numero_rainhas): # Percorre todas as colunas
            if tabuleiro[linha][coluna] == 1: # Se encontrar uma rainha na posição atual
                numero_ataques += verifica_ataques(tabuleiro, linha, coluna, numero_rainhas) # Soma o número de ataques que a rainha sofre
    return numero_ataques


# Função para resolver o problema das n rainhas sem paralelização
def solucao_n_rainhas(tabuleiro, numero_rainhas):
    numero_total_ataques = verifica_ataques_totais(tabuleiro, numero_rainhas) # Calcula o número total de ataques no tabuleiro
    melhor_tabuleiro = np.copy(tabuleiro) # Cria uma cópia do tabuleiro atual
    while numero_total_ataques > 0: # Enquanto houver ataques no tabuleiro
        ataque_atual = numero_total_ataques # Salva o número de ataques atual
        
        # Percorre todas as linhas e colunas, quando encontrar encontrar uma rainha, tenta mudar de linha
        for linha in range(numero_rainhas):
            for coluna in range(numero_rainhas):
                if melhor_tabuleiro[linha][coluna] == 1: # Se encontrar uma rainha na posição atual
                    ataques_antes = verifica_ataques(melhor_tabuleiro, linha, coluna, numero_rainhas) # Calcula o número de ataques que a rainha antes de mudar de posição
                    for muda_linha in range(numero_rainhas): # Tenta mudar a rainha de posição
                        if muda_linha != linha:
                            novo_tabuleiro = np.copy(melhor_tabuleiro) # Cria uma cópia do tabuleiro atual
                            novo_tabuleiro[linha][coluna] = 0   # Remove a rainha da posição atual
                            novo_tabuleiro[muda_linha][coluna] = 1 # Coloca a rainha na nova posição
                            ataques_depois = verifica_ataques(novo_tabuleiro, muda_linha, coluna, numero_rainhas) # Calcula o número de ataques que a rainha sofre na nova posição
                            
                            if ataques_depois < ataques_antes: # Se o número de ataques diminuir com a mudança
                                melhor_tabuleiro = np.copy(novo_tabuleiro) # Atualiza o tabuleiro
                                numero_total_ataques = verifica_ataques_totais(melhor_tabuleiro, numero_rainhas) # Atualiza o número total de ataques
                                break # Sai do loop
                                
        if ataque_atual == numero_total_ataques: # Se o número de ataques não diminuir com a mudança de posição das rainhas 
            break # Sai do loop
            
    return tabuleiro, melhor_tabuleiro, numero_total_ataques # Retorna o tabuleiro original, o melhor tabuleiro e o número total de ataques

# Resolução Paralelizada
def solucao_n_rainhas_paralelo(numero_rainhas, numero_tabuleiros):
    tabuleiros_iniciais = [gera_tabuleiro(numero_rainhas) for _ in range(numero_tabuleiros)] # Gera tabuleiros iniciais para cada processo paralelo 

    # Gerando a Pool de processos, na qual cada processo vai receber um tabuleiro inicial para resolver
    with mp.Pool(processes=mp.cpu_count()) as pool: 
        resultados = pool.starmap(solucao_n_rainhas, [(tabuleiro, numero_rainhas) for tabuleiro in tabuleiros_iniciais]) # Mapeia a função solucao_n_rainhas para cada tabuleiro inicial

    tabuleiro, melhor_tabuleiro, menor_ataque = min(resultados, key = lambda x: x[2]) # Pega o melhor tabuleiro de todos os resultados obtidos
    
    # Imprime o tabuleiro original, o melhor tabuleiro e o número total de ataques
    print("Tabuleiro original:")
    print(tabuleiro)
    print("Numero de Ataques:")
    print(verifica_ataques_totais(tabuleiro, numero_rainhas))
    print("Tabuleiro Depois:")
    print(melhor_tabuleiro)
    print("Numero de Ataques:")
    print(menor_ataque)
    
    return melhor_tabuleiro # Retorna o melhor tabuleiro encontrado

# Função principal para execução do programa
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script projeto n rainhas") # Cria um parser de argumentos para passar o número de rainhas como argumento na execução do programa
    parser.add_argument('--rainhas', type=int, help="Numero rainhas", required=True) # Adiciona o argumento --rainhas para passar o número de rainhas
    args = parser.parse_args() # Faz o parse dos argumentos passados na execução do programa para a variável args
    numero_rainhas = args.rainhas # Pega o número de rainhas passado como argumento e salva na variável numero_rainhas

    # Para calcular um valor otimizado de número de tabuleiros vamos usar a Lei de Amdahl
    # Em conjunto com um fator de escalabilidade
    P = 0.88335 #definido como a porcentagem do programa que é paralelizável
    S = 1 / ((1-P)+(P/numero_rainhas))
    num_tabuleiros = round(S * math.log2(numero_rainhas))

    print("Resolvendo n-rainhas sem sistemas distribuidos: ")
    inicio = time.time() # Inicia a contagem de tempo
    tabuleiros = [] # Lista para armazenar os tabuleiros gerados

    # Gera tabuleiros iniciais e resolve o problema das n rainhas para cada tabuleiro
    for i in range(num_tabuleiros):  # Para cada tabuleiro
        tabuleiro = gera_tabuleiro(numero_rainhas) # Gera um tabuleiro inicial
        tabuleiro, melhor_tabuleiro, numero_ataques = solucao_n_rainhas(tabuleiro, numero_rainhas) # Resolve o problema das n rainhas
        tabuleiros.append([tabuleiro, melhor_tabuleiro, numero_ataques]) # Adiciona o tabuleiro original, o melhor tabuleiro e o número total de ataques na lista de tabuleiros
    tabuleiro, melhor_tabuleiro, menor_ataque = min(tabuleiros, key = lambda x: x[2]) # Pega o melhor tabuleiro de todos os tabuleiros gerados e resolvidos
    fim = time.time() # Finaliza a contagem de tempo da solução sem paralelização
    
    # Imprime o tabuleiro original, o melhor tabuleiro e o número total de ataques
    print("Tabuleiro antes: ")
    print(tabuleiro)
    print(f"Numero de ataques : {verifica_ataques_totais(tabuleiro, numero_rainhas)}")
    print("Tabuleiro depois:")
    print(melhor_tabuleiro)
    print(f"Numero de ataques : {numero_ataques}")
    print(f"Tempo de execucao {fim - inicio}")

    # Resolvendo o problema das n rainhas com paralelização
    print('-'*20)
    print("Resolvendo Usando sistemas distribuidos: ")
    inicio = time.time() # Inicia a contagem de tempo
    solucao_n_rainhas_paralelo(numero_rainhas, num_tabuleiros)  # Resolve o problema das n rainhas com paralelização
    fim = time.time() # Finaliza a contagem de tempo da solução com paralelização
    print(f"Tempo de execucao {fim - inicio}")