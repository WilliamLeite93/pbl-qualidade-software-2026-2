"""Testes funcionais automatizados do LocalEats com Playwright.

Os fluxos são executados na interface real do sistema:
https://local-eats-unisenac.vercel.app/
"""

import re
import uuid

import pytest
from playwright.sync_api import expect

BASE_URL = "https://local-eats-unisenac.vercel.app"
NOME_USUARIO = "Usuário Teste"
SENHA_PADRAO = "senha123"


def gerar_email_unico() -> str:
    """Gera um e-mail novo para permitir o cadastro a cada execução."""
    return f"qa.{uuid.uuid4().hex[:10]}@teste.com"


def abrir_tela_de_login(page) -> None:
    """Acessa o LocalEats e espera o redirecionamento para o login."""
    page.goto(BASE_URL)
    page.wait_for_url("**/login.html")


def esperar_restaurantes_filtrados(page, culinaria: str) -> None:
    """Espera o grid terminar de recarregar com apenas a culinária pedida.

    Evita espera fixa: aguarda o próprio DOM refletir o resultado do filtro.
    """
    page.wait_for_function(
        """(culinaria) => {
            const cards = [...document.querySelectorAll('.rest-card')];
            return cards.length > 0
                && cards.every((card) => card.innerText.includes(culinaria));
        }""",
        arg=culinaria,
    )


def test_cadastro_de_novo_usuario_abre_home_com_restaurantes(page):
    abrir_tela_de_login(page)

    page.get_by_role("button", name="Criar Conta").click()
    page.locator("#regName").fill(NOME_USUARIO)
    page.locator("#regEmail").fill(gerar_email_unico())
    page.locator("#regPassword").fill(SENHA_PADRAO)
    page.get_by_role("button", name="Registrar").click()

    page.wait_for_url("**/index.html")

    assert page.url.endswith("/index.html")

    expect(page.locator("#userBadge")).to_contain_text("Olá, Usuário")

    cards = page.locator(".rest-card")
    expect(cards.first).to_be_visible()
    assert cards.count() >= 5

    expect(page.locator("#restaurantGrid .loading")).to_have_count(0)


@pytest.fixture
def usuario_cadastrado(playwright):
    """Cria a conta pela API e devolve as credenciais para o login via interface."""
    email = gerar_email_unico()
    contexto = playwright.request.new_context(base_url=BASE_URL)

    resposta = contexto.post(
        "/users/register",
        data={"name": NOME_USUARIO, "email": email, "password": SENHA_PADRAO},
    )
    assert resposta.ok, f"Falha ao preparar usuário: {resposta.status}"

    contexto.dispose()
    return {"email": email, "senha": SENHA_PADRAO}


def test_filtro_por_categoria_japonesa_exibe_somente_restaurantes_japoneses(
    page, usuario_cadastrado
):
    abrir_tela_de_login(page)

    page.locator("#loginEmail").fill(usuario_cadastrado["email"])
    page.locator("#loginPassword").fill(usuario_cadastrado["senha"])
    page.locator("#loginForm").get_by_role("button", name="Entrar").click()

    page.wait_for_url("**/index.html")
    expect(page.locator("#userBadge")).to_contain_text("Olá, Usuário")

    # Espera a carga inicial do grid terminar antes de filtrar, para não
    # disputar com a requisição que renderiza a lista completa.
    expect(page.locator("#restaurantGrid .rest-card").first).to_be_visible()

    botao_japonesa = page.get_by_role("button", name="Japonesa", exact=True)
    botao_japonesa.click()
    esperar_restaurantes_filtrados(page, "Japonesa")

    cards = page.locator(".rest-card")
    assert cards.count() > 0

    for indice in range(cards.count()):
        assert "Japonesa" in cards.nth(indice).inner_text()

    expect(botao_japonesa).to_have_class(re.compile(r"\bactive\b"))
    expect(page.get_by_role("button", name="Todos", exact=True)).not_to_have_class(
        re.compile(r"\bactive\b")
    )
