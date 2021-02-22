from __future__ import print_function, division
from array import array


if "xrange" not in globals():
    # py3
    xrange = range
else:
    # py2
    pass


def solucao_otimizada(distancias, conexoes, endpoints):
    """Função para otimizar a solção encontrada pelo algoritmo guloso"""
    N = len(conexoes)
    caminho = caminho_inicial(conexoes, endpoints)

    def ds(i, j):  # variáveis que são a distancia entre os pontos i e j
        pi = caminho[i]
        pj = caminho[j]
        if pi < pj:
            return distancias[pj][pi]
        else:
            return distancias[pi][pj]

    d_total = 0.0
    otimizacoes = 0
    for a in xrange(N - 1):
        b = a + 1
        for c in xrange(b + 2, N - 1):
            d = c + 1
            delta_d = ds(a, b) + ds(c, d) - (ds(a, c) + ds(b, d))
            if delta_d > 0:
                d_total += delta_d
                otimizacoes += 1
                conexoes[caminho[a]].remove(caminho[b])
                conexoes[caminho[a]].append(caminho[c])
                conexoes[caminho[b]].remove(caminho[a])
                conexoes[caminho[b]].append(caminho[d])

                conexoes[caminho[c]].remove(caminho[d])
                conexoes[caminho[c]].append(caminho[a])
                conexoes[caminho[d]].remove(caminho[c])
                conexoes[caminho[d]].append(caminho[b])
                caminho[:] = caminho_inicial(conexoes, endpoints)

    return otimizacoes, d_total


def caminho_inicial(conexoes, endpoints):
    """
    Pega uma matriz e retorna um caminho.
    As conexões consistem em uma lista de arrays com 1 ou 2 elementos
    onde esses elementos se tornam indices do vértice, conectados a este vértice.
    Esse método garante que o primeiro índice seja menor que o segundo
    """
    # quando o endpoint não é passado para a função, os pontos de começo e termino não são delimitados
    comeco, fim = endpoints or (None, None)
    """
    Se os pontos de partida e chegada não são especificados
    eles são substituidos com os resultados encontrados na execução do programa
    """
    precisa_reverter = False
    loop = (comeco is not None) and (comeco == fim)
    if comeco is None:
        if fim is None:
            # encontra o primeiro nodo que tem somente uma conexão
            comeco = next(idx
                         for idx, conn in enumerate(conexoes)
                         if len(conn) == 1)
        else:
            # Neste caso, encontra o final e então inverte a ordem
            comeco = fim
            precisa_reverter = True

    # pronto para gerar o caminho
    caminho = [comeco]
    ponto_anterior = None
    ponto_atual = comeco
    # A quantidade de pontos deve ser a mesma da de nodos ou mais uma se nós estamos procurando por um loop
    # Nós ja temos o ponto inicial, então faremos o resto das conexões
    for _ in xrange(len(conexoes) - (0 if loop else 1)):
        proximo_ponto = next(pnt for pnt in conexoes[ponto_atual]
                          if pnt != ponto_anterior)
        caminho.append(proximo_ponto)
        ponto_anterior, ponto_atual = ponto_atual, proximo_ponto
    if precisa_reverter:
        return caminho[::-1]
    else:
        return caminho


def _triangular(distancias):
    #Função que confirma se a matriz passada é triangular
    for i, row in enumerate(distancias):
        if len(row) < i: raise ValueError(
            "A matriz deve ser triangular. As linhas {row} devem ter ao menos {i} items".format(
                **locals()))


def pareia_pela_distancia(N, distancias):
    """retorna uma lista de pares ordenados (i,j), ordenados pela distância; sendo que i < j"""
    # ordena os pares de coordenadas de acordo com a distância
    indices = []
    for i in xrange(N):
        for j in xrange(i):
            indices.append(i * N + j)

    indices.sort(key=lambda ij: distancias[ij // N][ij % N])
    return ((ij // N, ij % N) for ij in indices)


def resolver(distancias, passos_otimizacao=3, pareia_pela_distancia=pareia_pela_distancia, endpoints=None):
    """Dado a distância da matriz, encontra uma solução para o problema do caixeiro viajante.
    Retorna uma lista de indices de vértices.
    Garante que o primeiro indice é menor que os posteriores
    :arg: distancias : matriz de distâncias. array of arrays
    :arg: passos_otimizacao (int) número adicional loops de otimização, permite melhorar a solução mas com perda de desempenho.
    :arg: pareia_pela_distancia (function) é uma função que pareia_pela_distancia. feita com propósitos de otmização.
    :arg: endpoinds : nenhum ou um par (int or None, int or None). especifica o começo e o final. None é sem a especificação.
    """
    N = len(distancias)
    comeco, fim = endpoints or (None, None)
    # Quando os dois endpoints são especificados, significa que estamos procurando por um loop
    loop = (comeco is not None) and (comeco == fim)
    if comeco is not None and not (0 <= comeco < N): raise ValueError("O ponto de inicio especificado não pertence ao array")
    if fim is not None and not (0 <= fim < N): raise ValueError("O ponto final especificado não pertence ao array")

    if N == 0: return []
    if N == 1:
        return [0, 0] if loop else [0]
    if N == 2 and loop:
        # O número de nodos passados são muito pequenos para o loop
        return [comeco, 1 - comeco, comeco]
    _triangular(distancias)

    # Pega o estado do algoritmo de resolução do caixeiro viajante.;
    valencia_nodo = array('i', [2]) * N  # Inicialmente cada nodo tem duas extremidades para se conectar
    dois_endpoints = (comeco is not None) and (fim is not None)

    if not loop:
        # em um loop, todos os nodos tem 2 pontos de valencia. Caso contrário, os nodos de começo e fim tem 1
        if comeco is not None:
            valencia_nodo[comeco] = 1
        if fim is not None:
            valencia_nodo[fim] = 1

    # para cada node, guarda 1 ou 2 nodos conectados
    conexoes = [[] for i in xrange(N)]

    def junta_segmentos(pares_ordenados):
        # segmentos dos nodos. Inicialmente, cada segmento contém somente 1 nodo
        segmentos = [[i] for i in xrange(N)]

        def pontas_possiveis():
            # Gera uma sequência de pontas nos grafos, que são possivelmente conectados por segmentos.
            for ij in pares_ordenados:
                i, j = ij
                # se eles ambos iniciarem e terminarem é possivel uma conexão,
                #  e ambos os nodos conectam a diferentes segmentos:
                if valencia_nodo[i] and valencia_nodo[j] and \
                        (segmentos[i] is not segmentos[j]):
                    yield ij

        def vertices_conectados(i, j):
            valencia_nodo[i] -= 1
            valencia_nodo[j] -= 1
            conexoes[i].append(j)
            conexoes[j].append(i)
            # Combina o segmento J no segmento I.
            seg_i = segmentos[i]
            seg_j = segmentos[j]
            if len(seg_j) > len(seg_i):
                seg_i, seg_j = seg_j, seg_i
                i, j = j, i
            for node_idx in seg_j:
                segmentos[node_idx] = seg_i
            seg_i.extend(seg_j)

        def conexoes_segmentos_endpoint(i, j):
            # retorna verdadeiro, se dados 2 combinações de 2 segmentos que tem endpoint entre eles
            # quando isso acontece, a pesquisa termina de forma prematura.
            # Também funciona no caso dos pontos de inicio e fim sejam os mesmos.
            si, sj = segmentos[i], segmentos[j]
            ss, se = segmentos[comeco], segmentos[fim]
            return (si is ss) and (sj is se) or (sj is ss) and (si is se)

        # Pega a primeira ponta N-1 possivel. eles já estão ordenados pela distância
        pontas_esquerda = N - 1
        for i, j in pontas_possiveis():
            if dois_endpoints and pontas_esquerda != 1 and conexoes_segmentos_endpoint(i, j):
                continue  # não permite termino prematuro da pesquisa
            vertices_conectados(i, j)
            pontas_esquerda -= 1
            if pontas_esquerda == 0:
                break
        # Se está procurando por um loop, então fecha a conexão
        if loop:
            _fecha_loop(conexoes)

    # invoca o algoritmo guloso principal
    junta_segmentos(pareia_pela_distancia(N, distancias))

    # chama pelo procedimento adicional de otimização
    for passn in range(passos_otimizacao):
        nopt, dtotal = solucao_otimizada(distancias, conexoes, endpoints)
        if nopt == 0:
            break
    # restaura o caminho das conexoes no mapa (grafo) e retorna
    return caminho_inicial(conexoes, endpoints=endpoints)


def _fecha_loop(conexoes):
    """Modifica as conexões para fechar o loop"""
    i, j = (i for i, conn in enumerate(conexoes)
            if len(conn) == 1)
    conexoes[i].append(j)
    conexoes[j].append(i)