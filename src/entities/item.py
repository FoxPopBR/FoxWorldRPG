from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any


class ItemType(Enum):
    """Tipos de itens do jogo."""

    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    CONSUMABLE = "consumable"


class Rarity(Enum):
    """Raridades de itens com cores associadas."""

    COMMON = ("common", (200, 200, 200))
    UNCOMMON = ("uncommon", (100, 255, 100))
    RARE = ("rare", (100, 150, 255))
    EPIC = ("epic", (200, 100, 255))
    LEGENDARY = ("legendary", (255, 200, 0))

    def __init__(self, value, color):
        self._value_ = value
        self.color = color


@dataclass
class Item:
    """Representa um item no jogo (arma, armadura, consumível, etc)."""

    id: str
    name: str
    type: ItemType
    description: str
    rarity: Rarity = Rarity.COMMON
    icon_path: str = ""
    icon_coords: tuple = (0, 0)  # (row, col) no atlas

    # Atributos de combate
    atk: int = 0
    def_: int = 0
    armadura: int = 0
    resistencia: int = 0

    # Atributos de slot (para equipáveis)
    slot: Optional[str] = None

    # Consumíveis
    stackable: bool = False
    max_stack: int = 1
    effect: str = ""
    effect_value: int = 0

    # Outros
    value: int = 0
    weight: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Converte item para dicionário para salvar."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "rarity": self.rarity.value,
            "icon_path": self.icon_path,
            "icon_coords": self.icon_coords,
            "atk": self.atk,
            "def": self.def_,
            "armadura": self.armadura,
            "resistencia": self.resistencia,
            "slot": self.slot,
            "stackable": self.stackable,
            "max_stack": self.max_stack,
            "effect": self.effect,
            "effect_value": self.effect_value,
            "value": self.value,
            "weight": self.weight,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Item":
        """Cria item a partir de dicionário."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            type=ItemType(data.get("type", "consumable")),
            description=data.get("description", ""),
            rarity=Rarity(data.get("rarity", "common")),
            icon_path=data.get("icon_path", ""),
            icon_coords=data.get("icon_coords", (0, 0)),
            atk=data.get("atk", 0),
            def_=data.get("def", 0),
            armadura=data.get("armadura", 0),
            resistencia=data.get("resistencia", 0),
            slot=data.get("slot"),
            stackable=data.get("stackable", False),
            max_stack=data.get("max_stack", 1),
            effect=data.get("effect", ""),
            effect_value=data.get("effect_value", 0),
            value=data.get("value", 0),
            weight=data.get("weight", 0),
        )
