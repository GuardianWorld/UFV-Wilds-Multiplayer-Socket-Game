import pygame
import sys
import random
import os
import re


# Inicializar o Pygame
pygame.init()

# Definir cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)

################################################Telas#######################################
# Cria a janela com um tamanho e altura

def TelaLogin(janela):
    pygame.font.init()
    fonte = pygame.font.SysFont('Arial', 40)

    input_box_nome = pygame.Rect(100, 100, 200, 50)
    input_box_senha = pygame.Rect(100, 200, 200, 50)
    botao_login = pygame.Rect(100, 300, 200, 50)

    cor_ativo = pygame.Color('dodgerblue2')
    cor_inativo = pygame.Color('lightskyblue3')
    cor_botao = pygame.Color('gray15')

    cor_nome = cor_inativo
    cor_senha = cor_inativo

    ativo_nome = False
    ativo_senha = False

    texto_nome = ''
    texto_senha = ''

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                # Se o usuário clicar no campo de entrada, ativa o campo de entrada correspondente
                if input_box_nome.collidepoint(evento.pos):
                    ativo_nome = True
                    ativo_senha = False
                elif input_box_senha.collidepoint(evento.pos):
                    ativo_senha = True
                    ativo_nome = False
                elif botao_login.collidepoint(evento.pos):
                    # Retorna o nome e senha quando o botão de login é clicado
                    return texto_nome, texto_senha
                else:
                    ativo_nome = False
                    ativo_senha = False

                cor_nome = cor_ativo if ativo_nome else cor_inativo
                cor_senha = cor_ativo if ativo_senha else cor_inativo

            if evento.type == pygame.KEYDOWN:
                if ativo_nome:
                    if evento.key == pygame.K_BACKSPACE:
                        texto_nome = texto_nome[:-1]
                    else:
                        texto_nome += evento.unicode
                if ativo_senha:
                    if evento.key == pygame.K_BACKSPACE:
                        texto_senha = texto_senha[:-1]
                    else:
                        texto_senha += evento.unicode

        janela.fill(BRANCO)
        txt_surface_nome = fonte.render(texto_nome, True, PRETO)
        txt_surface_senha = fonte.render('*' * len(texto_senha), True, PRETO)

        largura_max = max(input_box_nome.width, txt_surface_nome.get_width() + 10)
        input_box_nome.w = largura_max
        input_box_senha.w = largura_max

        # Desenha os campos de texto
        janela.blit(txt_surface_nome, (input_box_nome.x + 5, input_box_nome.y + 5))
        janela.blit(txt_surface_senha, (input_box_senha.x + 5, input_box_senha.y + 5))
        pygame.draw.rect(janela, cor_nome, input_box_nome, 2)
        pygame.draw.rect(janela, cor_senha, input_box_senha, 2)

        # Desenha o botão de login
        pygame.draw.rect(janela, cor_botao, botao_login)
        texto_botao = fonte.render('Login', True, BRANCO)
        janela.blit(texto_botao, (botao_login.x + 50, botao_login.y + 5))

        pygame.display.flip()

def TelaMenuPrincipal(janela, jogador1, jogador2, jogador3):
    rodando = True
    jogador1, jogador2, jogador3 = iniciaJogadores(jogador1, jogador2, jogador3)
    fonte = pygame.font.SysFont('Arial', 50)

    # Definir áreas dos botões
    largura_botao = 200
    altura_botao = 60
    margem = 20

    botoes = {
        'sair': pygame.Rect(500, 400, largura_botao, altura_botao),
        'jogar': pygame.Rect(500, 500, largura_botao, altura_botao),
        'montar_baralho': pygame.Rect(500, 600, largura_botao, altura_botao)
    }

    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = pygame.mouse.get_pos()
                if botoes['sair'].collidepoint(mouseX, mouseY):
                    pygame.quit()
                    sys.exit()
                if botoes['jogar'].collidepoint(mouseX, mouseY):
                    JogoPrincipal(janela, [jogador1, jogador2, jogador3])
                if botoes['montar_baralho'].collidepoint(mouseX, mouseY):
                    TelaMudarBaralho(janela, [jogador1, jogador2, jogador3])

        janela.fill(BRANCO)
        titulo = fonte.render('Jogo de Cartas', True, PRETO)
        sair = fonte.render('Sair', True, PRETO)
        jogar = fonte.render('Jogar', True, PRETO)
        montar_baralho = fonte.render('Montar Baralho', True, PRETO)

        janela.blit(titulo, (450, 100))

        # Desenhar os botões
        pygame.draw.rect(janela, BRANCO, botoes['sair'])
        pygame.draw.rect(janela, BRANCO, botoes['jogar'])
        pygame.draw.rect(janela, BRANCO, botoes['montar_baralho'])

        janela.blit(sair, (botoes['sair'].x + 10, botoes['sair'].y + 10))
        janela.blit(jogar, (botoes['jogar'].x + 10, botoes['jogar'].y + 10))
        janela.blit(montar_baralho, (botoes['montar_baralho'].x + 10, botoes['montar_baralho'].y + 10))

        pygame.display.update()

#Mostra os baralhos dos jogadores para excluirem ou criarem outro


def TelaEscolherAtributo(janela, atributos, turno):
    fonte = pygame.font.SysFont('Arial', 30)
    opcoes_atributo = []

    while True:
        janela.fill(BRANCO)
        titulo = fonte.render(f'Escolha um Atributo para o Turno {turno}', True, PRETO)
        janela.blit(titulo, (50, 50))

        y_offset = 150
        for i, atributo in enumerate(atributos):
            texto_atributo = fonte.render(atributo, True, PRETO)
            retangulo_atributo = pygame.Rect(50, y_offset + i * 60, 300, 50)
            pygame.draw.rect(janela, PRETO, retangulo_atributo, 2)
            janela.blit(texto_atributo, (retangulo_atributo.x + 5, retangulo_atributo.y + 5))
            opcoes_atributo.append(retangulo_atributo)

        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = pygame.mouse.get_pos()
                for i, rect in enumerate(opcoes_atributo):
                    if rect.collidepoint(mouseX, mouseY):
                        return atributos[i]  # Retorna o atributo escolhido

def TelaEscolherCarta(janela, cartas, nome_jogador, turno, atributo = 0):
    fonte = pygame.font.SysFont('Arial', 30)
    fonte_jogador = pygame.font.SysFont('Arial', 40)
    opcoes_carta = []

    # Carregar imagens das cartas com um tamanho menor
    imagens_cartas = {}
    largura_imagem = 100  # Diminuir largura da imagem
    altura_imagem = 155  # Diminuir altura da imagem

    for carta in cartas:
        nome_imagem = carta['Imagem']
        try:
            imagem = pygame.image.load(f'cartas/{nome_imagem}.jpg')
            imagem = pygame.transform.scale(imagem, (largura_imagem, altura_imagem))
            imagens_cartas[nome_imagem] = imagem
        except pygame.error:
            q = 1

    while True:
        janela.fill(BRANCO)

        # Exibir o nome do jogador atual
        if(atributo == 0):
            texto_jogador = fonte_jogador.render(f"Turno {turno} | Escolha de: {nome_jogador}", True, PRETO)
        else:
            texto_jogador = fonte_jogador.render(f"Turno {turno} | Escolha de: {nome_jogador} | Atributo {atributo}", True, PRETO)
        janela.blit(texto_jogador, (50, 10))

        titulo = fonte.render('Escolha uma Carta', True, PRETO)
        janela.blit(titulo, (50, 70))

        # Gerar posições para as imagens das cartas
        colunas = 4
        margem = 30
        posicoes = []

        for i in range(len(cartas)):
            x = margem + (i % colunas) * (largura_imagem + margem)
            y = 200 + (i // colunas) * (altura_imagem + margem)  # Mover as cartas para mais embaixo
            posicoes.append(pygame.Rect(x, y, largura_imagem, altura_imagem))

        # Desenhar as imagens das cartas
        for idx, carta in enumerate(cartas):
            nome_imagem = carta['Imagem']
            imagem = imagens_cartas.get(nome_imagem, None)
            if imagem:
                pos = posicoes[idx]
                janela.blit(imagem, pos.topleft)

                # Adicionar borda para a carta selecionada
                if carta in opcoes_carta:
                    pygame.draw.rect(janela, (255, 0, 0), pos, 3)  # Borda vermelha para a carta selecionada

        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = pygame.mouse.get_pos()
                for idx, pos in enumerate(posicoes):
                    if pos.collidepoint(mouseX, mouseY):
                        carta = cartas[idx]
                        if carta not in opcoes_carta:
                            opcoes_carta = [carta]  # Selecionar apenas uma carta
                        else:
                            opcoes_carta = []  # Deselecionar se a mesma carta for clicada novamente

                # Verificar se o botão de confirmar seleção foi clicado
                if len(opcoes_carta) > 0:
                    return opcoes_carta[0]   # Retorna a carta escolhida

#olha a seleção de baralhos e escolhe 1

def TelaEscolherBaralho(janela, jogador):
    fonte = pygame.font.SysFont('Arial', 30)
    baralhos = jogador['baralhos']
    opcoes_baralho = []

    while True:
        janela.fill(BRANCO)
        titulo = fonte.render(f'{jogador["nome"]} - Escolha seu Baralho', True, PRETO)
        janela.blit(titulo, (50, 50))

        y_offset = 150
        for i, baralho in enumerate(baralhos):
            texto_baralho = fonte.render(baralho['nome'], True, PRETO)
            retangulo_baralho = pygame.Rect(50, y_offset + i * 60, 300, 50)
            pygame.draw.rect(janela, PRETO, retangulo_baralho, 2)
            janela.blit(texto_baralho, (retangulo_baralho.x + 5, retangulo_baralho.y + 5))
            opcoes_baralho.append(retangulo_baralho)

        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = pygame.mouse.get_pos()
                for i, rect in enumerate(opcoes_baralho):
                    if rect.collidepoint(mouseX, mouseY):
                        return baralhos[i]  # Retorna o baralho escolhido


def TelaVencedor(janela, nome_jogador_vencedor, turno):
    pygame.font.init()
    fonte = pygame.font.SysFont('Arial', 40)
    fonte_botao = pygame.font.SysFont('Arial', 30)

    # Cor do botão e do texto
    cor_botao = (0, 128, 0)  # Verde
    cor_texto_botao = (255, 255, 255)  # Branco

    # Exibe o nome do jogador vencedor
    janela.fill((255, 255, 255))  # Fundo branco
    texto_vencedor = fonte.render(f"O jogador: {nome_jogador_vencedor} Foi o vencedor do Turno {turno}", True, (0, 0, 0))
    janela.blit(texto_vencedor, (50, 50))

    # Desenha o botão "Continuar"
    largura_botao = 200
    altura_botao = 50
    x_botao = (janela.get_width() - largura_botao) // 2
    y_botao = janela.get_height() - altura_botao - 50
    pygame.draw.rect(janela, cor_botao, pygame.Rect(x_botao, y_botao, largura_botao, altura_botao))
    texto_botao = fonte_botao.render("Continuar", True, cor_texto_botao)
    janela.blit(texto_botao, (x_botao + 50, y_botao + 10))

    pygame.display.update()

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = pygame.mouse.get_pos()
                if (x_botao < mouseX < x_botao + largura_botao and
                    y_botao < mouseY < y_botao + altura_botao):
                    return  # Retorna à tela principal

def TelaMudarBaralho(janela, jogadores):
    fonte = pygame.font.SysFont('Arial', 30)
    caixas_texto = [
        {'rect': pygame.Rect(100, 100, 300, 50), 'texto': 'Montar Baralho Jogador 1', 'jogador': jogadores[0]},
        {'rect': pygame.Rect(100, 200, 300, 50), 'texto': 'Montar Baralho Jogador 2', 'jogador': jogadores[1]},
        {'rect': pygame.Rect(100, 300, 300, 50), 'texto': 'Montar Baralho Jogador 3', 'jogador': jogadores[2]},
    ]

    # Adicionar botão de voltar
    largura_botao_voltar = 200
    altura_botao_voltar = 50
    botao_voltar = pygame.Rect(10, janela.get_height() - altura_botao_voltar - 10, largura_botao_voltar,
                               altura_botao_voltar)
    texto_botao_voltar = fonte.render('Voltar ao Menu', True, (255, 255, 255))

    rodando = True

    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = pygame.mouse.get_pos()
                # Verificar se o botão de voltar foi clicado
                if botao_voltar.collidepoint(mouseX, mouseY):
                    rodando = False
                    TelaMenuPrincipal(janela, jogadores[0], jogadores[1], jogadores[2])  # Função para retornar ao menu principal

                for caixa in caixas_texto:
                    if caixa['rect'].collidepoint(mouseX, mouseY):
                        jogador = caixa['jogador']  # Obter o jogador da caixa de texto
                        TelaMontarBaralhoJogador(janela, jogador)

        janela.fill((255, 255, 255))  # Cor de fundo branca

        # Desenhar os botões dos baralhos existentes
        for caixa in caixas_texto:
            pygame.draw.rect(janela, (0, 0, 0), caixa['rect'], 2)
            texto = fonte.render(caixa['texto'], True, (0, 0, 0))
            janela.blit(texto, (caixa['rect'].x + 5, caixa['rect'].y + 5))

        # Desenhar o botão de voltar
        pygame.draw.rect(janela, (255, 0, 0), botao_voltar)  # Botão vermelho
        janela.blit(texto_botao_voltar, (botao_voltar.x + 5, botao_voltar.y + 10))

        pygame.display.update()


def TelaSelecionarCartas(janela, todasCartas):
    fonte = pygame.font.SysFont('Arial', 20)
    cartas_selecionadas = []
    imagens_cartas = {}

    # Carregar imagens das cartas com um tamanho menor
    for nome in todasCartas:
        try:
            imagem = pygame.image.load(f'cartas/{nome}.jpg')
            imagem = pygame.transform.scale(imagem, (80, 120))  # Reduzir o tamanho das imagens
            imagens_cartas[nome] = imagem
        except pygame.error:
                p= 1
    # Gerar posições para as imagens das cartas
    colunas = 5
    margem = 10
    largura_imagem = 80
    altura_imagem = 120
    posicoes = []

    for i in range(len(todasCartas)):
        x = margem + (i % colunas) * (largura_imagem + margem)
        y = margem + (i // colunas) * (altura_imagem + margem)
        posicoes.append(pygame.Rect(x, y, largura_imagem, altura_imagem))

    # Botão para confirmar a seleção
    largura_botao = 200
    altura_botao = 50
    botao_confirmar = pygame.Rect(10, janela.get_height() - altura_botao - 10, largura_botao, altura_botao)
    texto_botao = fonte.render('Confirmar Seleção', True, (255, 255, 255))

    rodando = True

    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = pygame.mouse.get_pos()
                if evento.button == 1:  # Botão esquerdo do mouse
                    for idx, pos in enumerate(posicoes):
                        if pos.collidepoint(mouseX, mouseY):
                            carta_nome = todasCartas[idx]
                            # Adicionar carta se ainda não houver 4 cartas selecionadas no total
                            if len(cartas_selecionadas) < 9:
                                if cartas_selecionadas.count(carta_nome) < 8:
                                    cartas_selecionadas.append(carta_nome)
                elif evento.button == 3:  # Botão direito do mouse
                    for idx, pos in enumerate(posicoes):
                        if pos.collidepoint(mouseX, mouseY):
                            carta_nome = todasCartas[idx]
                            # Remover carta se estiver presente na lista
                            if carta_nome in cartas_selecionadas:
                                cartas_selecionadas.remove(carta_nome)

                # Verificar se o botão de confirmar seleção foi clicado
                if botao_confirmar.collidepoint(mouseX, mouseY) and len(cartas_selecionadas) > 0:
                    rodando = False

        janela.fill((255, 255, 255))  # Cor de fundo branca

        # Desenhar as imagens das cartas
        for idx, nome in enumerate(todasCartas):
            imagem = imagens_cartas[nome]
            pos = posicoes[idx]
            janela.blit(imagem, pos.topleft)
            # Destacar as cartas selecionadas
            count = cartas_selecionadas.count(nome)
            if count > 0:
                if count == 1:
                    pygame.draw.rect(janela, (0, 0, 255), pos, 3)  # Borda azul para 1 carta
                elif count == 2:
                    pygame.draw.rect(janela, (255, 255, 0), pos, 3)  # Borda amarela para 2 cartas
                elif count == 3:
                    pygame.draw.rect(janela, (255, 0, 0), pos, 3)  # Borda vermelha para 3 cartas

        # Desenhar o botão de confirmação
        pygame.draw.rect(janela, (0, 0, 255), botao_confirmar)  # Botão azul
        janela.blit(texto_botao, (botao_confirmar.x + 5, botao_confirmar.y + 10))

        pygame.display.update()

    return cartas_selecionadas


def TelaMostrarCartasBaralho(janela, baralho, jogador):
    fonte = pygame.font.SysFont('Arial', 20)
    imagens_cartas = {}
    posicoes = []
    margem = 10
    largura_imagem = 80
    altura_imagem = 120
    colunas = 5


    for i, carta in enumerate(baralho['cartas']):
        nome_imagem = carta['Imagem']
        try:
            imagem = pygame.image.load(f'cartas/{nome_imagem}.jpg')
            imagem = pygame.transform.scale(imagem, (largura_imagem, altura_imagem))  # Reduzir o tamanho das imagens
            imagens_cartas[nome_imagem] = imagem
        except pygame.error:
            q = 1

    # Gerar posições para as imagens das cartas
    for i in range(len(baralho['cartas'])):
        x = margem + (i % colunas) * (largura_imagem + margem)
        y = margem + (i // colunas) * (altura_imagem + margem)
        posicoes.append(pygame.Rect(x, y, largura_imagem, altura_imagem))

    # Botão de voltar
    largura_botao_voltar = 200
    altura_botao_voltar = 50
    botao_voltar = pygame.Rect(10, janela.get_height() - altura_botao_voltar - 10, largura_botao_voltar,
                               altura_botao_voltar)
    texto_botao_voltar = fonte.render('Voltar', True, (255, 255, 255))

    # Botão de excluir baralho
    largura_botao_excluir = 200
    altura_botao_excluir = 50
    botao_excluir = pygame.Rect(janela.get_width() - largura_botao_excluir - 10,
                                janela.get_height() - altura_botao_excluir - 10, largura_botao_excluir,
                                altura_botao_excluir)
    texto_botao_excluir = fonte.render('Excluir Baralho', True, (255, 255, 255))

    rodando = True

    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = pygame.mouse.get_pos()

                # Verificar se o botão de voltar foi clicado
                if botao_voltar.collidepoint(mouseX, mouseY):
                    rodando = False

                # Verificar se o botão de excluir baralho foi clicado
                if botao_excluir.collidepoint(mouseX, mouseY):
                    if len(jogador["baralhos"]) > 1:
                        jogador["baralhos"].remove(baralho)
                        return  # Retorna para atualizar a lista de baralhos
                    else:
                        p = 1

        janela.fill((255, 255, 255))  # Cor de fundo branca

        # Desenhar as imagens das cartas
        for i, carta in enumerate(baralho['cartas']):
            nome_imagem = carta['Imagem']
            imagem = imagens_cartas[nome_imagem]
            pos = posicoes[i]
            janela.blit(imagem, pos.topleft)

        # Desenhar o botão de voltar
        pygame.draw.rect(janela, (255, 0, 0), botao_voltar)  # Botão vermelho
        janela.blit(texto_botao_voltar, (botao_voltar.x + 5, botao_voltar.y + 10))

        # Desenhar o botão de excluir baralho
        pygame.draw.rect(janela, (255, 0, 0), botao_excluir)  # Botão vermelho
        janela.blit(texto_botao_excluir, (botao_excluir.x + 5, botao_excluir.y + 10))

        pygame.display.update()

def TelaMontarBaralhoJogador(janela, jogador):
    fonte = pygame.font.SysFont('Arial', 30)
    caixas_texto = []
    # Função para atualizar a lista de baralhos
    def atualizar_botoes():
        caixas_texto.clear()
        for i, baralho in enumerate(jogador["baralhos"]):
            caixa = {
                'rect': pygame.Rect(100, 100 + i * 60, 300, 50),
                'texto': f'Mudar Baralho {baralho["nome"]}',
                'baralho': baralho
            }
            caixas_texto.append(caixa)

        # Adicionar botão para criar um novo baralho
        nova_posicao = 100 + len(jogador["baralhos"]) * 60
        caixa_novo = {
            'rect': pygame.Rect(100, nova_posicao, 300, 50),
            'texto': 'Criar Novo Baralho',
            'baralho': None
        }
        caixas_texto.append(caixa_novo)

    atualizar_botoes()  # Inicializa os botões

    # Adicionar botão de voltar
    largura_botao_voltar = 200
    altura_botao_voltar = 50
    botao_voltar = pygame.Rect(10, janela.get_height() - altura_botao_voltar - 10, largura_botao_voltar,
                               altura_botao_voltar)
    texto_botao_voltar = fonte.render('Voltar', True, (255, 255, 255))

    rodando = True

    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = pygame.mouse.get_pos()
                for caixa in caixas_texto:
                    if caixa['rect'].collidepoint(mouseX, mouseY):
                        if caixa['baralho']:
                            # Mostrar as cartas do baralho selecionado
                            TelaMostrarCartasBaralho(janela, caixa['baralho'], jogador)
                            atualizar_botoes()  # Atualizar a lista de baralhos após a exclusão
                        else:
                            # Criar um novo baralho
                            cartas_selecionadas = TelaSelecionarCartas(janela, jogador["todasCartas"])
                            cartas_selecionadas = iniciaBaralho(cartas_selecionadas)
                            if len(cartas_selecionadas) > 0:
                                novo_baralho = {
                                    "nome": f"Baralho {len(jogador['baralhos']) + 1}",
                                    "cartas": [carta for carta in cartas_selecionadas]
                                }
                                jogador["baralhos"].append(novo_baralho)
                                atualizar_botoes()  # Atualizar a lista de baralhos após a criação

                # Verificar se o botão de voltar foi clicado
                if botao_voltar.collidepoint(mouseX, mouseY):
                    rodando = False

        janela.fill((255, 255, 255))  # Cor de fundo branca

        # Desenhar os botões dos baralhos existentes e o botão de criar novo baralho
        for caixa in caixas_texto:
            pygame.draw.rect(janela, (0, 0, 0), caixa['rect'], 2)
            texto = fonte.render(caixa['texto'], True, (0, 0, 0))
            janela.blit(texto, (caixa['rect'].x + 5, caixa['rect'].y + 5))

        # Desenhar o botão de voltar
        pygame.draw.rect(janela, (255, 0, 0), botao_voltar)  # Botão vermelho
        janela.blit(texto_botao_voltar, (botao_voltar.x + 5, botao_voltar.y + 10))

        pygame.display.update()

def TelaVencedorFinal(janela, nome_vencedor, jogador1, jogador2, jogador3):
    # Fonte para o texto do vencedor
    fonte_vencedor = pygame.font.SysFont('Arial', 60)
    fonte_botao = pygame.font.SysFont('Arial', 40)

    while True:
        janela.fill(BRANCO)
        texto_vencedor = fonte_vencedor.render(f"Vencedor: {nome_vencedor}", True, PRETO)
        janela.blit(texto_vencedor, (janela.get_width() // 2 - texto_vencedor.get_width() // 2, 150))

        # Desenha o botão de voltar ao menu principal
        botao_rect = pygame.Rect(janela.get_width() // 2 - 100, 300, 200, 60)
        pygame.draw.rect(janela, PRETO, botao_rect)
        texto_botao = fonte_botao.render("Voltar ao Menu", True, BRANCO)
        janela.blit(texto_botao, (janela.get_width() // 2 - texto_botao.get_width() // 2, 315))

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if botao_rect.collidepoint(evento.pos):
                    TelaMenuPrincipal(janela, jogador1, jogador2, jogador3)


######################################################Lógica#########################################

def iniciaJogadores(jogador1, jogador2, jogador3):
    jogadores = []
    baralhos = []

    jogadores.append(jogador1)
    if(len(jogador1['baralhos']) == 0):
        novoBaralho = iniciaBaralho(jogador1['todasCartas'])
        jogador1["baralhos"].append({
            "nome": "Baralho1",
            "cartas": novoBaralho
        })
    baralhos.append(jogador1['baralhos'][0])

    jogadores.append(jogador2)
    if (len(jogador2['baralhos']) == 0):
        novoBaralho = iniciaBaralho(jogador2['todasCartas'])
        jogador2["baralhos"].append({
            "nome": "Baralho1",
            "cartas": novoBaralho
        })
    baralhos.append(jogador2['baralhos'][0])

    if (jogador3 != 0):
        jogadores.append(jogador3)
        if (len(jogador3['baralhos']) == 0):
            novoBaralho = iniciaBaralho(jogador3['todasCartas'])
            jogador3["baralhos"].append({
                "nome": "Baralho1",
                "cartas": novoBaralho
            })
        baralhos.append(jogador3['baralhos'][0])

    return jogadores[0], jogadores[1], jogadores[2]


def iniciaJanela(largura_janela, altura_janela):
    janela = pygame.display.set_mode((largura_janela, altura_janela))
    pygame.display.set_caption('Jogo de Cartas')
    return janela

def escolherBaralhosJogadores(jogador, janela):
    baralho = TelaEscolherBaralho(janela, jogador)
    return baralho


def mostraCarta(janela, carta, posX, posY):
    alt = 150
    larg = 100
    carta_img = pygame.transform.scale(pygame.image.load(carta['imagem']), (alt, larg))
    carta_rect = carta_img.get_rect(topleft=(posX, posY))
    janela.blit(carta_img, carta_rect)
    return carta_rect


def iniciaBaralho(cartas_strings):

    cartas = []
    padrao = re.compile(r'(\d+)_(\d+)_(\d+)_([a-zA-Z]+)_([a-zA-Z]+)_([a-zA-Z]+)')

    for i in range(len(cartas_strings)):
        carta_string = cartas_strings[i]
        correspondencia = padrao.match(carta_string)
        if correspondencia:
            atributos = correspondencia.groups()
            carta = {
                'Forca': int(atributos[0]),
                'Fofura': int(atributos[1]),
                'Velocidade': int(atributos[2]),
                'Tamanho': atributos[3],
                'Idade': atributos[4],
                'Tipo': atributos[5],
                'Imagem': carta_string
            }
            cartas.append(carta)

    return cartas

def comprarCartas(mao, baralho):
    # Embaralha o baralho
    try:
        random.shuffle(baralho)
    except:
        a = 1

    num_cartas = 3
    if(len(baralho) < 3):
        num_cartas = len(baralho)


    # Adiciona cartas à mão conforme disponível no baralho
    for _ in range(num_cartas):
        if baralho:  # Verifica se o baralho não está vazio
            mao.append(baralho.pop())  # Remove a última carta e adiciona à mão

    return mao, baralho

def Jogar(janela, jogadores, Mao1, Mao2, Mao3, turno):
    ordem_tamanho = ['minusculo', 'pequeno', 'medio', 'grande', 'enorme']
    ordem_idade = ['jovem', 'adolescente', 'adulto', 'anciao']
    ordem_tipo = ['aquatico', 'voador', 'terrestre']

    # Inicialização da fonte
    pygame.font.init()
    fonte_jogador = pygame.font.SysFont('Arial', 40)

    # Cria uma lista de mãos para facilitar o acesso por índice
    Maos = [Mao1, Mao2, Mao3]
    cartas_vencedoras = []

    JogadorAleatorio = random.randint(0, 2)
    nome_jogador_aleatorio = jogadores[JogadorAleatorio]['nome']
    mao_jogadorAleatorio = Maos[JogadorAleatorio]

    # Exibir texto com o nome do jogador
    texto_jogador = fonte_jogador.render(f"Vez do Jogador: {nome_jogador_aleatorio} no Turno {turno}", True, (0, 0, 0))
    janela.blit(texto_jogador, (50, 10))

    carta_escolhida_aleatoria = TelaEscolherCarta(janela, mao_jogadorAleatorio, nome_jogador_aleatorio, turno)
    Maos[JogadorAleatorio].remove(carta_escolhida_aleatoria)
    cartas_vencedoras.append(carta_escolhida_aleatoria)

    atributo_escolhido = TelaEscolherAtributo(janela, ['Forca', 'Fofura', 'Velocidade', 'Tamanho', 'Idade', 'Tipo'], turno)

    # Mapeamento dos atributos
    if atributo_escolhido == 'Tamanho':
        valor_atributo_aleatorio = ordem_tamanho.index(carta_escolhida_aleatoria[atributo_escolhido])
    elif atributo_escolhido == 'Idade':
        valor_atributo_aleatorio = ordem_idade.index(carta_escolhida_aleatoria[atributo_escolhido])
    elif atributo_escolhido == 'Tipo':
        valor_atributo_aleatorio = ordem_tipo.index(carta_escolhida_aleatoria[atributo_escolhido])
    else:
        valor_atributo_aleatorio = carta_escolhida_aleatoria[atributo_escolhido]


    valores_atributos = [valor_atributo_aleatorio]
    cartas_escolhidas = [carta_escolhida_aleatoria]
    indices_jogadores = [JogadorAleatorio]

    for i in range(3):
        if i == JogadorAleatorio:
            continue
        nome_jogador = jogadores[i]['nome']
        mao_jogadorOutro = Maos[i]
        carta_escolhida = TelaEscolherCarta(janela, mao_jogadorOutro, nome_jogador, turno, atributo_escolhido)
        if carta_escolhida:
            if atributo_escolhido == 'Tamanho':
                valor_atributo_outro = ordem_tamanho.index(carta_escolhida[atributo_escolhido])
            elif atributo_escolhido == 'Idade':
                valor_atributo_outro = ordem_idade.index(carta_escolhida[atributo_escolhido])
            elif atributo_escolhido == 'Tipo':
                valor_atributo_outro = ordem_tipo.index(carta_escolhida_aleatoria[atributo_escolhido])
            else:
                valor_atributo_outro = carta_escolhida[atributo_escolhido]

            valores_atributos.append(valor_atributo_outro)
            cartas_escolhidas.append(carta_escolhida)
            indices_jogadores.append(i)
            Maos[i].remove(carta_escolhida)
            cartas_vencedoras.append(carta_escolhida)

    max_valor = max(valores_atributos)
    vencedores = [i for i, valor in enumerate(valores_atributos) if valor == max_valor]
    vencedor_aleatorio = random.choice(vencedores)
    jogador_vencedor_index = indices_jogadores[vencedor_aleatorio]
    jogador_vencedor = jogadores[jogador_vencedor_index]


    # Adicionar todas as cartas vencedoras à mão do jogador vencedor
    Maos[jogador_vencedor_index].extend(cartas_vencedoras)

    return jogador_vencedor['nome'], Mao1, Mao2, Mao3

def JogoPrincipal(janela, jogadores):
    Baralhos = []  # Lista para armazenar todos os baralhos escolhidos
    Mao1 = []
    Mao2 = []
    Mao3 = []

    # Jogar turno para cada jogador na ordem
    for jogador in jogadores:
        baralho = escolherBaralhosJogadores(jogador, janela)
        Baralhos.append(baralho)

    turno = 0
    while True:


        # Adiciona cartas para os jogadores e atualiza os baralhos
        Mao1, Baralhos[0]['cartas'] = comprarCartas(Mao1, Baralhos[0]['cartas'])
        Mao2, Baralhos[1]['cartas'] = comprarCartas(Mao2, Baralhos[1]['cartas'])
        Mao3, Baralhos[2]['cartas'] = comprarCartas(Mao3, Baralhos[2]['cartas'])

        turno += 1
        jogador_vencedor, Mao1, Mao2, Mao3 = Jogar(janela, jogadores, Mao1, Mao2, Mao3, turno)

        # Adiciona as cartas das mãos ao baralho e limpa as mãos
        Baralhos[0]['cartas'].extend(Mao1)
        Baralhos[1]['cartas'].extend(Mao2)
        Baralhos[2]['cartas'].extend(Mao3)

        Mao1.clear()
        Mao2.clear()
        Mao3.clear()

        TelaVencedor(janela, jogador_vencedor, turno)

    # Determina o jogador com mais cartas e declara-o vencedor
    num_cartas = [len(baralho['cartas']) for baralho in Baralhos]
    vencedor_index = num_cartas.index(max(num_cartas))
    jogador_vencedor_final = jogadores[vencedor_index]

    # Tela de vencedor final
    TelaVencedorFinal(janela, jogador_vencedor_final['nome'], jogadores[0], jogadores[1], jogadores[2])

    pygame.quit()
    sys.exit()



