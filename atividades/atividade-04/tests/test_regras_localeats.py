"""Testes unitários das regras de negócio do LocalEats."""

import pytest

from src.regras_localeats import pedido_atingiu_valor_minimo


def test_pedido_acima_do_valor_minimo_retorna_true():
    resultado = pedido_atingiu_valor_minimo(50)

    assert resultado is True


def test_pedido_abaixo_do_valor_minimo_retorna_false():
    resultado = pedido_atingiu_valor_minimo(20)

    assert resultado is False


def test_pedido_com_valor_negativo_gera_value_error():
    with pytest.raises(ValueError):
        pedido_atingiu_valor_minimo(-1)


@pytest.mark.parametrize(
    ("valor_pedido", "esperado"),
    [(29.99, False), (30, True), (30.01, True)],
)
def test_fronteira_do_valor_minimo(valor_pedido, esperado):
    assert pedido_atingiu_valor_minimo(valor_pedido) is esperado
