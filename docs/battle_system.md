# Sistema de Batalha e Balanceamento

## 1. Atributos Base e Derivados

### Atributos Primários (1-100+)
- **Força (STR):** Aumenta Dano Físico e Vida.
- **Destreza (DEX):** Aumenta Crítico, Esquiva e Precisão.
- **Inteligência (INT):** Aumenta Dano Mágico e Mana.
- **Vitalidade (VIT):** Aumenta Vida e Defesa Física.
- **Mana (MNA):** Aumenta Mana e Defesa Mágica.
- **Stamina (STM):** Aumenta Stamina (ações).

### Fórmulas de Derivação (Proposta Conservadora)
- **Vida Máxima:** `(VIT * 10) + (STR * 2) + 50`
- **Mana Máxima:** `(INT * 8) + (MNA * 4) + 20`
- **Dano Físico Base:** `(STR * 1.5) + (DEX * 0.5)`
- **Defesa Física:** `(VIT * 0.5) + (STR * 0.2)`

## 2. Cálculo de Dano

### Fórmula de Dano Físico
```python
Dano = (Dano_Atacante * Multiplicador_Skill) - (Defesa_Alvo * Fator_Mitigacao)
```

**Onde:**
- `Dano_Atacante`: Valor entre `dano_min` e `dano_max`.
- `Fator_Mitigacao`: Constante para evitar que defesa anule dano cedo demais (ex: 0.3 ou 0.5).

### Exemplo de Balanceamento Inicial (Nível 1)

**Herói (Bárbaro Lvl 1)**
- STR: 8, VIT: 7
- Dano Base: ~12-16 (com arma inicial)
- Defesa: ~4

**Inimigo (Rato Lvl 1)**
- Vida: 30
- Dano: 4-6
- Defesa: 1

**Simulação:**
- Herói ataca Rato:
  - Dano: 14 - (1 * 0.5) = 13.5 -> 13 de dano.
  - Hits para matar: 30 / 13 = ~3 hits. (Bom ritmo)

- Rato ataca Herói:
  - Dano: 5 - (4 * 0.5) = 3 de dano.
  - Vida Herói: ~130.
  - Hits para matar: 130 / 3 = ~43 hits. (Fácil, mas ok para lvl 1)

## 3. Progressão de XP
Fórmula de XP para próximo nível:
`XP_Next = Base_XP * (Level ^ Exponent)`
- Base_XP: 100
- Exponent: 1.5

Lvl 1 -> 2: 100 XP
Lvl 2 -> 3: 282 XP
...

## 4. Equipamento Inicial
Todo herói deve começar com:
- 1 Arma Básica (Dano +2 a +4)
- 1 Armadura Básica (Defesa +1 a +2)
