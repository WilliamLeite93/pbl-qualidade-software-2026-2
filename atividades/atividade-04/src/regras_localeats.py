"""Regras de negócio do LocalEats.

Regra 1: valor mínimo do pedido.
"""

VALOR_MINIMO_PEDIDO = 30.0


def pedido_atingiu_valor_minimo(valor_pedido: float) -> bool:
    """Indica se o pedido atingiu o valor mínimo aceito pelo LocalEats.

    Pedidos de R$ 30,00 ou mais retornam True; pedidos abaixo disso retornam
    False. Valores negativos são inválidos e geram ValueError.
    """
    if valor_pedido < 0:
        raise ValueError("O valor do pedido não pode ser negativo.")

    return valor_pedido >= VALOR_MINIMO_PEDIDO
