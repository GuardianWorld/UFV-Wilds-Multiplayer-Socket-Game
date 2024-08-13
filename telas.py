import pygame
import sys
import random
import math
import numpy as np
from time import sleep


# Inicializar o Pygame
pygame.init()

# Definir cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)

################################################Telas#######################################
# Cria a janela com um tamanho e altura

def Fechar(message_queue):
    message_queue.put("exit")
    pygame.quit()
    sys.exit()

def TelaLogin(janela, message_queue, response_queue, imagemFundo):
    pygame.font.init()
    fonte = pygame.font.SysFont('Arial', 40)

    # Carrega a imagem de fundo
    fundo = pygame.image.load(imagemFundo)
    fundo = pygame.transform.scale(fundo, janela.get_size())

    largura_janela, altura_janela = janela.get_size()

    # Centraliza as caixas de texto e botões
    input_box_nome = pygame.Rect((largura_janela - 200) // 2, altura_janela // 3, 200, 50)
    input_box_senha = pygame.Rect((largura_janela - 200) // 2, altura_janela // 3 + 80, 200, 50)
    botao_login = pygame.Rect((largura_janela - 200) // 2, altura_janela // 3 + 160, 200, 50)
    botao_registrar = pygame.Rect((largura_janela - 200) // 2, altura_janela // 3 + 240, 200, 50)

    cor_ativo = pygame.Color('dodgerblue2')
    cor_inativo = pygame.Color('lightskyblue3')
    cor_botao = pygame.Color('gray15')
    cor_caixa_texto = pygame.Color('white')

    cor_nome = cor_inativo
    cor_senha = cor_inativo

    ativo_nome = False
    ativo_senha = False

    texto_nome = ''
    texto_senha = ''

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                Fechar(message_queue)
            if evento.type == pygame.MOUSEBUTTONDOWN:
                # Se o usuário clicar no campo de entrada, ativa o campo de entrada correspondente
                if input_box_nome.collidepoint(evento.pos):
                    ativo_nome = True
                    ativo_senha = False
                elif input_box_senha.collidepoint(evento.pos):
                    ativo_senha = True
                    ativo_nome = False
                elif botao_login.collidepoint(evento.pos):
                    # Retorna o nome, senha e 0 para login
                    return texto_nome, texto_senha
                elif botao_registrar.collidepoint(evento.pos):
                    # Retorna o nome, senha e 1 para registrar
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

        janela.blit(fundo, (0, 0))
        txt_surface_nome = fonte.render(texto_nome, True, PRETO)
        txt_surface_senha = fonte.render('*' * len(texto_senha), True, PRETO)

        largura_max = max(input_box_nome.width, txt_surface_nome.get_width() + 10)
        input_box_nome.w = largura_max
        input_box_senha.w = largura_max

        # Desenha os campos de texto com fundo branco
        pygame.draw.rect(janela, cor_caixa_texto, input_box_nome)
        pygame.draw.rect(janela, cor_caixa_texto, input_box_senha)
        janela.blit(txt_surface_nome, (input_box_nome.x + 5, input_box_nome.y + 5))
        janela.blit(txt_surface_senha, (input_box_senha.x + 5, input_box_senha.y + 5))
        pygame.draw.rect(janela, cor_nome, input_box_nome, 2)
        pygame.draw.rect(janela, cor_senha, input_box_senha, 2)

        # Desenha o botão de login
        pygame.draw.rect(janela, cor_botao, botao_login)
        texto_botao_login = fonte.render('Login', True, BRANCO)
        janela.blit(texto_botao_login, (botao_login.x + 50, botao_login.y + 5))

        # Desenha o botão de registrar
        pygame.draw.rect(janela, cor_botao, botao_registrar)
        texto_botao_registrar = fonte.render('Registrar', True, BRANCO)
        janela.blit(texto_botao_registrar, (botao_registrar.x + 35, botao_registrar.y + 5))

        pygame.display.flip()

def TelaMenuPrincipal(janela, message_queue, response_queue, imagemFundo):
    rodando = True
    fonte_titulo = pygame.font.SysFont('Arial', 100, bold=True)  # Título maior e em negrito
    fonte_botoes = pygame.font.SysFont('Arial', 50)

    # Carrega a imagem de fundo
    fundo = pygame.image.load(imagemFundo)
    fundo = pygame.transform.scale(fundo, janela.get_size())

    # Definir áreas dos botões
    largura_botao = 200
    altura_botao = 60

    botoes = {
        'Jogar': pygame.Rect(500, 400, largura_botao, altura_botao),
        'Baralhos': pygame.Rect(500, 500, largura_botao, altura_botao),
        'Sair': pygame.Rect(500, 600, largura_botao, altura_botao)
    }

    cores_botoes = {
        'Jogar': (0, 128, 255),  # Azul
        'Baralhos': (255, 165, 0),  # Laranja
        'Sair': (255, 69, 0)  # Vermelho
    }

    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                Fechar(message_queue)
            if evento.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = pygame.mouse.get_pos()
                if botoes['Sair'].collidepoint(mouseX, mouseY):
                    return 0
                if botoes['Jogar'].collidepoint(mouseX, mouseY):
                    if(response_queue.qsize == 1):
                        response_queue.get()
                    return 2
                if botoes['Baralhos'].collidepoint(mouseX, mouseY):
                    if(response_queue.qsize == 1):
                        response_queue.get()
                    return 1

        janela.blit(fundo, (0, 0))

        # Renderizar e desenhar o título maior e mais destacado
        titulo = fonte_titulo.render('UFV WILDS', True, (255, 255, 255))  # Branco
        titulo_rect = titulo.get_rect(center=(janela.get_width() // 2, 150))
        janela.blit(titulo, titulo_rect)

        # Desenhar os botões com cores diferentes
        for chave, botao in botoes.items():
            pygame.draw.rect(janela, cores_botoes[chave], botao)
            texto_botao = fonte_botoes.render(chave.replace('_', ' ').capitalize(), True, (255, 255, 255))
            texto_botao_rect = texto_botao.get_rect(center=botao.center)
            janela.blit(texto_botao, texto_botao_rect)

        pygame.display.update()

def TelaCarregamento(janela, pathImagemTelaPrincipal, message_queue, response_queue):
    # Definições de constantes
    BRANCO = (255, 255, 255)
    AZUL = (0, 0, 255)
    CINZA = (169, 169, 169)
    LARGURA_CIRCULO = 50
    VELOCIDADE_ANIMACAO = 5
    largura_tela = janela.get_width()
    altura_tela = janela.get_height()
    try:
        imagem_fundo = pygame.image.load(pathImagemTelaPrincipal).convert()
        imagem_fundo = pygame.transform.scale(imagem_fundo, (largura_tela, altura_tela))
    except pygame.error as e:
        print(f"Erro ao carregar a imagem de fundo: {e}")
        Fechar(message_queue)

    fonte = pygame.font.Font(None, 74)
    texto_carregando = fonte.render('Carregando...', True, CINZA)
    texto_rect = texto_carregando.get_rect(center=(largura_tela // 2, altura_tela // 2))

    message_queue.put("match_search")
    resposta = response_queue.get()

    while True:
        janela.blit(imagem_fundo, (0, 0))  # Desenha a imagem de fundo
        janela.blit(texto_carregando, texto_rect)  # Desenha a mensagem "Carregando..."

        pygame.display.flip()

        if(resposta[0] == "Match started"):
            return 1
        elif(not response_queue.empty()):
            resposta = response_queue.get()

        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Fechar(message_queue)

def TelaPartida(janela, turnos, imagemPantano, message_queue, response_queue):
    # Definições de constantes
    LARGURA_CARTA = 250  # Aumenta o tamanho das cartas
    ALTURA_CARTA = 350  # Aumenta o tamanho das cartas
    MARGEM = 30  # Margem entre as cartas
    MARGEM_SUPERIOR = 50  # Margem superior
    LARGURA_BOTAO = 200
    ALTURA_BOTAO = 50
    BRANCO = (255, 255, 255)
    PRETO = (0, 0, 0)
    AMARELO = (255, 255, 0)
    VERDE = (0, 255, 0)
    VERMELHO = (255, 0, 0)

    largura_tela = janela.get_width()
    altura_tela = janela.get_height()

    # Coordenadas das cartas ajustadas para centralizar
    pos_x = (largura_tela - (LARGURA_CARTA * 3 + MARGEM * 2)) // 2  # Ajusta a posição x
    pos_y = (altura_tela - ALTURA_CARTA) // 2  # Centraliza a posição y
    pos_y_botoes = altura_tela - (ALTURA_BOTAO + 30)  # Posição do botão na parte inferior

    # Carregar imagem de fundo
    try:
        fundo = pygame.image.load(imagemPantano).convert()
        fundo = pygame.transform.scale(fundo, (largura_tela, altura_tela))
    except pygame.error as e:
        print(f"Erro ao carregar a imagem de fundo: {e}")
        Fechar(message_queue)
        
    fonte = pygame.font.Font(None, 74)
    fonte_titulo = pygame.font.Font(None, 50) 

    selecao = None

    turno = response_queue.get()
    baralho, mao = response_queue.get()

    # Recupera a imagem das cartas
    paths = []
    for i in range(3):
        paths.append(mao[i][9])
    imagens_cartas = [pygame.image.load(path[1:]).convert_alpha() for path in paths]

    atributo_selecionado = False
    atributo = ""
    fim_turno = False

    if turno == "Your turn":
        print(response_queue.get())
    
    while True:
        if(not response_queue.empty()):
            if(response_queue.get() == "Select card"):
                atributo_selecionado = True
                atributo = response_queue.get()
        
        janela.blit(fundo, (0, 0))  # Desenha o fundo
        
        texto_turno = fonte_titulo.render(f'Turno: {turnos}', True, PRETO)  # Cor do texto do turno ajustada para preto
        texto_turno_rect = texto_turno.get_rect(center=(largura_tela // 2, MARGEM_SUPERIOR // 2))

        # Desenhar o título do turno

        # Desenho da caixa ao redor do texto
        margem_caixa = 10
        caixa_rect = texto_turno_rect.inflate(2 * margem_caixa, 2 * margem_caixa)
        caixa_rect.topleft = (texto_turno_rect.left - margem_caixa, texto_turno_rect.top - margem_caixa)

        # Desenhar a caixa branca ao redor do texto do turno
        pygame.draw.rect(janela, BRANCO, caixa_rect)
        janela.blit(texto_turno, texto_turno_rect)

        # Desenhar as cartas
        for idx, imagem in enumerate(imagens_cartas):
            rect = pygame.Rect(pos_x + idx * (LARGURA_CARTA + MARGEM), pos_y, LARGURA_CARTA, ALTURA_CARTA)
            janela.blit(pygame.transform.scale(imagem, (LARGURA_CARTA, ALTURA_CARTA)), rect)

            # Desenhar borda amarela se a carta estiver selecionada
            if selecao == idx:
                pygame.draw.rect(janela, VERMELHO, rect, 5)

        # Desenhar o botão de selecionar atributo
        if(turno == "Your turn" and atributo_selecionado == False):
            botao_selecionar = pygame.Rect((largura_tela - 260) // 2, pos_y_botoes, 260, ALTURA_BOTAO)
            pygame.draw.rect(janela, VERDE, botao_selecionar)
            fonte_botao = pygame.font.Font(None, 36)
            texto_botao = fonte_botao.render('Selecionar atributo', True, BRANCO)
            texto_botao_rect = texto_botao.get_rect(center=botao_selecionar.center)
            janela.blit(texto_botao, texto_botao_rect)
        
        # Desenhar o botão de confirmação
        if(atributo_selecionado == True):
            fonte_atributo_externo = pygame.font.Font(None, 51)
            texto_atributo_interno = fonte_titulo.render(f'Atributo: {atributo}', True, VERMELHO)
            texto_atributo_interno_rect = texto_atributo_interno.get_rect(center=(largura_tela // 2, 200))
            janela.blit(texto_atributo_interno, texto_atributo_interno_rect)
            
            botao_confirmar = pygame.Rect((largura_tela - LARGURA_BOTAO - 20), pos_y_botoes, LARGURA_BOTAO, ALTURA_BOTAO)
            pygame.draw.rect(janela, VERDE, botao_confirmar)
            fonte_botao = pygame.font.Font(None, 36)
            texto_botao = fonte_botao.render('Confirmar', True, BRANCO)
            texto_botao_rect = texto_botao.get_rect(center=botao_confirmar.center)
            janela.blit(texto_botao, texto_botao_rect)
        else:
            if turno == "Oppnent turn":
                texto_carregando = fonte.render('Espere sua vez...', True, BRANCO)
                texto_rect = texto_carregando.get_rect(center=(largura_tela // 2, altura_tela // 2))
                janela.blit(texto_carregando, texto_rect)

        pygame.display.flip()

        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Fechar(message_queue)

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                # Verificar se o botão de confirmação foi clicado
                if atributo_selecionado == True:
                    if botao_confirmar.collidepoint(pos) and selecao is not None:
                        message_queue.put(f"select_card {mao[selecao][1]}")
                        
                        while True:
                            if not response_queue.empty():
                                resposta, vencedor = response_queue.get()
                                if resposta == "Turn ended":
                                    fim_turno = True
                                    break
                        break

                # Verificar se o botão de selecionar atributo foi clicado
                if(turno == "Your turn"):
                    if botao_selecionar.collidepoint(pos):
                        atributo_selecionado = TelaSelecaoAtributo(janela, imagemPantano, message_queue, response_queue)

                # Verificar se uma das cartas foi clicada
                for idx in range(len(paths)):
                    rect = pygame.Rect(pos_x + idx * (LARGURA_CARTA + MARGEM), pos_y, LARGURA_CARTA, ALTURA_CARTA)
                    if rect.collidepoint(pos):
                        selecao = idx
        
        if fim_turno:
            turnos = turnos + 1 
            
            # Verifica se o jogo acabou e mostra a tela de vencedor do jogo ou do turno
            turno = response_queue.get()
            if turno == "Match ended":
                TelaVencedor(janela, vencedor, turnos, True, imagemPantano, message_queue, response_queue)
                return
            
            TelaVencedor(janela, vencedor, turnos, False, imagemPantano, message_queue, response_queue)

            # Reseta os valores do turno
            selecao = None
            
            baralho, mao = response_queue.get()
            
            # Recupera a imagem das cartas
            paths = []
            for i in range(3):
                paths.append(mao[i][9])
            imagens_cartas = [pygame.image.load(path[1:]).convert_alpha() for path in paths]

            atributo_selecionado = False
            fim_turno = False

def TelaVencedor(janela, vencedor, turno, jogo_completo, imagemPantano, message_queue, response_queue):
    BRANCO = (255, 255, 255)
    AMARELO = (255, 255, 0)
    fonte = pygame.font.Font(None, 100)

    # Carregar imagem de fundo
    try:
        fundo = pygame.image.load(imagemPantano).convert()
        fundo = pygame.transform.scale(fundo, (janela.get_width(), janela.get_height()))
    except pygame.error as e:
        print(f"Erro ao carregar a imagem de fundo: {e}")
        Fechar(message_queue)

    recompensa = None
    if jogo_completo:
        mensagem = f'{vencedor} venceu o jogo!'
    else:
        mensagem = f'{vencedor} venceu o turno {turno}!'

    texto_mensagem = fonte.render(mensagem, True, AMARELO)
    texto_rect = texto_mensagem.get_rect(center=(janela.get_width() // 2, janela.get_height() // 2))

    piscar_repeticoes = 3
    intervalo_piscar = 500  # Milissegundos entre piscadas
    intervalo_pausa = 500  # Milissegundos de pausa após as piscadas

    clock = pygame.time.Clock()
    tempo_inicio = pygame.time.get_ticks()
    piscando = True
    piscado_repeticoes = 0
    recompensa = None

    while True:
        if not response_queue.empty() and jogo_completo:
            recompensa = response_queue.get()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Fechar(message_queue)

        janela.blit(fundo, (0, 0))  # Desenha a imagem de fundo

        tempo_atual = pygame.time.get_ticks()
        if piscando:
            if (tempo_atual - tempo_inicio) % (2 * intervalo_piscar) < intervalo_piscar:
                janela.blit(texto_mensagem, texto_rect)
            if (tempo_atual - tempo_inicio) >= (piscar_repeticoes * intervalo_piscar + intervalo_pausa):
                piscado_repeticoes += 1
                if piscado_repeticoes >= piscar_repeticoes:
                    pygame.display.flip()
                    pygame.time.wait(intervalo_pausa)  # Pausa após as piscadas
                    if not recompensa == None:
                        texto_recompensa = fonte.render(f"Você ganhou a carta: {recompensa}", True, AMARELO)
                        janela.blit(texto_recompensa, texto_rect)
                    return  # Retorna após concluir a exibição

        pygame.display.flip()
        clock.tick(30)

def TelaSelecaoAtributo(janela, imagemPantano, message_queue, response_queue):
    # Definições de constantes
    LARGURA_BOTAO = 300
    ALTURA_BOTAO = 50
    MARGEM = 20
    BRANCO = (255, 255, 255)
    CINZA = (192, 192, 192)
    AMARELO = (255, 255, 0)
    VERMELHO = (255, 0, 0)
    PRETO = (0, 0, 0)
    VERDE = (0, 255, 0)
    atributos = ['Forca', 'Fofura', 'Velocidade', 'Tamanho', 'Idade', 'Tipo']
    pos_y = 200  # Ajusta a posição vertical dos botões
    selecao = None

    fonte_titulo = pygame.font.Font(None, 50)
    texto_titulo = fonte_titulo.render('Selecione um Atributo', True, PRETO)
    texto_titulo_rect = texto_titulo.get_rect(center=(janela.get_width() // 2, 50))

    # Adicionar uma caixa branca ao redor do título
    caixa_branca_rect = texto_titulo_rect.inflate(20, 20)  # Aumenta o retângulo para criar margem
    caixa_branca_rect.center = texto_titulo_rect.center  # Centraliza a caixa em relação ao título

    # Carregar imagem de fundo
    try:
        fundo = pygame.image.load(imagemPantano).convert()
        fundo = pygame.transform.scale(fundo, (janela.get_width(), janela.get_height()))
    except pygame.error as e:
        print(f"Erro ao carregar a imagem de fundo: {e}")
        Fechar(message_queue)

    while True:
        janela.blit(fundo, (0, 0))  # Desenha o fundo

        # Desenhar a caixa branca ao redor do título
        pygame.draw.rect(janela, BRANCO, caixa_branca_rect)

        # Desenhar o título
        janela.blit(texto_titulo, texto_titulo_rect)

        # Desenhar botões para atributos
        for idx, atributo in enumerate(atributos):
            botao_rect = pygame.Rect((janela.get_width() - LARGURA_BOTAO) // 2, pos_y + idx * (ALTURA_BOTAO + MARGEM),
                                     LARGURA_BOTAO, ALTURA_BOTAO)
            pygame.draw.rect(janela, AMARELO, botao_rect)
            fonte_botao = pygame.font.Font(None, 36)
            texto_botao = fonte_botao.render(atributo, True, PRETO)
            texto_botao_rect = texto_botao.get_rect(center=botao_rect.center)
            janela.blit(texto_botao, texto_botao_rect)

            # Desenhar borda cinza se o atributo estiver selecionado
            if selecao == idx:
                pygame.draw.rect(janela, VERMELHO, botao_rect, 5)

        # Desenhar o botão "Confirmar" se um atributo for selecionado
        if selecao is not None:
            botao_confirmar = pygame.Rect((janela.get_width() - LARGURA_BOTAO) // 2,
                                          pos_y + len(atributos) * (ALTURA_BOTAO + MARGEM),
                                          LARGURA_BOTAO, ALTURA_BOTAO)
            pygame.draw.rect(janela, VERDE, botao_confirmar)
            texto_confirmar = fonte_botao.render('Confirmar', True, BRANCO)
            texto_confirmar_rect = texto_confirmar.get_rect(center=botao_confirmar.center)
            janela.blit(texto_confirmar, texto_confirmar_rect)

        pygame.display.flip()

        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Fechar(message_queue)

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                # Verificar se um dos botões de atributo foi clicado
                for idx in range(len(atributos)):
                    botao_rect = pygame.Rect((janela.get_width() - LARGURA_BOTAO) // 2,
                                             pos_y + idx * (ALTURA_BOTAO + MARGEM), LARGURA_BOTAO, ALTURA_BOTAO)
                    if botao_rect.collidepoint(pos):
                        selecao = idx

                # Verificar se o botão "Confirmar" foi clicado
                if selecao is not None:
                    botao_confirmar = pygame.Rect((janela.get_width() - LARGURA_BOTAO) // 2,
                                                  pos_y + len(atributos) * (ALTURA_BOTAO + MARGEM),
                                                  LARGURA_BOTAO, ALTURA_BOTAO)
                    if botao_confirmar.collidepoint(pos):
                        message_queue.put(f"select_attribute {atributos[selecao]}")
                        return True

def TelaEscolherBaralho(janela, jogador, message_queue, response_queue):
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
                Fechar(message_queue)
            if evento.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = pygame.mouse.get_pos()
                for i, rect in enumerate(opcoes_baralho):
                    if rect.collidepoint(mouseX, mouseY):
                        return baralhos[i]  # Retorna o baralho escolhido

def TelaMudarBaralho(janela, message_queue, response_queue, imagemFundo):
    pygame.init()
    fonte = pygame.font.SysFont('Arial', 30)
    largura_janela = janela.get_width()
    altura_janela = janela.get_height()

    largura_caixa = 300
    altura_caixa = 50

    # Carregar e redimensionar a imagem de fundo
    try:
        fundo = pygame.image.load(imagemFundo)
        fundo = pygame.transform.scale(fundo, (largura_janela, altura_janela))
    except pygame.error as e:
        print(f"Erro ao carregar a imagem de fundo: {e}")
        Fechar(message_queue)

    caixas_texto = [
        {'rect': pygame.Rect((largura_janela - largura_caixa) // 2, 100, largura_caixa, altura_caixa),
         'texto': 'Ver Decks', 'retorno': 0},
        {'rect': pygame.Rect((largura_janela - largura_caixa) // 2, 200, largura_caixa, altura_caixa),
         'texto': 'Ver Coleção', 'retorno': 1},
        {'rect': pygame.Rect((largura_janela - largura_caixa) // 2, 300, largura_caixa, altura_caixa),
         'texto': 'Criar Deck', 'retorno': 2}
    ]

    # Adicionar botão de voltar
    largura_botao_voltar = 200
    altura_botao_voltar = 50
    botao_voltar = pygame.Rect((largura_janela - largura_botao_voltar) // 2,
                               altura_janela - altura_botao_voltar - 10,
                               largura_botao_voltar, altura_botao_voltar)
    texto_botao_voltar = fonte.render('Voltar ao Menu', True, (0, 0, 0))  # Texto preto

    rodando = True

    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                Fechar(message_queue)
            if evento.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = pygame.mouse.get_pos()
                # Verificar se o botão de voltar foi clicado
                if botao_voltar.collidepoint(mouseX, mouseY):
                    rodando = False
                    return 3  # Retorna 3 quando o botão de voltar é clicado

                for caixa in caixas_texto:
                    if caixa['rect'].collidepoint(mouseX, mouseY):
                        rodando = False
                        return caixa['retorno']  # Retorna o número correspondente à ação selecionada

        # Desenhar a imagem de fundo
        janela.blit(fundo, (0, 0))

        # Desenhar os botões das opções com fundo branco
        for caixa in caixas_texto:
            pygame.draw.rect(janela, (255, 255, 255), caixa['rect'])  # Fundo branco
            pygame.draw.rect(janela, (0, 0, 0), caixa['rect'], 2)  # Borda preta
            texto = fonte.render(caixa['texto'], True, (0, 0, 0))  # Texto preto
            janela.blit(texto, (caixa['rect'].x + 5, caixa['rect'].y + 5))

        # Desenhar o botão de voltar com fundo branco
        pygame.draw.rect(janela, (255, 255, 255), botao_voltar)  # Fundo branco
        pygame.draw.rect(janela, (255, 0, 0), botao_voltar, 2)  # Borda vermelha
        janela.blit(texto_botao_voltar, (botao_voltar.x + 5, botao_voltar.y + 10))

        pygame.display.update()


def TelaCriarDeck(janela, todasCartas, imagemFundo, message_queue, response_queue):
    # Definições de constantes
    LARGURA_CARTA = 100
    ALTURA_CARTA = 140
    MARGEM = 10
    LIMITE_CARTAS = 9  # Máximo de cartas que podem ser selecionadas
    LARGURA_BOTAO = 150
    ALTURA_BOTAO = 50

    # Cores
    BRANCO = (255, 255, 255)
    VERDE = (0, 255, 0)
    AZUL = (0, 0, 255)
    VERMELHO = (255, 0, 0)
    CINZA = (169, 169, 169)
    PRETO = (0, 0, 0)

    largura_tela = janela.get_width()
    altura_tela = janela.get_height()

    # Carregar imagem de fundo
    try:
        fundo = pygame.image.load(imagemFundo).convert()
        fundo = pygame.transform.scale(fundo, (largura_tela, altura_tela))
    except pygame.error as e:
        print(f"Erro ao carregar a imagem de fundo: {e}")
        Fechar(message_queue)
    
    # Recupera o caminho para as imagens das cartas
    paths = []
    for nome in todasCartas[:, 0]:
        message_queue.put(f"check_card {nome}")
        paths.append(response_queue.get()[7])
    
    # Carregar imagens das cartas
    imagens_cartas = [pygame.image.load(path[1:]).convert_alpha() for path in paths]

    # Inicializar variáveis
    quantidade = [0] * todasCartas.shape[0]
    total_selecionadas = 0
    cartas_selecionadas = []

    fonte = pygame.font.Font(None, 36)
    fonte_caixa_texto = pygame.font.Font(None, 48)

    # Variáveis para o nome do deck
    nome_deck = ""
    caixa_texto_ativa = False

    #add botão voltar
    largura_botao_voltar = 200
    altura_botao_voltar = 50
    botao_voltar = pygame.Rect((largura_tela - largura_botao_voltar + 250) // 2,
                               altura_tela - altura_botao_voltar - 20,
                               largura_botao_voltar, altura_botao_voltar)
    texto_botao_voltar = fonte.render('Voltar ao Menu', True, (0, 0, 0))  # Texto preto

    while True:
        janela.blit(fundo, (0, 0))  # Desenhar a imagem de fundo

        # Coordenadas das cartas
        pos_x = MARGEM
        pos_y = MARGEM

        # Desenhar cartas na tela
        for idx, imagem in enumerate(imagens_cartas):
            rect = pygame.Rect(pos_x, pos_y, LARGURA_CARTA, ALTURA_CARTA)

            # Define a cor da borda conforme a quantidade selecionada
            if quantidade[idx] == 1:
                cor_borda = VERDE
            elif quantidade[idx] == 2:
                cor_borda = AZUL
            elif quantidade[idx] == 3:
                cor_borda = VERMELHO
            else:
                cor_borda = BRANCO  # Sem seleção

            janela.blit(pygame.transform.scale(imagem, (LARGURA_CARTA, ALTURA_CARTA)), rect)
            pygame.draw.rect(janela, cor_borda, rect, 5)  # Borda das cartas

            # Atualizar a posição das cartas
            pos_x += LARGURA_CARTA + MARGEM
            if (idx + 1) % 5 == 0:
                pos_x = MARGEM
                pos_y += ALTURA_CARTA + MARGEM

        # Desenhar o texto "NOME DO DECK:"
        texto_nome_label = fonte.render('NOME DO DECK:', True, BRANCO)
        janela.blit(texto_nome_label, (MARGEM, altura_tela - ALTURA_BOTAO - 4 * MARGEM))

        # Desenhar caixa de texto para o nome do deck
        caixa_texto_rect = pygame.Rect(MARGEM, altura_tela - ALTURA_BOTAO - 2 * MARGEM, largura_tela // 2, ALTURA_BOTAO)
        pygame.draw.rect(janela, BRANCO, caixa_texto_rect, 2)

        texto_nome_deck = fonte_caixa_texto.render(nome_deck, True, BRANCO)
        janela.blit(texto_nome_deck, (caixa_texto_rect.x + 5, caixa_texto_rect.y + 5))

        # Desenhar o botão "Confirmar" se o limite de cartas for atingido e o nome do deck não estiver vazio
        if total_selecionadas == LIMITE_CARTAS and len(nome_deck) > 0:
            botao_confirmar = pygame.Rect(largura_tela - LARGURA_BOTAO - MARGEM, altura_tela - ALTURA_BOTAO - MARGEM,
                                       LARGURA_BOTAO, ALTURA_BOTAO)
            pygame.draw.rect(janela, VERDE, botao_confirmar)
            texto_confirmar = fonte.render('Confirmar', True, BRANCO)
            janela.blit(texto_confirmar, (botao_confirmar.x + (LARGURA_BOTAO - texto_confirmar.get_width()) // 2,
                                          botao_confirmar.y + (ALTURA_BOTAO - texto_confirmar.get_height()) // 2))

        pygame.draw.rect(janela, (255, 255, 255), botao_voltar)  # Fundo branco
        pygame.draw.rect(janela, (255, 0, 0), botao_voltar, 2)  # Borda vermelha
        janela.blit(texto_botao_voltar, (botao_voltar.x + 5, botao_voltar.y + 10))

        pygame.display.flip()

        
        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Fechar(message_queue)

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                mouseX = pos[0]
                mouseY = pos[1]

                if caixa_texto_rect.collidepoint(pos):
                    caixa_texto_ativa = True
                else:
                    caixa_texto_ativa = False
                    
                if botao_voltar.collidepoint(mouseX, mouseY):
                    return 

                if total_selecionadas == LIMITE_CARTAS and len(nome_deck) > 0:
                    # Verificar se o botão "Confirmar" foi clicado
                    if botao_confirmar.collidepoint(pos):
                        message_queue.put(f"create_deck {nome_deck}")
                        resposta, nome_deck = response_queue.get()
                        if resposta == "Deck created":
                            for i in range(9):
                                message_queue.put(f"add_card_to_deck {nome_deck} {cartas_selecionadas[i]}")
                                if response_queue.get() == "Card added":
                                    continue
                                else:
                                    # erro, mostrar um popup ou algo assim
                                    break
                        else:
                            True
                            # erro, mostrar um popup ou algo assim
                        return

                else:
                    # Selecionar ou desmarcar cartas
                    for idx, imagem in enumerate(imagens_cartas):
                        rect = pygame.Rect(MARGEM + (idx % 5) * (LARGURA_CARTA + MARGEM),
                                           MARGEM + (idx // 5) * (ALTURA_CARTA + MARGEM),
                                           LARGURA_CARTA, ALTURA_CARTA)
                        if rect.collidepoint(pos):
                            carta = todasCartas[idx][0]
                            if event.button == 1:  # Clique esquerdo
                                if quantidade[idx] < 3 and total_selecionadas < LIMITE_CARTAS:
                                    quantidade[idx] += 1
                                    total_selecionadas += 1
                                    cartas_selecionadas.append(carta)
                            elif event.button == 3:  # Clique direito
                                if quantidade[idx] > 0:
                                    quantidade[idx] -= 1
                                    total_selecionadas -= 1
                                    cartas_selecionadas.remove(carta)

            if event.type == pygame.KEYDOWN:
                if caixa_texto_ativa:
                    if event.key == pygame.K_RETURN:
                        if total_selecionadas == LIMITE_CARTAS and len(nome_deck) > 0:
                            return cartas_selecionadas, nome_deck
                    elif event.key == pygame.K_BACKSPACE:
                        nome_deck = nome_deck[:-1]
                    else:
                        nome_deck += event.unicode
            


def TelaMostrarColecao(janela, todasCartas, imagemFundo, message_queue, response_queue):
    pygame.init()
    fonte = pygame.font.SysFont('Arial', 30)
    largura_janela = janela.get_width()
    altura_janela = janela.get_height()

    largura_carta = 100
    altura_carta = 150
    margem = 20
    colunas = 10
    linhas = (todasCartas.shape[0] + colunas - 1) // colunas  # Calcula o número de linhas necessárias
    largura_botao = 250
    altura_botao = 50

    # Carregar e redimensionar a imagem de fundo
    fundo = pygame.image.load(imagemFundo)
    fundo = pygame.transform.scale(fundo, (largura_janela, altura_janela))

    # Botão de voltar
    botao_voltar = pygame.Rect(10, altura_janela - altura_botao - 10, largura_botao, altura_botao)
    texto_voltar = fonte.render('Voltar', True, (255, 255, 255))

    # Calcular a posição inicial das cartas para começar do topo
    x_inicial = (largura_janela - (largura_carta * colunas + margem * (colunas - 1))) // 2
    y_inicial = 20  # Ajusta a posição y para começar do topo

    # Recupera o caminho para as imagens das cartas
    paths = []
    for nome in todasCartas[:,0]:
        message_queue.put(f"check_card {nome}")
        paths.append(response_queue.get()[7])

    rodando_cartas = True
    while rodando_cartas:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                Fechar(message_queue)
            if evento.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = pygame.mouse.get_pos()
                if botao_voltar.collidepoint(mouseX, mouseY):
                    rodando_cartas = False
                    return  # Retorna para a tela anterior

        # Desenhar a imagem de fundo
        janela.blit(fundo, (0, 0))

        # Desenhar as cartas
        for i, path_imagem in enumerate(paths):
            imagem = pygame.image.load(path_imagem[1:])
            imagem_redimensionada = pygame.transform.scale(imagem, (largura_carta, altura_carta))
            x = x_inicial + (i % colunas) * (largura_carta + margem)
            y = y_inicial + (i // colunas) * (altura_carta + margem)
            if y < altura_janela:  # Verifica se a carta está dentro da altura da janela
                janela.blit(imagem_redimensionada, (x, y))

        # Desenhar o botão de voltar
        pygame.draw.rect(janela, (255, 0, 0), botao_voltar)  # Botão vermelho
        janela.blit(texto_voltar, (botao_voltar.x + 5, botao_voltar.y + 10))

        pygame.display.update()

def TelaMostrarDecks(janela, baralhos, imagemFundo, message_queue, response_queue):
    pygame.init()
    fonte = pygame.font.SysFont('Arial', 30)
    largura_janela = janela.get_width()
    altura_janela = janela.get_height()

    largura_caixa = 300
    altura_caixa = 50

    nomeBaralhos = baralhos[:,1]

    caixas_texto = [
        {'rect': pygame.Rect(10, 100 + i * 60, largura_caixa, altura_caixa),
         'texto': nomeBaralhos[i], 'index': i}
        for i in range(len(nomeBaralhos))
    ]

    largura_botao_voltar = 200
    altura_botao_voltar = 50
    botao_voltar = pygame.Rect(10, altura_janela - altura_botao_voltar - 10, largura_botao_voltar, altura_botao_voltar)
    texto_voltar = fonte.render('Voltar', True, (0, 0, 0))

    # Carregar e redimensionar a imagem de fundo
    fundo = pygame.image.load(imagemFundo)
    fundo = pygame.transform.scale(fundo, (largura_janela, altura_janela))

    rodando = True

    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                Fechar(message_queue)
            if evento.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = pygame.mouse.get_pos()
                if botao_voltar.collidepoint(mouseX, mouseY):
                    rodando = False
                    return 0

                for caixa in caixas_texto:
                    if caixa['rect'].collidepoint(mouseX, mouseY):
                        index = caixa['index']
                        if(TelaMostrarCartasBaralho(janela, baralhos[index], index, imagemFundo, message_queue, response_queue) == 0):
                            return 1

        # Desenhar a imagem de fundo
        janela.blit(fundo, (0, 0))

        for caixa in caixas_texto:
            pygame.draw.rect(janela, (255, 255, 255), caixa['rect'])  # Fundo branco
            pygame.draw.rect(janela, (0, 0, 0), caixa['rect'], 2)  # Borda preta
            texto = fonte.render(caixa['texto'], True, (0, 0, 0))  # Texto preto
            janela.blit(texto, (caixa['rect'].x + 5, caixa['rect'].y + 5))

        pygame.draw.rect(janela, (200, 200, 200), botao_voltar)  # Botão cinza
        janela.blit(texto_voltar, (botao_voltar.x + 5, botao_voltar.y + 10))

        pygame.display.update()

def TelaMostrarCartasBaralho(janela, baralho, index_baralho, imagemFundo, message_queue, response_queue):
    pygame.init()
    fonte = pygame.font.SysFont('Arial', 30)
    largura_janela = janela.get_width()
    altura_janela = janela.get_height()

    largura_carta = 150  # Aumente a largura das cartas
    altura_carta = 200  # Aumente a altura das cartas
    margem = 20  # Ajuste a margem para maior espaçamento
    colunas = 3
    linhas = 3

    largura_total = largura_carta * colunas + margem * (colunas - 1)
    altura_total = altura_carta * linhas + margem * (linhas - 1)
    x_inicial = (largura_janela - largura_total) // 2
    y_inicial = (altura_janela - altura_total) // 2

    largura_botao = 250
    altura_botao = 50
    botao_ativo = pygame.Rect(10, altura_janela - 120, largura_botao, altura_botao)
    botao_voltar = pygame.Rect(10, altura_janela - 60, largura_botao, altura_botao)

    if index_baralho != 0:
        botao_deletar = pygame.Rect(10, altura_janela - 180, largura_botao, altura_botao)
        texto_deletar = fonte.render('Deletar Deck', True, (255, 255, 255))
    else:
        botao_deletar = None
        texto_deletar = None

    texto_ativo = fonte.render('Escolher Deck Ativo', True, (255, 255, 255))
    texto_voltar = fonte.render('Voltar', True, (255, 255, 255))

    # Carregar e redimensionar a imagem de fundo
    fundo = pygame.image.load(imagemFundo)
    fundo = pygame.transform.scale(fundo, (largura_janela, altura_janela))

    # Recupera as cartas do baralho
    message_queue.put(f"check_deck {baralho[1]}")
    nomes = response_queue.get()[2]
    
    # Recupera o caminho para as imagens das cartas
    paths = []
    for nome in nomes:
        message_queue.put(f"check_card {nome}")
        paths.append(response_queue.get()[7])
    
    rodando_cartas = True
    while rodando_cartas:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                Fechar(message_queue)
            if evento.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = pygame.mouse.get_pos()
                if botao_voltar.collidepoint(mouseX, mouseY):
                    rodando_cartas = False
                    return
                if botao_deletar and botao_deletar.collidepoint(mouseX, mouseY):
                    rodando_cartas = False
                    message_queue.put(f"delete_deck {baralho[1]}")
                    if(response_queue.get()[0] == "Deck deleted"):
                        return 0
                    else:
                        True
                        # erro, mostrar um pop up ou algm coisa assim
                if botao_ativo.collidepoint(mouseX, mouseY):
                    rodando_cartas = False
                    message_queue.put(f"activate_deck {baralho[1]}")
                    resposta = response_queue.get()
                    if(resposta[0] == "Activated deck"):
                        return 0
                    else:
                        print(resposta)
                        # erro, mostrar um pop up ou algm coisa assim

        # Desenhar a imagem de fundo
        janela.blit(fundo, (0, 0))

        for i, path_imagem in enumerate(paths):
            imagem = pygame.image.load(path_imagem[1:])
            imagem_redimensionada = pygame.transform.scale(imagem, (largura_carta, altura_carta))
            x = x_inicial + (i % colunas) * (largura_carta + margem)
            y = y_inicial + (i // colunas) * (altura_carta + margem)
            janela.blit(imagem_redimensionada, (x, y))

        if botao_deletar:
            pygame.draw.rect(janela, (255, 0, 0), botao_deletar)  # Botão vermelho
            janela.blit(texto_deletar, (botao_deletar.x + 5, botao_deletar.y + 10))

        pygame.draw.rect(janela, (0, 0, 255), botao_ativo)  # Botão azul
        pygame.draw.rect(janela, (200, 200, 200), botao_voltar)  # Botão cinza

        janela.blit(texto_ativo, (botao_ativo.x + 5, botao_ativo.y + 10))
        janela.blit(texto_voltar, (botao_voltar.x + 5, botao_voltar.y + 10))

        pygame.display.update()

def iniciaJanela(largura_janela, altura_janela):
    janela = pygame.display.set_mode((largura_janela, altura_janela))
    pygame.display.set_caption('Jogo de Cartas')
    return janela







