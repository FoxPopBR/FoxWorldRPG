# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [0.0.01] - 2025-11-23

### Adicionado
- **Infraestrutura Core**:
    - `Game`: Loop principal e gerenciamento de janelas.
    - `StateManager`: Sistema de estados com pilha (Push/Pop/Change).
    - `GameConfig`: Hub central de configuração e injeção de dependência.
    - `ResourceManager`: Carregamento e cache de assets (imagens, sons, fontes).
    - `DatabaseManager`: Persistência SQLite com migrações automáticas.
- **Interface de Usuário (UI)**:
    - `UIScaler`: Sistema de escala responsiva para múltiplas resoluções.
    - `ThemeManager`: Sistema de temas via JSON (Default, Christmas, Halloween).
    - Componentes: Botões, Menus, Notificações.
- **Funcionalidades de Jogo**:
    - **Slots de Save**: Gerenciamento de 5 slots de perfil.
    - **Criação de Personagem**: Seleção de 5 classes (Bárbaro, Paladino, Druida, Feiticeiro, Necromante).
    - **Persistência**: Salvar e Carregar progresso do jogador.
    - **HUD**: Interface de jogo com status do herói.
    - **Grupo**: Tela de visualização do grupo de heróis.

### Corrigido
- Inicialização incorreta de `ResourceManager` e `HeroManager` na classe `Game`.
- Erros de indentação e lógica na seleção de slots.
- Carregamento de assets de herói e exibição na HUD/Grupo.

### Segurança
- Validação básica de dados ao carregar saves.
