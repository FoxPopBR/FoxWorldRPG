# 🗺️ Roadmap Fase 2: Implementação de Gameplay

Este documento descreve o "Plano Mestre" para a implementação da jogabilidade do FoxWorld RPG, focando na separação entre Overworld (2D) e Dungeons (Pseudo-3D).

## 🎯 Visão Geral

O projeto adotará uma abordagem híbrida clássica (estilo Phantasy Star 1):
1.  **Overworld (Mundo Aberto)**: Visualização 2D Top-Down (vista de cima).
2.  **Dungeons (Cavernas/Interiores)**: Visualização Pseudo-3D (Raycasting) baseada em grid.

## 🛠️ Requisitos Técnicos

### Software & Bibliotecas
-   **Engine**: Python + `pygame-ce` (Community Edition)
-   **Mapas**: `pytmx` (para carregar mapas .tmx do Tiled)
-   **Editor de Mapas**: Tiled Map Editor
-   **Pixel Art**: Pyxel Edit ou Aseprite

### Padrões Visuais (A Regra de Ouro)
-   **Tile Size**: 32x32 pixels.
-   **Resolução Interna**: 640x360 (16:9) ou 480x270.
    -   *Motivo*: O jogo será renderizado nesta resolução baixa para manter o pixel art "crocante" e depois escalado para a resolução da tela do jogador (Full HD/4K) pelo `UIScaler`.

---

## 📅 Roteiro de Implementação

### FASE 2.1: Pipeline do Overworld (Foco Imediato)

O objetivo é criar o sistema de exploração do mundo aberto.

#### Passo A: Criação de Assets (Arte)
-   **Ferramenta**: Pyxel Edit.
-   **Output**: `overworld_tileset.png` (com fundo transparente).
-   **Conteúdo Inicial**:
    -   Grama básica.
    -   Transições (Grama->Água, Grama->Terra).
    -   Objetos de colisão (Árvores, Pedras).

#### Passo B: Montagem do Mapa (Level Design)
-   **Ferramenta**: Tiled Map Editor.
-   **Configuração**: Mapas ortogonais, tiles 32x32.
-   **Camadas (Layers)**:
    1.  `Ground` (Chão base).
    2.  `Decoration` (Detalhes não-colidíveis).
    3.  `Collision` / `Walls` (Objetos que bloqueiam movimento).
-   **Output**: `mapa_mundo.tmx`.

#### Passo C: Implementação no Código
-   **Biblioteca**: `pytmx`.
-   **Lógica**:
    -   Carregar o arquivo `.tmx`.
    -   Renderizar as camadas visuais.
    -   Implementar movimento **Grid-Based** (personagem desliza de tile em tile, 32px por vez).
    -   Sistema de colisão checando a camada `Collision`.

---

### FASE 2.2: Dungeons & Interiores (Raycasting)

O objetivo é criar a imersão de exploração de masmorras.

#### Conceito
Em vez de desenhar centenas de imagens estáticas para cada corredor, usaremos **Raycasting** (técnica do Wolfenstein 3D).

#### Processo
1.  **Mapa Lógico**: Criar um mapa no Tiled (`caverna_01.tmx`) onde tiles específicos representam paredes.
2.  **Texturas**: Usar tiles 32x32 de "parede" e "chão" do tileset existente.
3.  **Engine**: O Pygame lerá a "planta baixa" do Tiled e renderizará as paredes verticalmente para criar a ilusão de 3D.

---

## 🚀 Próximos Passos (Checklist Imediato)

1.  [ ] Atualizar dependências para `pygame-ce` e `pytmx`.
2.  [ ] Criar estrutura de pastas `assets/maps` e `assets/tilesets`.
3.  [ ] Criar o primeiro tileset de teste (Grama, Água, Árvore).
4.  [ ] Criar o primeiro mapa de teste no Tiled.
5.  [ ] Implementar `WorldMapState` para carregar e exibir o mapa.
