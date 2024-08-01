from telas import iniciaJanela, TelaLogin, TelaMenuPrincipal
import queue

jogador1 = {
    "nome": "Jogador1",
    "baralhos": [
        {
            "nome": "Baralho1",
            "cartas": [{
                "Forca": 1,
                "Fofura": 2,
                "Velocidade": 5,
                "Tamanho": "enorme",
                "Idade": "anciao",
                "Tipo": "terrestre",
                "Imagem": "1_2_5_enorme_anciao_terrestre"
            },{
                "Forca": 1,
                "Fofura": 2,
                "Velocidade": 5,
                "Tamanho": "enorme",
                "Idade": "anciao",
                "Tipo": "terrestre",
                "Imagem": "1_2_5_enorme_anciao_terrestre"
            },
                {
                "Forca": 1,
                "Fofura": 2,
                "Velocidade": 5,
                "Tamanho": "enorme",
                "Idade": "anciao",
                "Tipo": "terrestre",
                "Imagem": "1_2_5_enorme_anciao_terrestre"
            }, {
                "Forca": 1,
                "Fofura": 5,
                "Velocidade": 9,
                "Tamanho": "medio",
                "Idade": "adulto",
                "Tipo": "voador",
                "Imagem": "1_5_9_medio_adulto_voador"
            },
                {
                    "Forca": 2,
                    "Fofura": 5,
                    "Velocidade": 6,
                    "Tamanho": "minusculo",
                    "Idade": "anciao",
                    "Tipo": "voador",
                    "Imagem": "2_5_6_minusculo_anciao_voador"
                },{
                "Forca": 1,
                "Fofura": 2,
                "Velocidade": 5,
                "Tamanho": "enorme",
                "Idade": "anciao",
                "Tipo": "terrestre",
                "Imagem": "1_2_5_enorme_anciao_terrestre"
            },
                {
                "Forca": 1,
                "Fofura": 2,
                "Velocidade": 5,
                "Tamanho": "enorme",
                "Idade": "anciao",
                "Tipo": "terrestre",
                "Imagem": "1_2_5_enorme_anciao_terrestre"
            }, {
                "Forca": 1,
                "Fofura": 5,
                "Velocidade": 9,
                "Tamanho": "medio",
                "Idade": "adulto",
                "Tipo": "voador",
                "Imagem": "1_5_9_medio_adulto_voador"
            },
                {
                    "Forca": 2,
                    "Fofura": 5,
                    "Velocidade": 6,
                    "Tamanho": "minusculo",
                    "Idade": "anciao",
                    "Tipo": "voador",
                    "Imagem": "2_5_6_minusculo_anciao_voador"
                }]
        },
        {
            "nome": "Baralho2",
            "cartas": [{
                "Forca": 3,
                "Fofura": 7,
                "Velocidade": 8,
                "Tamanho": "grande",
                "Idade": "adolescente",
                "Tipo": "terrestre",
                "Imagem": "3_7_8_grande_adolescente_aquatico"
            },{
                "Forca": 1,
                "Fofura": 2,
                "Velocidade": 5,
                "Tamanho": "enorme",
                "Idade": "anciao",
                "Tipo": "terrestre",
                "Imagem": "1_2_5_enorme_anciao_terrestre"
            }, {
                "Forca": 1,
                "Fofura": 5,
                "Velocidade": 9,
                "Tamanho": "medio",
                "Idade": "adulto",
                "Tipo": "voador",
                "Imagem": "1_5_9_medio_adulto_voador"
            },
                {
                    "Forca": 8,
                    "Fofura": 7,
                    "Velocidade": 1,
                    "Tamanho": "medio",
                    "Idade": "jovem",
                    "Tipo": "aquatico",
                    "Imagem": "8_7_1_medio_jovem_aquatico"
                }]
        }
    ],
    "todasCartas": ['1_2_5_enorme_anciao_terrestre', '1_5_9_medio_adulto_voador', '2_3_10_pequeno_jovem_terrestre',
                    '2_5_6_minusculo_anciao_voador']

}

jogador2 = {
    "nome": "Jogador2",
    "baralhos": [
        {
            "nome": "Baralho1",
            "cartas": [{
                "Forca": 8,
                "Fofura": 7,
                "Velocidade": 1,
                "Tamanho": "medio",
                "Idade": "jovem",
                "Tipo": "aquatico",
                "Imagem": "8_7_1_medio_jovem_aquatico"
            },{
                "Forca": 8,
                "Fofura": 7,
                "Velocidade": 1,
                "Tamanho": "medio",
                "Idade": "jovem",
                "Tipo": "aquatico",
                "Imagem": "8_7_1_medio_jovem_aquatico"
            },{
                "Forca": 1,
                "Fofura": 2,
                "Velocidade": 5,
                "Tamanho": "enorme",
                "Idade": "anciao",
                "Tipo": "terrestre",
                "Imagem": "1_2_5_enorme_anciao_terrestre"
            }, {
                "Forca": 9,
                "Fofura": 4,
                "Velocidade": 1,
                "Tamanho": "enorme",
                "Idade": "anciao",
                "Tipo": "aquatico",
                "Imagem": "8_7_1_medio_jovem_aquatico"
            },
                {
                    "Forca": 2,
                    "Fofura": 5,
                    "Velocidade": 6,
                    "Tamanho": "minusculo",
                    "Idade": "anciao",
                    "Tipo": "voador",
                    "Imagem": "2_5_6_minusculo_anciao_voador"
                },{
                "Forca": 8,
                "Fofura": 7,
                "Velocidade": 1,
                "Tamanho": "medio",
                "Idade": "jovem",
                "Tipo": "aquatico",
                "Imagem": "8_7_1_medio_jovem_aquatico"
            },{
                "Forca": 1,
                "Fofura": 2,
                "Velocidade": 5,
                "Tamanho": "enorme",
                "Idade": "anciao",
                "Tipo": "terrestre",
                "Imagem": "1_2_5_enorme_anciao_terrestre"
            }, {
                "Forca": 9,
                "Fofura": 4,
                "Velocidade": 1,
                "Tamanho": "enorme",
                "Idade": "anciao",
                "Tipo": "aquatico",
                "Imagem": "8_7_1_medio_jovem_aquatico"
            },
                {
                    "Forca": 2,
                    "Fofura": 5,
                    "Velocidade": 6,
                    "Tamanho": "minusculo",
                    "Idade": "anciao",
                    "Tipo": "voador",
                    "Imagem": "2_5_6_minusculo_anciao_voador"
                }]
        },
        {
            "nome": "Baralho2",
            "cartas": [{
                "Forca": 3,
                "Fofura": 7,
                "Velocidade": 8,
                "Tamanho": "grande",
                "Idade": "adolescente",
                "Tipo": "terrestre",
                "Imagem": "3_7_8_grande_adolescente_aquatico"
            },{
                "Forca": 1,
                "Fofura": 2,
                "Velocidade": 5,
                "Tamanho": "enorme",
                "Idade": "anciao",
                "Tipo": "terrestre",
                "Imagem": "1_2_5_enorme_anciao_terrestre"
            }, {
                "Forca": 10,
                "Fofura": 2,
                "Velocidade": 6,
                "Tamanho": "medio",
                "Idade": "adolescente",
                "Tipo": "voador",
                "Imagem": "10_2_6_medio_adolescente_voador"
            },
                {
                    "Forca": 3,
                    "Fofura": 7,
                    "Velocidade": 8,
                    "Tamanho": "grande",
                    "Idade": "adolescente",
                    "Tipo": "aquatico",
                    "Imagem": "3_7_8_grande_adolescente_aquatico"
                }]
        }
    ],
    "todasCartas": ['1_2_5_enorme_anciao_terrestre', '1_5_9_medio_adulto_voador', '2_3_10_pequeno_jovem_terrestre',
                    '2_5_6_minusculo_anciao_voador']
}

jogador3 = {
    "nome": "Jogador3",
    "baralhos": [
    ],
    "todasCartas": ['1_2_5_enorme_anciao_terrestre', '1_5_9_medio_adulto_voador', '2_3_10_pequeno_jovem_terrestre',
                    '2_5_6_minusculo_anciao_voador','1_2_5_enorme_anciao_terrestre', '1_5_9_medio_adulto_voador', '2_3_10_pequeno_jovem_terrestre',
                    '2_5_6_minusculo_anciao_voador','2_5_6_minusculo_anciao_voador']
}

def startInterface(message_queue, response_queue):
    cartas = 0
    janela = iniciaJanela(1200, 800)
    while True:
        nome, senha = TelaLogin(janela)
        message_queue.put(f"login {nome} {senha}")
        resposta = response_queue.get()
        if(resposta == "Success"):
            TelaMenuPrincipal(janela, jogador1, jogador2, jogador3)
        else:
            # mostrar pop-up ou escrever na tela o erro (provavelmente vai ta na 'resposta')
            continue


if __name__ == "__main__":
    startInterface()