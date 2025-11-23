# Inventário de Assets - Tema Padrão

## Visão Geral
Este documento cataloga todos os assets visuais que compõem o **Tema Padrão** do FoxWorld RPG.

---

## Assets Implementados

### 🖼️ Backgrounds
| Asset | Caminho | Dimensões | Uso |
|-------|---------|-----------|-----|
| Background Principal | `images/titles/title_background.jpg` | Variável | Menu inicial e telas de configuração |

### 🔘 Botões
| Asset | Caminho | Dimensões | Uso |
|-------|---------|-----------|-----|
| Botão Normal | `images/button/button_main_menu_ON.png` | 400px largura | Botões principais (Novo Jogo, Configurações, etc.) |
| Botão Pressionado | `images/button/button_main_menu_OFF.png` | 400px largura | Estado "pressed" dos botões principais |
| Botão Pequeno Normal | `images/button/small_button_padrao_ON.png` | ~40px | Controles +/- (volume, etc.) |
| Botão Pequeno Pressionado | `images/button/small_button_padrao_OFF.png` | ~40px | Estado "pressed" dos controles |

### 📝 Textos e Títulos
| Asset | Caminho | Dimensões | Uso |
|-------|---------|-----------|-----|
| Título do Jogo | `images/titles/title_FoxWorldRPG.png` | Variável | Logo na tela inicial |

---

## Telas que Utilizam o Tema

### ✅ Implementadas
1. **Menu Principal** (`menu.py`)
   - Background: `menu_background`
   - Botões: `button_normal/pressed`
   - Título: `title_image`
   - Efeito: Sistema de partículas (procedural)

2. **Configurações** (`settings_state.py`)
   - Background: `menu_background` (escurecido 50%)
   - Botões: `button_normal/pressed`

3. **Configurações de Vídeo** (`video_settings_state.py`)
   - Background: `menu_background` (escurecido 50%)
   - Botões: `button_normal/pressed`

4. **Configurações de Áudio** (`audio_settings_state.py`)
   - Background: `menu_background` (escurecido 50%)
   - Botões: `button_normal/pressed`
   - Botões pequenos: `small_button_normal/pressed`

5. **Seleção de Tema** (`theme_selection_state.py`)
   - Background: `menu_background` (escurecido 50%)
   - Botões: `button_normal/pressed`

6. **Seleção de Slot** (`game_slot_select_state.py`)
   - Background: `menu_background` (escurecido 50%)
   - Botões: `button_normal/pressed`

### ⏳ A Implementar
- Criação de Personagem
- Tela de Jogo (HUD e UI)
- Inventário
- Diálogos
- Combate

---

## Efeitos Visuais

### Sistema de Partículas
- **Tipo:** Procedural (gerado em código)
- **Arquivo:** `src/ui/particles.py`
- **Uso:** Menu Principal (fundo)
- **Características:**
  - 4 tipos de texturas (Starburst, X-Ray, Diamond, Orb)
  - Transparência: 10-80%
  - Tamanho: 9-13px
  - Cores: Branco, Dourado, Azul Pálido

---

## Estrutura de Diretórios

```
assets/
├── images/
│   ├── titles/
│   │   ├── title_background.jpg
│   │   └── title_FoxWorldRPG.png
│   └── button/
│       ├── button_main_menu_ON.png
│       ├── button_main_menu_OFF.png
│       ├── small_button_padrao_ON.png
│       └── small_button_padrao_OFF.png
```

---

## Notas de Implementação
- Todos os assets são carregados via `ThemeManager`
- Caminhos são resolvidos dinamicamente através de `menu_assets.py`
- Sistema preparado para adicionar temas alternativos no futuro
