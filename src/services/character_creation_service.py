# src/services/character_creation_service.py
import pygame
from typing import Dict, List, Any, Optional, Tuple
from src.entities.hero import Hero, HeroClass


class CharacterCreationService:
    """Serviço para orquestrar a criação de personagens"""

    def __init__(self, database):
        self.database = database

    def get_available_classes(self) -> List[Dict[str, Any]]:
        """Retorna todas as classes disponíveis do banco de dados"""
        return self.database.get_hero_classes()

    def get_class_by_key(self, class_key: str) -> Optional[Dict[str, Any]]:
        """Retorna uma classe específica pela chave"""
        return self.database.get_hero_class_by_key(class_key)

    def validate_character_name(self, name: str) -> Tuple[bool, str]:
        """Valida o nome do personagem"""
        if not name or not name.strip():
            return False, "O nome não pode estar vazio."

        if len(name) < 3:
            return False, "O nome deve ter pelo menos 3 caracteres."

        if len(name) > 16:
            return False, "O nome deve ter no máximo 16 caracteres."

        # Verifica caracteres válidos (apenas letras, números e espaços)
        if not all(c.isalnum() or c.isspace() for c in name):
            return False, "O nome pode conter apenas letras, números e espaços."

        # Verifica se já existe um personagem com esse nome
        existing_player = self.database.get_player(name)
        if existing_player:
            return False, "Já existe um personagem com esse nome."

        return True, "Nome válido."

    def calculate_final_attributes(
        self, base_attributes: Dict[str, int], class_data: Dict[str, Any]
    ) -> Dict[str, int]:
        """Calcula os atributos finais aplicando os bônus da classe"""
        final_attributes = base_attributes.copy()

        # Aplica bônus da classe
        bonuses = {
            "forca": class_data.get("strength_bonus", 0),
            "destreza": class_data.get("dexterity_bonus", 0),
            "vitalidade": class_data.get("vitality_bonus", 0),
            "inteligencia": class_data.get("intelligence_bonus", 0),
            "armadura": class_data.get("armor_bonus", 0),
            "energia": class_data.get("energy_bonus", 0),
            "stamina": class_data.get("stamina_bonus", 0),
        }

        for attr, bonus in bonuses.items():
            if attr in final_attributes:
                final_attributes[attr] = max(1, final_attributes[attr] + bonus)

        return final_attributes

    def calculate_derived_attributes(
        self, base_attributes: Dict[str, int], class_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calcula todos os atributos derivados baseados nos atributos base e bônus da classe"""
        # Aplica bônus primeiro
        effective_attrs = self.calculate_final_attributes(base_attributes, class_data)

        # Calcula todos os atributos derivados
        derived = {
            # Atributos básicos
            "vida_maxima": effective_attrs["vitalidade"] * 12
            + effective_attrs["forca"] * 3,
            "mana_maxima": effective_attrs["inteligencia"] * 10
            + effective_attrs["energia"] * 5,
            "dano_fisico_min": effective_attrs["forca"] * 2,
            "dano_fisico_max": effective_attrs["forca"] * 3
            + effective_attrs["destreza"],
            "dano_magico_min": effective_attrs["inteligencia"] * 2,
            "dano_magico_max": effective_attrs["inteligencia"] * 3,
            "defesa_fisica": effective_attrs["armadura"] * 3
            + effective_attrs["vitalidade"] // 2,
            "defesa_magica": effective_attrs["inteligencia"] * 2
            + effective_attrs["energia"],
            # Atributos detalhados
            "bloqueio": effective_attrs["armadura"] * 0.5,
            "chance_critico": effective_attrs["destreza"] * 0.6,
            "dano_critico": 150 + effective_attrs["destreza"] * 1.5,
            "chance_esquiva": effective_attrs["destreza"] * 0.4,
            "velocidade_ataque": 1.0 + effective_attrs["destreza"] * 0.03,
            "precisao": 80 + effective_attrs["destreza"] * 2,
            "regeneracao_vida": effective_attrs["vitalidade"] * 0.15,
            "regeneracao_mana": effective_attrs["energia"] * 0.25,
            "resistencia_fogo": effective_attrs["vitalidade"] * 0.6,
            "resistencia_gelo": effective_attrs["vitalidade"] * 0.6,
            "resistencia_eletrico": effective_attrs["vitalidade"] * 0.6,
            "resistencia_veneno": effective_attrs["vitalidade"] * 1.0,
            "resistencia_escuro": effective_attrs["inteligencia"] * 0.5,
            "sorte": effective_attrs["destreza"] * 0.4,
            "velocidade_movimento": 100 + effective_attrs["destreza"] * 2,
            "capacidade_carga": effective_attrs["forca"] * 10
            + effective_attrs["vitalidade"] * 5,
        }

        # Status iniciais
        derived["vida_atual"] = derived["vida_maxima"]
        derived["mana_atual"] = derived["mana_maxima"]
        derived["stamina_atual"] = effective_attrs["stamina"] * 10

        # Arredonda valores float
        for key, value in derived.items():
            if isinstance(value, float):
                derived[key] = round(value, 2)

        return {**effective_attrs, **derived}

    def create_character(
        self, name: str, class_key: str, base_attributes: Dict[str, int]
    ) -> Optional[Dict[str, Any]]:
        """Cria um novo personagem e retorna os dados para salvar"""
        # Valida o nome
        is_valid, message = self.validate_character_name(name)
        if not is_valid:
            print(f"❌ Nome inválido: {message}")
            return None

        # Obtém dados da classe
        class_data = self.get_class_by_key(class_key)
        if not class_data:
            print(f"❌ Classe {class_key} não encontrada.")
            return None

        # Calcula atributos finais
        final_attributes = self.calculate_derived_attributes(
            base_attributes, class_data
        )

        # Prepara dados do personagem
        character_data = {
            "name": name,
            "hero_class_id": class_data["id"],
            "level": 1,
            "experience": 0,
            "experience_to_next_level": 100,
            **final_attributes,
            "zona_id": 1,
            "posicao_x": 0.0,
            "posicao_y": 0.0,
            "gold": 0,
            "tempo_jogo": 0,
            "equipamento": "{}",
        }

        return character_data

    def get_class_display_info(self, class_key: str) -> Dict[str, Any]:
        """Retorna informações formatadas para exibição de uma classe"""
        class_data = self.get_class_by_key(class_key)
        if not class_data:
            return {}

        # Converte cor HEX para RGB
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip("#")
            return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

        return {
            "name": class_data["name"],
            "description": class_data["description"],
            "bonus": {
                "forca": class_data.get("strength_bonus", 0),
                "destreza": class_data.get("dexterity_bonus", 0),
                "vitalidade": class_data.get("vitality_bonus", 0),
                "inteligencia": class_data.get("intelligence_bonus", 0),
                "armadura": class_data.get("armor_bonus", 0),
                "energia": class_data.get("energy_bonus", 0),
                "stamina": class_data.get("stamina_bonus", 0),
            },
            "primary_attribute": class_data.get("primary_attribute", "forca"),
            "color": hex_to_rgb(class_data.get("color_hex", "#FFFFFF")),
            "icon_path": class_data.get("icon_path", ""),
        }
