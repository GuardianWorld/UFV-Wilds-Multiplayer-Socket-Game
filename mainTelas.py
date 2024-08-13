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
                        saidaTelaMudarBaralho = TelaMudarBaralho(janela, message_queue, response_queue, imagemCerrado)
                        
                        if(saidaTelaMudarBaralho == 0):
                            # Recupera as informações dos decks
                            message_queue.put("check_decks")
                            baralhos = np.array(response_queue.get())

                            while True:
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
                    
                    while(True):
                        if(respostaTelaCarregamento == 0):
                            break
                        TelaPartida(janela, 0, imagemPantano, message_queue, response_queue)
                        break


if __name__ == "__main__":
    startInterface()