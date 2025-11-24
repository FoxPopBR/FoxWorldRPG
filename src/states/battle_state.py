import pygame
import random
from src.states.base_state import BaseState
from src.ui.button import Button
from src.ui.ui_panel import UIPanel
from src.entities.enemy import Enemy
from src.core.battle_calculator import BattleCalculator
from src.ui.floating_text import FloatingTextManager


import pygame
import random
from src.states.base_state import BaseState
from src.ui.button import Button
import pygame
import random
from src.states.base_state import BaseState
from src.ui.button import Button
from src.ui.ui_panel import UIPanel
from src.entities.enemy import Enemy
from src.core.battle_calculator import BattleCalculator
from src.ui.floating_text import FloatingTextManager


import pygame
import random
from src.states.base_state import BaseState
from src.ui.button import Button
from src.ui.ui_panel import UIPanel
from src.entities.enemy import Enemy
from src.core.battle_calculator import BattleCalculator
from src.ui.floating_text import FloatingTextManager


class BattleState(BaseState):
    """Estado de Batalha - Estilo Phantasy Star (Refatorado)"""

    def __init__(self, game):
        super().__init__(game)
        self.hero = self.game.game_config.hero_manager.get_active_hero()

        # Lista de Inimigos
        self.enemies = [Enemy.create_rat()]
        self._load_enemy_images()

        # UI Assets
        self.panel = UIPanel(
            "assets/images/Box/painel_medio_retangulo_ferro.png",
            corner_size=32,
        )

        # Gerenciador de texto flutuante
        self.floating_texts = FloatingTextManager(game)

        # Estado do turno
        self.turn_state = "PLAYER_INPUT"
        self.turn_timer = 0
        self.current_enemy_index = 0

        self.buttons = []
        self._create_ui()

    def _load_enemy_images(self):
        for enemy in self.enemies:
            try:
                if not enemy.image:
                    img = pygame.image.load(enemy.image_path).convert_alpha()
                    # Escala menor (1.5x em vez de 3x)
                    w, h = img.get_size()
                    enemy.image = pygame.transform.scale(
                        img, (int(w * 1.5), int(h * 1.5))
                    )
            except Exception as e:
                print(f"❌ Erro ao carregar imagem do inimigo: {e}")

    def _create_ui(self):
        # Botões de ação (Centro Esquerda)
        # Layout: Vertical

        btn_w = 180
        btn_h = 50
        x_base = 50
        y_base = self.game.display_config.height // 2 - 100

        actions = ["ATACAR", "MAGIA", "ITEM", "FUGIR"]

        for i, label in enumerate(actions):
            btn = Button(
                x_base,
                y_base + i * (btn_h + 10),
                btn_w,
                btn_h,
                label,
                lambda l=label: self._on_action_click(l),
                font_size=24,
                button_image_normal=pygame.image.load(
                    "assets/images/button/botao_rust_medio.png"
                ).convert_alpha(),
                button_image_pressed=pygame.image.load(
                    "assets/images/button/botao_rust_medio.png"
                ).convert_alpha(),
            )
            self.buttons.append(btn)

    def _on_action_click(self, action):
        if self.turn_state != "PLAYER_INPUT":
            return

        if action == "ATACAR":
            self._player_attack()
        elif action == "FUGIR":
            self._exit_battle()
        else:
            print(f"Ação {action} não implementada ainda.")

    def _player_attack(self):
        if not self.enemies:
            return

        target = self.enemies[self.current_enemy_index]
        print(f"⚔️ {self.hero.name} ataca {target.name}!")

        dmg, is_crit = BattleCalculator.calculate_physical_damage(
            self.hero.stats, target.stats
        )
        target.stats.vida_atual = max(0, target.stats.vida_atual - dmg)

        # Texto flutuante
        color = (255, 255, 0) if is_crit else (255, 255, 255)
        text = f"{dmg}!" if not is_crit else f"CRÍTICO {dmg}!"

        # Posição do inimigo
        cx = self.game.display_config.width // 2
        cy = self.game.display_config.height // 2
        self.floating_texts.add_text(cx, cy - 50, text, color)

        self.turn_state = "PLAYER_ANIM"
        self.turn_timer = 0.8

    def _enemy_turn(self):
        alive_enemies = [e for e in self.enemies if e.stats.vida_atual > 0]

        if not alive_enemies:
            self.turn_state = "VICTORY"
            return

        attacker = alive_enemies[0]

        print(f"🐺 {attacker.name} ataca!")
        dmg, is_crit = BattleCalculator.calculate_physical_damage(
            attacker.stats, self.hero.stats
        )
        self.hero.stats.vida_atual = max(0, self.hero.stats.vida_atual - dmg)

        # Texto flutuante no HUD do herói (Painel 1)
        # Painel 1 fica na esquerda inferior
        panel_w = self.game.display_config.width // 4
        hx = panel_w // 2
        hy = self.game.display_config.height - 100

        self.floating_texts.add_text(hx, hy, f"-{dmg}", (255, 50, 50))

        self.turn_state = "ENEMY_ANIM"
        self.turn_timer = 0.8

    def _exit_battle(self):
        from src.states.game_state import GameState

        self.game.state_manager.change_state(GameState(self.game))

    def update(self):
        dt = self.game.clock.get_time() / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        for btn in self.buttons:
            btn.update(mouse_pos)

        self.floating_texts.update()

        # Remove inimigos mortos da lista visual
        # Mantém lógica de índices consistente?
        # Simplesmente filtra para renderização e lógica de alvo

        # Lógica de Turnos
        if self.turn_state == "PLAYER_ANIM":
            self.turn_timer -= dt
            if self.turn_timer <= 0:
                if all(e.stats.vida_atual <= 0 for e in self.enemies):
                    self.turn_state = "VICTORY"
                    self.turn_timer = 1.0  # Inicia timer para processar vitória
                else:
                    self.turn_state = "ENEMY_TURN"
                    self._enemy_turn()

        elif self.turn_state == "ENEMY_ANIM":
            self.turn_timer -= dt
            if self.turn_timer <= 0:
                if self.hero.stats.vida_atual <= 0:
                    self.turn_state = "DEFEAT"
                else:
                    self.turn_state = "PLAYER_INPUT"

        elif self.turn_state == "VICTORY":
            if self.turn_timer == 1.0:
                self._process_victory()
                self.turn_timer = 0
            # Aguarda input

        elif self.turn_state == "DEFEAT":
            self._exit_battle()

    def _process_victory(self):
        """Processa recompensas de vitória e salva o jogo."""
        total_xp = 0
        total_gold = 0

        for enemy in self.enemies:
            # XP base + bônus aleatório
            xp = enemy.level * 20
            gold = enemy.level * 10

            total_xp += xp
            total_gold += gold

        print(f"🏆 Vitória! Ganhou {total_xp} XP e {total_gold} Ouro!")

        # Atualiza Herói
        self.hero.experience += total_xp
        self.hero.gold += total_gold

        # Salva no Banco de Dados
        try:
            self.game.game_config.hero_manager.update_hero(self.hero)
            print("💾 Progresso salvo com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao salvar progresso pós-batalha: {e}")

    def handle_event(self, event):
        if self.turn_state == "PLAYER_INPUT":
            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn in self.buttons:
                    if btn.handle_event(event):
                        return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._on_action_click("FUGIR")

        elif self.turn_state == "VICTORY":
            # Fecha com qualquer tecla ou clique no botão OK (que vamos adicionar)
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                    self._exit_battle()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Verifica clique no botão OK do popup
                cx, cy = (
                    self.game.display_config.width // 2,
                    self.game.display_config.height // 2,
                )
                ok_btn_rect = pygame.Rect(cx - 50, cy + 60, 100, 40)
                if ok_btn_rect.collidepoint(event.pos):
                    self._exit_battle()

    def render(self, surface, world_surface=None):
        # 1. Fundo
        surface.fill((10, 5, 15))

        # 2. Inimigos (Centro)
        alive_enemies = [e for e in self.enemies if e.stats.vida_atual > 0]
        if alive_enemies:
            enemy = alive_enemies[0]
            if enemy.image:
                ex = self.game.display_config.width // 2 - enemy.image.get_width() // 2
                ey = (
                    self.game.display_config.height // 2 - enemy.image.get_height() // 2
                )
                surface.blit(enemy.image, (ex, ey))

        # 3. Lista de Inimigos (Topo Direito)
        self._render_enemy_list(surface, alive_enemies)

        # 4. HUD Inferior (4 Painéis)
        self._render_hud(surface)

        # 5. Botões
        for btn in self.buttons:
            btn.render(surface)

        # 6. Textos Flutuantes
        self.floating_texts.render(surface)

        # 7. Victory Popup
        if self.turn_state == "VICTORY":
            self._render_victory_popup(surface)

    def _render_victory_popup(self, surface):
        # Fundo semi-transparente
        overlay = pygame.Surface(
            (self.game.display_config.width, self.game.display_config.height),
            pygame.SRCALPHA,
        )
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        # Caixa de Vitória
        box_w, box_h = 400, 200
        cx, cy = (
            self.game.display_config.width // 2,
            self.game.display_config.height // 2,
        )
        rect = pygame.Rect(cx - box_w // 2, cy - box_h // 2, box_w, box_h)

        # Desenha painel (usando UIPanel se possível, ou rect simples)
        pygame.draw.rect(surface, (20, 20, 20), rect)
        pygame.draw.rect(surface, (255, 215, 0), rect, 3)  # Borda Dourada

        font_title = self.game.ui_scaler.get_themed_font("title")
        font_text = self.game.ui_scaler.get_themed_font("menu")

        # Título
        title = font_title.render("VITÓRIA!", True, (255, 215, 0))
        surface.blit(title, (cx - title.get_width() // 2, rect.y + 20))

        # Recompensas (Recalculando apenas para display - idealmente seria salvo em self.rewards)
        # Como é simples, calculamos aqui
        total_xp = sum(e.level * 20 for e in self.enemies)
        total_gold = sum(e.level * 10 for e in self.enemies)

        xp_text = font_text.render(f"XP: +{total_xp}", True, (200, 200, 255))
        gold_text = font_text.render(f"Ouro: +{total_gold}", True, (255, 255, 0))

        surface.blit(xp_text, (cx - xp_text.get_width() // 2, rect.y + 80))
        surface.blit(gold_text, (cx - gold_text.get_width() // 2, rect.y + 120))

        # Botão OK
        ok_rect = pygame.Rect(cx - 50, cy + 60, 100, 40)
        pygame.draw.rect(surface, (60, 180, 60), ok_rect, border_radius=5)
        pygame.draw.rect(surface, (200, 255, 200), ok_rect, 2, border_radius=5)

        ok_text = font_text.render("OK", True, (255, 255, 255))
        surface.blit(
            ok_text,
            (
                ok_rect.centerx - ok_text.get_width() // 2,
                ok_rect.centery - ok_text.get_height() // 2,
            ),
        )

    def _render_enemy_list(self, surface, enemies):
        if not enemies:
            return

        font = self.game.ui_scaler.get_themed_font("menu")

        # Caixa no topo direito
        box_w = 300
        box_h = len(enemies) * 30 + 20
        start_x = self.game.display_config.width - box_w - 20
        start_y = 20

        bg_rect = pygame.Rect(start_x, start_y, box_w, box_h)
        pygame.draw.rect(surface, (0, 0, 0), bg_rect)
        pygame.draw.rect(surface, (255, 255, 255), bg_rect, 2)

        for i, enemy in enumerate(enemies):
            text = (
                f"{enemy.name}   HP {enemy.stats.vida_atual}/{enemy.stats.vida_maxima}"
            )
            surf = font.render(text, True, (255, 255, 255))
            surface.blit(surf, (start_x + 10, start_y + 10 + i * 30))

            if i == self.current_enemy_index:
                arrow = font.render(">", True, (255, 255, 0))
                surface.blit(arrow, (start_x - 15, start_y + 10 + i * 30))

    def _render_hud(self, surface):
        # Divide a parte inferior em 4 painéis
        panel_h = 180
        total_w = self.game.display_config.width
        panel_w = total_w // 4
        y = self.game.display_config.height - panel_h

        # Painel 1: Herói Atual
        rect1 = pygame.Rect(0, y, panel_w, panel_h)
        self.panel.draw(surface, rect1)
        self._render_hero_status(surface, rect1, self.hero)

        # Painéis 2, 3, 4 (Vazios por enquanto)
        for i in range(1, 4):
            rect = pygame.Rect(i * panel_w, y, panel_w, panel_h)
            self.panel.draw(surface, rect)
            # Placeholder "Vazio"
            font = self.game.ui_scaler.get_themed_font("menu_small")
            txt = font.render("VAZIO", True, (100, 100, 100))
            surface.blit(
                txt,
                (
                    rect.centerx - txt.get_width() // 2,
                    rect.centery - txt.get_height() // 2,
                ),
            )

    def _render_hero_status(self, surface, rect, hero):
        # Layout compacto dentro do painel
        # Nome Lvl
        # HP Bar
        # MP Bar

        font_name = self.game.ui_scaler.get_themed_font("menu_small")
        font_bar = self.game.ui_scaler.get_themed_font("text")

        # Margem
        mx = rect.x + 20
        my = rect.y + 20

        # Nome
        name = font_name.render(f"{hero.name} Lv.{hero.level}", True, (255, 255, 255))
        surface.blit(name, (mx, my))

        # Barras
        bar_w = rect.width - 40
        bar_h = 15
        by = my + 35

        def draw_bar(val, max_val, color, label):
            nonlocal by
            pct = max(0, min(1, val / max(1, max_val)))
            pygame.draw.rect(surface, (30, 30, 30), (mx, by, bar_w, bar_h))
            pygame.draw.rect(surface, color, (mx, by, int(bar_w * pct), bar_h))
            pygame.draw.rect(surface, (100, 100, 100), (mx, by, bar_w, bar_h), 1)

            txt = font_bar.render(
                f"{label} {int(val)}/{int(max_val)}", True, (255, 255, 255)
            )
            surface.blit(txt, (mx + 5, by - 1))
            by += bar_h + 8

        draw_bar(hero.stats.vida_atual, hero.stats.vida_maxima, (200, 50, 50), "HP")
        draw_bar(hero.stats.mana_atual, hero.stats.mana_maxima, (50, 50, 200), "MP")
