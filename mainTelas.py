from telas import iniciaJanela, TelaLogin, TelaMenuPrincipal, TelaMudarBaralho
from telas import TelaCarregamento, TelaPartida, TelaSelecaoAtributo, TelaVencedor
from telas import TelaMostrarDecks, TelaMostrarColecao, TelaCriarDeck
import pygame

baralho1 = ['server/StreamingAssets/aranha.png', 'server/StreamingAssets/bem_te_vi.png','server/StreamingAssets/borboleta.png', 'server/StreamingAssets/aranha.png', 'server/StreamingAssets/bem_te_vi.png','server/StreamingAssets/borboleta.png', 'server/StreamingAssets/aranha.png', 'server/StreamingAssets/bem_te_vi.png','server/StreamingAssets/borboleta.png']
baralho2 = ['server/StreamingAssets/calopsita.png', 'server/StreamingAssets/cobra_de_vidro.png','server/StreamingAssets/coruja.png']
baralho3 = ['server/StreamingAssets/coruja.png', 'server/StreamingAssets/grilo.png','server/StreamingAssets/lagartixa.png']
baralhos = [baralho1, baralho2, baralho3]
todasCartas = ['server/StreamingAssets/aranha.png', 'server/StreamingAssets/bem_te_vi.png','server/StreamingAssets/borboleta.png', 'server/StreamingAssets/aranha.png', 'server/StreamingAssets/bem_te_vi.png','server/StreamingAssets/borboleta.png', 'server/StreamingAssets/aranha.png', 'server/StreamingAssets/bem_te_vi.png','server/StreamingAssets/borboleta.png', 'server/StreamingAssets/coruja.png', 'server/StreamingAssets/grilo.png','server/StreamingAssets/lagartixa.png']
nomeBaralhos = ['AAA', 'BBB', 'CCC']
NomeJogadore ='Marcus'

imagemPantano = 'server/StreamingAssets/pantano.jpg'
imagemCerrado = 'server/StreamingAssets/cerrado.jpg'
pathImagemLogin = 'server/StreamingAssets/imagemLogin.jpg'
pathImagemTelaPrincipal = 'server/StreamingAssets/imagemTelaPrincipal.jpg'
def startInterface(message_queue, response_queue):
    janela = iniciaJanela(1200, 800)
    resposta = 1
    while True:
        #retorna 0 se login e 1 se registrar
        #nome, senha, reposta = TelaLogin(janela, message_queue, response_queue, pathImagemLogin)
        #message_queue.put(f"login {nome} {senha}")
        #resposta = response_queue.get()
        if(resposta == 1):

            #retorna 0 se for para sair, 1 se for para ir para opções de baralho e 2 se for para jogar
            saidaTelaMenuPrincipal = TelaMenuPrincipal(janela, message_queue, response_queue, pathImagemTelaPrincipal)
            if(saidaTelaMenuPrincipal == 0):
                break
            #ramo de mudar o baralho
            if(saidaTelaMenuPrincipal == 1):
                #0 = ver decks TelaMostrarDecks (aqui que deleta deck e marca que está usando)
                #1 = ver coleção TelaMostrarCartasBaralho
                #2 = criar deck TelaCriarDeck
                #3 = voltar ao menu
                TelaMudarBaralho(janela, message_queue, response_queue, imagemCerrado)

                #precisa como entrada a coleção de baralhos, onde cada baralho é composto pelo caminho das imagens das cartas
                #nome dos baralho é literalmente o nome de todos os baralhos
                #vai mostrar todos os decks do usuario, depois de ele escolher 1
                #chama a função TelaMostrarCartasBaralho
                # que vai retornar 0 e o baralho caso o usuario escolha deletar
                # Retornar 1 e o baralho quando "Escolher Deck Ativo" for clicado.
                # retorna 2 se o usuario clicar em voltar e none
                TelaMostrarDecks(janela, baralhos, nomeBaralhos,imagemCerrado )

                #só mostra todas as cartas e tem um botão que volta
                TelaMostrarColecao(janela, todasCartas, imagemCerrado)

                TelaCriarDeck(janela, todasCartas, imagemCerrado)
            else:
                #TelaCarregamento(janela, pathImagemTelaPrincipal)

                #retorna a carta escolhida, e o baralho3 é o caminho das 3 cartas do usuário
                TelaPartida(janela, baralho3, 0, imagemPantano)

                #retorna o atributo escolhido
                TelaSelecaoAtributo(janela, imagemPantano)

                # se jogo_completo for True aparece que o jogador ganhou o jogo
                # se for false aparece que ele ganhou o turno
                TelaVencedor(janela, "Marcus", 1, True, imagemPantano)
        else:
            continue


if __name__ == "__main__":
    startInterface()