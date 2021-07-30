import sqlite3
import re
import os
import operator
from django.shortcuts import render


def historico(carta, tree=[], index=[1]):
    # Função recursiva para coletar todas as cartas anteriores; armazena historico em tree
    # index: [1,1]; [1,1,2]; ... Organiza posição da carta na tree

    # Conecta com o arquivo database
    connection = sqlite3.connect("historico/cartas.db")   # conecta com a database
    c = connection.cursor()

    # Checa se há cartas anteriores:
    query = c.execute("SELECT anterior FROM referencias WHERE referencias.carta = ?",[carta]).fetchall()

    # Entra se carta não tem nenhuma anterior
    if len(query) == 0:
        # Anexa a lista, com respectiva index
        tree.append([index, carta])
        
        return

    j=1
    for i in range(len(query)):
        # Adiciona o index correspondente da child entre todas as referências da parent
        index_copy = index[:]           # Atribuição de valor com = para evitar mudança na variável original 'index'
        index_copy.append(j)
        # Chama a função recursivamente na carta child, com o respectivo index
        historico(query[i][0], tree, index_copy)
        j+=1

    # Anexa a lista a carta parent, após anexar todas as suas children
    tree.append([index,carta])

    return


def idToCarta(tree):
    # Itera pela lista e converte ids de cartas para nomes
    # Conecta com o arquivo database
    connection = sqlite3.connect("historico/cartas.db")   # conecta com a database
    c = connection.cursor()
    
    for i, item in enumerate(tree):
        # Coleta id da carta
        carta = item[1]
        # Coleta o nome da carta
        nome = c.execute("SELECT numero FROM cartas WHERE cartas.id = ?",[carta]).fetchall()[0][0]
        # Muda de id para número da carta
        tree[i][1] = nome        

    return tree


def index(request):
    if request.method == 'POST':

        # SQL commands
        connection = sqlite3.connect("historico/cartas.db")   # conecta com a database
        c = connection.cursor()

        # Igual ao método GET:
        # Coleta todas as cartas disponíveis para verificação client-side do form
        cartas = c.execute("SELECT numero FROM cartas").fetchall()
        # Tratamento da lista de cartas
        aux = []
        for carta in cartas:
            aux += carta
        cartas = aux

        carta = request.POST["carta"]

        # Checa se carta inserida é válida
        carta = re.sub("/","-",carta)

        id = c.execute("SELECT id FROM cartas WHERE cartas.numero = ?", [carta]).fetchall()

        if len(id) == 0:
            alerta = "Carta não encontrada!"
            return render(request, "historico/index.html", {
                "alerta": alerta
            })

        # Variável original que guarda lista das cartas
        tree = []
        historico(id[0][0], tree)     # Chama a função com a id da carta escolhida

        # Tratamento do índice de cada carta na tree
        for carta in tree:
            for i in range(len(carta[0])):
                carta[0][i] = str(carta[0][i])
            carta[0] = '.'.join(carta[0])

        # Converte ids da lista para nome da carta
        anteriores = idToCarta(tree)

        # Ordenação da ordem das cartas na lista
        anteriores = sorted(anteriores, key=operator.itemgetter(0))

        # Geração do HTML content para visualização da árvore de cartas
        content = ''
        quebra = '</br>'
        tab = '&#9;'
        # Adiciona carta principal
        content += '<pre>' + anteriores[0][1]       # <pre> previne de colapsar múltiplos tabs
        # Conta a identação atual do loop
        cont = 0
        # Itera por cada carta
        for i in range(1,len(anteriores)):
            # Opção 1: Quebra de linha e identação maior
            if len(anteriores[i][0]) > len(anteriores[i-1][0]):
                content += quebra + tab*(cont+1) + anteriores[i][1]
                cont += 1
            # Opção 2: Quebra de linha e identação igual
            elif len(anteriores[i][0]) == len(anteriores[i-1][0]):
                content += quebra + tab*cont + anteriores[i][1]
            # Opção 3: Quebra de linha e identação menor
            else:
                # Calcula a identação necessária para próxima linha
                def contaTab(index):
                    tabs = int(len(index)/2)
                    return tabs
                cont = contaTab(anteriores[i][0])
                content += quebra + tab*cont + anteriores[i][1]
        # Finalização do HTML contendo toda a árvore de cartas
        content += '</pre>'

        return render(request, "historico/index.html", {
            "cartas": cartas,
            "anteriores": content
        })

    else:

        # SQL commands
        connection = sqlite3.connect("historico/cartas.db")   # conecta com a database
        c = connection.cursor()

        # Coleta todas as cartas disponíveis para verificação client-side do form
        cartas = c.execute("SELECT numero FROM cartas").fetchall()

        # Tratamento da lista de cartas
        aux = []
        for carta in cartas:
            aux += carta
        cartas = aux

        # method == "GET"
        return render(request, "historico/index.html", {
            "cartas": cartas
        })

