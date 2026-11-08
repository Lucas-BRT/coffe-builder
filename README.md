# Coffe Builder

## Dependências

instale as dependências do projeto rodando o comando abaixo

```bash
pip install -r requirements.txt
```

## Rodando

o projeto deve ser rodado como módulo, tendo commo entrypoint o arquivo main

```bash
python -m src.main
```

## Controles

### Câmeras

| Tecla / ação             | O que faz                                                       |
| ------------------------ | --------------------------------------------------------------- |
| `C`                      | alterna entre a câmera isométrica e a de primeira pessoa        |
| `W` `A` `S` `D`          | anda pelo mapa (isométrica) ou pela cafeteria (primeira pessoa) |
| mouse                    | olha ao redor (primeira pessoa)                                 |
| roda do mouse, `=` e `-` | zoom (isométrica)                                               |
| `Shift` + `Q` / `E`      | gira a câmera isométrica em 90°                                 |
| `M`                      | alterna entre malha sólida e wireframe                          |
| `N`                      | troca o sol pela lua (e vice-versa)                             |
| `Esc`                    | fecha o jogo                                                    |

### Edição (câmera isométrica)

| Tecla / ação                                  | O que faz                                                                   |
| --------------------------------------------- | --------------------------------------------------------------------------- |
| arrastar um item da barra lateral para a cena | cria o objeto na célula sob o cursor                                        |
| roda do mouse sobre a barra lateral           | rola a lista de objetos                                                     |
| clique e arraste um objeto                    | seleciona e move, uma célula por vez                                        |
| `Shift` + clique e arraste                    | pega também as peças de dentro de um grupo e move em passos de 0,1          |
| `R`                                           | gira o objeto selecionado em 90°                                            |
| `Backspace`                                   | apaga o objeto selecionado                                                  |
| `Espaço`                                      | aciona o objeto selecionado (liga e desliga a luminária)                    |
| clique em área vazia                          | limpa a seleção                                                             |
| `Tab` e setas                                 | seleciona o próximo objeto da lista e move o selecionado em pequenos passos |
| `Enter`                                       | cria um quadrado                                                            |

## Tutorial

1. **Escolha o ponto de vista.** O jogo abre na câmera isométrica, que é a de edição. Use `C` para ver a cafeteria em primeira pessoa, andando com `W` `A` `S` `D` e olhando com o mouse.
2. **Adicione objetos.** Na barra lateral esquerda, arraste um item (cadeira, mesa, balcão, luminária...) até a cena. O objeto aparece na célula sob o cursor, que fica amarelo quando está sobre algo já existente.
3. **Mova e organize.** Clique num objeto e arraste. Ele anda de célula em célula e é solto onde você largar o botão. Um conjunto de mesa e cadeiras anda junto, como um grupo só.
4. **Mexa nas peças.** Com `Shift`, o clique pega uma peça de dentro do grupo, como uma cadeira da mesa. Nesse modo vc pode ajustar a posição mais fina do objeto.
5. **Gire e apague.** Com um objeto selecionado, `R` gira em 90° e `Backspace` apaga.
6. **Ajuste a iluminação.** Selecione uma luminária e aperte `Espaço` para ligar ou desligar. `N` alterna entre o sol (de dia) e a lua (de noite), que é mais fraca e azulada.

## Texturas

Boa parte das texturas foram geradas proceduralmente usando o código `scripts/gerar_texturas.py`. Elas são geradas em `assets/textures`. O foco é apenas não deixar o pacote do jogo muito pesado, então quando vc executa ele deve gerar as texutas antes de iniciar. O alogritmo de geração de texturas foi feito com ajuda de AI, mas como dito, é só pq ninguém merece ficar lotando o espaço alheio com texturas, além de asssim permitir que a gente calibre a aparência do jogo, oq ajuda no debug.
