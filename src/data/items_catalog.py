from src.entities.item import Item, ItemType, Rarity


# Catálogo de Itens do Jogo
ITEMS_CATALOG = {
    # === ARMAS ===
    "iron_sword": Item(
        id="iron_sword",
        name="Espada de Ferro",
        type=ItemType.WEAPON,
        description="Uma espada simples de ferro.",
        rarity=Rarity.COMMON,
        icon_path="assets/images/items/weapons/iron_sword.png",
        icon_coords=(5, 1),  # Atualizado via JSON
        atk=5,
        slot="main_hand",
        value=50,
        weight=5,
    ),
    "wooden_shield": Item(
        id="wooden_shield",
        name="Escudo de Madeira",
        type=ItemType.ARMOR,
        description="Proteção básica.",
        rarity=Rarity.COMMON,
        icon_path="assets/images/items/armor/wooden_shield.png",
        icon_coords=(7, 0),  # Atualizado via JSON
        def_=3,
        slot="off_hand",
        value=30,
        weight=3,
    ),
    "steel_axe": Item(
        id="steel_axe",
        name="Machado de Aço",
        type=ItemType.WEAPON,
        description="Um machado pesado e poderoso.",
        rarity=Rarity.UNCOMMON,
        icon_path="assets/images/items/weapons/steel_axe.png",
        icon_coords=(5, 11),  # Atualizado via JSON
        atk=8,
        slot="main_hand",
        value=120,
        weight=8,
    ),
    # === ARMADURAS ===
    "leather_armor": Item(
        id="leather_armor",
        name="Couro Batido",
        type=ItemType.ARMOR,
        description="Armadura leve de couro.",
        rarity=Rarity.COMMON,
        icon_path="assets/images/items/armor/leather_armor.png",
        icon_coords=(8, 4),  # Atualizado via JSON
        armadura=5,
        resistencia=2,
        slot="chest",
        value=60,
        weight=4,
    ),
    "iron_helmet": Item(
        id="iron_helmet",
        name="Elmo de Ferro",
        type=ItemType.ARMOR,
        description="Protege a cabeça.",
        rarity=Rarity.COMMON,
        icon_path="assets/images/items/armor/iron_helmet.png",
        icon_coords=(8, 2),  # Atualizado via JSON
        armadura=3,
        slot="head",
        value=40,
        weight=2,
    ),
    "iron_boots": Item(
        id="iron_boots",
        name="Botas de Ferro",
        type=ItemType.ARMOR,
        description="Botas resistentes.",
        rarity=Rarity.COMMON,
        icon_path="assets/images/items/armor/iron_boots.png",
        icon_coords=(9, 3),  # Atualizado via JSON
        armadura=2,
        slot="feet",
        value=35,
        weight=2,
    ),
    # === ACESSÓRIOS ===
    "strength_ring": Item(
        id="strength_ring",
        name="Anel de Força",
        type=ItemType.ACCESSORY,
        description="Aumenta a força do usuário.",
        rarity=Rarity.RARE,
        icon_path="assets/images/items/accessories/strength_ring.png",
        icon_coords=(9, 4),  # Atualizado via JSON (Ring Gold placeholder)
        atk=3,
        slot="ring_l",
        value=200,
        weight=0,
    ),
    "defense_amulet": Item(
        id="defense_amulet",
        name="Amuleto de Proteção",
        type=ItemType.ACCESSORY,
        description="Oferece proteção mágica.",
        rarity=Rarity.RARE,
        icon_path="assets/images/items/accessories/defense_amulet.png",
        icon_coords=(9, 7),  # Atualizado via JSON (Necklace Ruby placeholder)
        resistencia=5,
        slot="neck",
        value=250,
        weight=0,
    ),
    # === CONSUMÍVEIS ===
    "health_potion": Item(
        id="health_potion",
        name="Poção de Vida",
        type=ItemType.CONSUMABLE,
        description="Restaura 50 HP.",
        rarity=Rarity.COMMON,
        icon_path="assets/images/items/consumables/health_potion.png",
        icon_coords=(10, 0),  # Atualizado via JSON
        stackable=True,
        max_stack=99,
        effect="heal_hp",
        effect_value=50,
        value=20,
        weight=1,
    ),
    "mana_potion": Item(
        id="mana_potion",
        name="Poção de Mana",
        type=ItemType.CONSUMABLE,
        description="Restaura 30 MP.",
        rarity=Rarity.COMMON,
        icon_path="assets/images/items/consumables/mana_potion.png",
        icon_coords=(10, 1),  # Atualizado via JSON
        stackable=True,
        max_stack=99,
        effect="heal_mp",
        effect_value=30,
        value=25,
        weight=1,
    ),
    "stamina_potion": Item(
        id="stamina_potion",
        name="Poção de Energia",
        type=ItemType.CONSUMABLE,
        description="Restaura 40 Stamina.",
        rarity=Rarity.UNCOMMON,
        icon_path="assets/images/items/consumables/stamina_potion.png",
        icon_coords=(10, 2),  # Atualizado via JSON
        stackable=True,
        max_stack=99,
        effect="heal_stamina",
        effect_value=40,
        value=30,
        weight=1,
    ),
    # === MATERIAIS/DROPS ===
    "rat_pelt": Item(
        id="rat_pelt",
        name="Pele de Rato",
        type=ItemType.CONSUMABLE,
        description="Material de artesanato.",
        rarity=Rarity.COMMON,
        icon_path="assets/images/items/materials/rat_pelt.png",
        icon_coords=(14, 0),  # Wood placeholder (Stone was 14,1)
        stackable=True,
        max_stack=99,
        value=5,
        weight=1,
    ),
}


def create_item(item_id: str, quantity: int = 1) -> dict:
    """
    Factory function para criar um item a partir do catálogo.

    Args:
        item_id: ID do item no catálogo
        quantity: Quantidade (para stackables)

    Returns:
        Dicionário do item pronto para adicionar ao inventário
    """
    if item_id not in ITEMS_CATALOG:
        raise ValueError(f"Item '{item_id}' não encontrado no catálogo!")

    item = ITEMS_CATALOG[item_id]
    item_dict = item.to_dict()

    if item.stackable:
        item_dict["quantity"] = quantity

    return item_dict


def get_item_by_id(item_id: str) -> Item:
    """Retorna o Item do catálogo pelo ID."""
    if item_id not in ITEMS_CATALOG:
        raise ValueError(f"Item '{item_id}' não encontrado no catálogo!")
    return ITEMS_CATALOG[item_id]
