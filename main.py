################################################################################
# Algoritmo para a resolução do problema do caixeiro viajante utilizando a heuristica do vizinho mais próximo
# código original de referência: https://github.com/dmishin/tsp-solver
################################################################################

import nnn
import matriz

if __name__ == '__main__':

    caminho = nnn.resolver(matriz.matriz(), endpoints=(2, 2))

    print(caminho)
