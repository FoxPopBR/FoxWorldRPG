from typing import List, Optional, Tuple
import pygame
from src.states.base_state import BaseState


class StateManager:
    """Gerenciador de estados do jogo"""

    def __init__(self, game):
        self.game = game
        self.states: List[BaseState] = []
        self._pending_change = None

    def push_state(self, state: BaseState):
        """Adiciona um novo estado na pilha"""
        self.states.append(state)
        state.enter()

    def pop_state(self) -> Optional[BaseState]:
        """Remove o estado atual da pilha"""
        if self.states:
            state = self.states.pop()
            state.exit()
            return state
        return None

    def change_state(self, state: BaseState):
        """Troca completamente o estado atual"""
        self._pending_change = state

    def _process_pending_change(self):
        """Processa mudanças de estado pendentes"""
        if self._pending_change:
            while self.states:
                self.pop_state()
            self.push_state(self._pending_change)
            self._pending_change = None

    def handle_event(self, event):
        """Delega eventos para o estado atual"""
        if self.states:
            self.states[-1].handle_event(event)

    def update(self):
        """Atualiza o estado atual"""
        self._process_pending_change()
        if self.states:
            self.states[-1].update()

    def render(self, surface, world_surface=None):
        """Renderiza o estado atual"""
        if self.states:
            self.states[-1].render(surface, world_surface)

    def on_resize(self, old_size: Tuple[int, int], new_size: Tuple[int, int]):
        """Notifica todos os estados sobre mudança de tamanho"""
        for state in self.states:
            if hasattr(state, "on_resize"):
                state.on_resize(old_size, new_size)
