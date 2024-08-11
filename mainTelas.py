from telas import iniciaJanela, TelaLogin, TelaMenuPrincipal, TelaMudarBaralho
from telas import TelaCarregamento, TelaPartida, TelaSelecaoAtributo, TelaVencedor
from telas import TelaMostrarDecks, TelaMostrarColecao, TelaCriarDeck
import numpy as np
import pygame

# baralho1 = ['StreamingAssets/aranha.png', 'StreamingAssets/bem_te_vi.png','StreamingAssets/borboleta.png', 'StreamingAssets/aranha.png', 'StreamingAssets/bem_te_vi.png','StreamingAssets/borboleta.png', 'StreamingAssets/aranha.png', 'StreamingAssets/bem_te_vi.png','StreamingAssets/borboleta.png']
# baralho2 = ['StreamingAssets/calopsita.png', 'StreamingAssets/cobra_de_vidro.png','StreamingAssets/coruja.png']
# baralho3 = ['StreamingAssets/coruja.png', 'StreamingAssets/grilo.png','StreamingAssets/lagartixa.png']
# baralhos = [baralho1, baralho2, baralho3]
# todasCartas = ['StreamingAssets/aranha.png', 'StreamingAssets/bem_te_vi.png','StreamingAssets/borboleta.png', 'StreamingAssets/aranha.png', 'StreamingAssets/bem_te_vi.png','StreamingAssets/borboleta.png', 'StreamingAssets/aranha.png', 'StreamingAssets/bem_te_vi.png','StreamingAssets/borboleta.png', 'StreamingAssets/coruja.png', 'StreamingAssets/grilo.png','StreamingAssets/lagartixa.png']
# nomeBaralhos = ['AAA', 'BBB', 'CCC']
# NomeJogadore ='Marcus'

imagemPantano = 'StreamingAssets/pantano.jpg'
imagemCerrado = 'StreamingAssets/cerrado.jpg'
pathImagemLogin = 'StreamingAssets/imagemLogin.jpg'
pathImagemTelaPrincipal = 'StreamingAssets/imagemTelaPrincipal.jpg'

def startInterface(message_queue, response_queue):
    janela = iniciaJanela(1200, 800)
    resposta = 1
    while True:
        # retorna 0 se login e 1 se registrar
        nome, senha = TelaLogin(janela, message_queue, response_queue, pathImagemLogin)
        message_queue.put(f"login {nome} {senha}")
        resposta = response_queue.get()
        if(resposta == "logging in"):
            while True:
                #retorna 0 se for para sair, 1 se for para ir para opções de baralho e 2 se for para jogar
                saidaTelaMenuPrincipal = TelaMenuPrincipal(janela, message_queue, response_queue, pathImagemTelaPrincipal)

                if(saidaTelaMenuPrincipal == 0):
                    message_queue.put("exit")
                    return
                #ramo de mudar o baralho
                if(saidaTelaMenuPrincipal == 1):
                    while True:

                        #0 = ver decks TelaMostrarDecks (aqui que deleta deck e marca que está usando)
                        #1 = ver coleção TelaMostrarCartasBaralho
                        #2 = criar deck TelaCriarDeck
                        #3 = voltar ao menu
                        
                        saidaTelaMudarBaralho = TelaMudarBaralho(janela, message_queue, response_queue, imagemCerrado)
                        
                        if(saidaTelaMudarBaralho == 0):
                            # Recupera as informações dos decks
                            message_queue.put("check_decks")
                            baralhos = np.array(response_queue.get())

                            while True:

                                #precisa como entrada a coleção de baralhos, onde cada baralho é composto pelo caminho das imagens das cartas
                                #nome dos baralho é literalmente o nome de todos os baralhos
                                #vai mostrar todos os decks do usuario, depois de ele escolher 1
                                #chama a função TelaMostrarCartasBaralho
                                # que vai retornar 0 e o baralho caso o usuario escolha deletar
                                # Retornar 1 e o baralho quando "Escolher Deck Ativo" for clicado.
                                # retorna 2 se o usuario clicar em voltar e none

                                saidaTelaMostraDecks = TelaMostrarDecks(janela, baralhos, imagemCerrado, message_queue, response_queue)

                                if(saidaTelaMostraDecks == 0):
                                    break
                                elif(saidaTelaMostraDecks == 1):
                                    # Atualiza as informações dos decks
                                    message_queue.put("check_decks")
                                    baralhos = np.array(response_queue.get())
                                continue
                            
                            continue

                        elif(saidaTelaMudarBaralho == 1):
                            # Recupera as informações das cartas
                            message_queue.put("check_cards")
                            todasCartas = np.array(response_queue.get())

                            TelaMostrarColecao(janela, todasCartas, imagemCerrado, message_queue, response_queue)

                        elif(saidaTelaMudarBaralho == 2):
                            # Recupera as informações das cartas
                            message_queue.put("check_cards")
                            todasCartas = np.array(response_queue.get())
                            
                            TelaCriarDeck(janela, todasCartas, imagemCerrado, message_queue, response_queue)
                            
                            # Atualiza as informações dos decks
                            message_queue.put("check_decks")
                            baralhos = np.array(response_queue.get())

                        else:
                            break
                else:
                    respostaTelaCarregamento = TelaCarregamento(janela, pathImagemTelaPrincipal, message_queue, response_queue)
                    
                    if(respostaTelaCarregamento == 0):
                        #retorna a carta escolhida, e o baralho3 é o caminho das 3 cartas do usuário
                        TelaPartida(janela, baralho3, 0, imagemPantano, message_queue, response_queue)

                    #retorna o atributo escolhido
                    # TelaSelecaoAtributo(janela, imagemPantano, message_queue, response_queue)

                    # se jogo_completo for True aparece que o jogador ganhou o jogo
                    # se for false aparece que ele ganhou o turno
                    # TelaVencedor(janela, "Marcus", 1, True, imagemPantano, message_queue, response_queue)


if __name__ == "__main__":
    startInterface()