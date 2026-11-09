# Atividade 4: Testes Automatizados do LocalEats

## 1. Identificação

| Item | Informação |
| --- | --- |
| Unidade Curricular | Qualidade de Software |
| Projeto | LocalEats |
| Modalidade | Individual |
| Integrante | Integrante único |
| Sistema testado | <https://local-eats-unisenac.vercel.app/> |
| Data da execução | 09/11/2026 |
| Ferramenta de execução | pytest 8.3.4 + pytest-playwright 0.10.0 + Playwright 1.64.1 (Chromium) |

## 2. Contexto e objetivo

O LocalEats é uma aplicação web de delivery de restaurantes locais. Esta atividade aplica, sobre o domínio do sistema, testes unitários com TDD e testes funcionais automatizados com Playwright, todos executados por meio do pytest.

Antes de automatizar, o sistema foi explorado manualmente. A aplicação é servida a partir de `/static/`; ao abrir a URL raiz, o redirecionamento para `login.html` é feito pelo JavaScript de autenticação (`auth.js`). Portanto, os fluxos funcionais precisam de uma conta autenticada. A página inicial só é exibida depois do cadastro ou do login, e os dados dos restaurantes são carregados por JavaScript a partir da API.

## 3. Estrutura entregue

```text
atividade-04/
├── atividade-04-testes-automatizados.md
├── relatorio-pytest.txt
├── requirements.txt
├── src/
│   ├── __init__.py
│   └── regras_localeats.py
├── tests/
│   ├── __init__.py
│   ├── test_regras_localeats.py
│   └── test_localeats.py
└── evidencias/
    ├── tests-test-localeats-py-test-cadastro-de-novo-usuario-abre-home-com-restaurantes-chromium/
    │   └── test-finished-1.png
    └── tests-test-localeats-py-test-filtro-por-categoria-japonesa-exibe-somente-restaurantes-japoneses-chromium/
        └── test-finished-1.png
```

Para reproduzir e atualizar o relatório:

```powershell
python -m pip install -r requirements.txt
python -m playwright install chromium
python -m pytest -v | Tee-Object -FilePath relatorio-pytest.txt
```

Para gerar novamente as capturas de tela usadas como evidência (opcional):

```powershell
python -m pytest -v --screenshot=on --output=evidencias
```

## 4. Parte 1: Testes unitários e TDD

### 4.1 Regra escolhida: Regra 1 — valor mínimo do pedido

Implementação em `src/regras_localeats.py`:

```python
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
```

Comportamento implementado:

- pedidos de R$ 30,00 ou mais retornam `True`;
- pedidos abaixo de R$ 30,00 retornam `False`;
- valores negativos geram `ValueError`.

### 4.2 TDD

**Regra escolhida:** valor mínimo do pedido (`pedido_atingiu_valor_minimo`).

**Primeiro teste escrito:**

```python
def test_pedido_acima_do_valor_minimo_retorna_true():
    resultado = pedido_atingiu_valor_minimo(50)

    assert resultado is True
```

**Por que o teste falhou inicialmente:** a função ainda não existia no módulo. O pytest interrompeu a coleta com:

```text
ImportError: cannot import name 'pedido_atingiu_valor_minimo' from 'src.regras_localeats'
=================== 1 error in 0.38s ===================
```

**Implementação mínima realizada:** para fazer apenas o primeiro teste passar, a função foi criada retornando sempre `True` (passo "fake it" do TDD), sem nenhuma regra de negócio:

```python
def pedido_atingiu_valor_minimo(valor_pedido):
    return True
```

Resultado: `1 passed`.

**Segundo teste escrito:**

```python
def test_pedido_abaixo_do_valor_minimo_retorna_false():
    resultado = pedido_atingiu_valor_minimo(20)

    assert resultado is False
```

O teste falhou, porque a implementação provisória respondia `True` para qualquer valor:

```text
>       assert resultado is False
E       assert True is False
FAILED tests/test_regras_localeats.py::test_pedido_abaixo_do_valor_minimo_retorna_false
=================== 1 failed, 1 passed in 0.27s ====================
```

**Melhoria ou refatoração realizada:** a função passou a comparar o valor recebido com o mínimo e a rejeitar valores negativos com `ValueError`. Também foi extraída a constante `VALOR_MINIMO_PEDIDO`, adicionada a anotação de tipo e escrita a docstring. Depois disso, os dois testes passaram (`2 passed`).

**Testes adicionais (diferenciais):** foram incluídos um teste de exceção com `pytest.raises` e um teste parametrizado da fronteira (R$ 29,99 / R$ 30,00 / R$ 30,01), registrados como TU03 e TU04 na tabela. O teste de exceção passou já na primeira execução, porque a validação de valores negativos havia sido incluída na etapa anterior.

## 5. Parte 2: Testes funcionais com Playwright

### 5.1 TF01 — Cadastro de novo usuário

Fluxo: acessar o LocalEats → ser redirecionado para a tela de login → clicar em **Criar Conta** → preencher nome, e-mail e senha → clicar em **Registrar** → conferir a página inicial.

Interações e locators usados:

| Elemento | Locator |
| --- | --- |
| Botão que abre o cadastro | `page.get_by_role("button", name="Criar Conta")` |
| Campo nome | `page.locator("#regName")` |
| Campo e-mail | `page.locator("#regEmail")` |
| Campo senha | `page.locator("#regPassword")` |
| Botão de envio | `page.get_by_role("button", name="Registrar")` |
| Identificação do usuário | `page.locator("#userBadge")` |
| Cards de restaurante | `page.locator(".rest-card")` |
| Placeholder de carregamento | `page.locator("#restaurantGrid .loading")` |

Assertions (5):

1. a URL final termina em `/index.html`;
2. o cabeçalho exibe `Olá, Usuário` após o cadastro;
3. o primeiro card de restaurante fica visível (verificação usada também como espera da renderização);
4. o grid apresenta pelo menos 5 restaurantes;
5. o aviso de carregamento não está mais no DOM.

Cada execução usa um e-mail único gerado com `uuid4`, então o teste pode rodar repetidamente sem conflito de cadastro.

### 5.2 TF02 — Filtro por categoria Japonesa (diferencial)

Fluxo: criar a conta pela API (preparação), entrar pela interface com e-mail e senha e clicar no filtro **Japonesa**.

Assertions (6):

1. o cabeçalho exibe `Olá, Usuário` após o login;
2. o primeiro card da carga inicial fica visível antes do filtro (verificação usada também como espera);
3. o grid continua com pelo menos um restaurante;
4. todos os cards exibidos contêm a culinária `Japonesa`;
5. o botão **Japonesa** recebe a classe `active`;
6. o botão **Todos** deixa de ter a classe `active`.

Nenhum teste usa `time.sleep` nem espera fixa. As esperas são baseadas em condições reais: `page.wait_for_url` para as navegações, `page.wait_for_function` para o recarregamento do grid e assertions auto-retentativas do Playwright (`expect`) para os demais estados do DOM.

### 5.3 Cenário BDD (diferencial)

```gherkin
# language: pt
Funcionalidade: Filtro por culinária no LocalEats

  Cenário: Exibir somente restaurantes japoneses
    Dado que estou autenticado no LocalEats
    Quando clico no filtro "Japonesa"
    Então o grid exibe apenas restaurantes com culinária "Japonesa"
    E o filtro "Japonesa" fica destacado como ativo
```

### 5.4 Falha encontrada e corrigida (diferencial)

Na primeira execução do TF02, o teste falhou com `Page.wait_for_function: Timeout 30000ms exceeded`. O clique no filtro acontecia enquanto a requisição de carga inicial ainda estava em andamento; a resposta da lista completa chegava depois e sobrescrevia o resultado filtrado. A correção foi esperar o grid inicial terminar de renderizar com `expect(page.locator("#restaurantGrid .rest-card").first).to_be_visible()` antes de clicar no filtro. Depois do ajuste, o teste passou de forma estável.

## 6. Identificação das responsabilidades

| ID | Integrante | Tipo | Comportamento verificado | Arquivo e função |
| --- | --- | --- | --- | --- |
| TU01 | Integrante único | Unitário | Pedido de R$ 50,00 atinge o valor mínimo | `tests/test_regras_localeats.py::test_pedido_acima_do_valor_minimo_retorna_true` |
| TU02 | Integrante único | Unitário | Pedido de R$ 20,00 não atinge o valor mínimo | `tests/test_regras_localeats.py::test_pedido_abaixo_do_valor_minimo_retorna_false` |
| TU03 | Integrante único | Unitário | Valor negativo gera `ValueError` | `tests/test_regras_localeats.py::test_pedido_com_valor_negativo_gera_value_error` |
| TU04 | Integrante único | Unitário | Fronteira de R$ 29,99, R$ 30,00 e R$ 30,01 | `tests/test_regras_localeats.py::test_fronteira_do_valor_minimo` |
| TF01 | Integrante único | Funcional | Cadastro de usuário e exibição da página inicial | `tests/test_localeats.py::test_cadastro_de_novo_usuario_abre_home_com_restaurantes[chromium]` |
| TF02 | Integrante único | Funcional | Filtro de restaurantes por culinária japonesa | `tests/test_localeats.py::test_filtro_por_categoria_japonesa_exibe_somente_restaurantes_japoneses[chromium]` |

## 7. Relatório da execução

Comando executado no diretório `atividades/atividade-04`:

```powershell
python -m pytest -v | Tee-Object -FilePath relatorio-pytest.txt
```

Resumo final registrado em `relatorio-pytest.txt`:

```text
collecting ... collected 8 items
tests/test_localeats.py::test_cadastro_de_novo_usuario_abre_home_com_restaurantes[chromium] PASSED [ 12%]
tests/test_localeats.py::test_filtro_por_categoria_japonesa_exibe_somente_restaurantes_japoneses[chromium] PASSED [ 25%]
tests/test_regras_localeats.py::test_pedido_acima_do_valor_minimo_retorna_true PASSED [ 37%]
tests/test_regras_localeats.py::test_pedido_abaixo_do_valor_minimo_retorna_false PASSED [ 50%]
tests/test_regras_localeats.py::test_pedido_com_valor_negativo_gera_value_error PASSED [ 62%]
tests/test_regras_localeats.py::test_fronteira_do_valor_minimo[29.99-False] PASSED [ 75%]
tests/test_regras_localeats.py::test_fronteira_do_valor_minimo[30-True] PASSED [ 87%]
tests/test_regras_localeats.py::test_fronteira_do_valor_minimo[30.01-True] PASSED [100%]
======================== 8 passed, 1 warning in 6.57s ========================
```

Todos os testes citados na tabela aparecem no relatório, sem aprovações pendentes. O relatório registra 1 warning interno do plugin `pytest-asyncio` (`asyncio.get_event_loop_policy`), sem relação com o código da atividade. Na execução local também aparece um aviso de configuração do mesmo plugin no stderr (`asyncio_default_fixture_loop_scope` não definido), que não entra no resumo do relatório e não afeta o resultado dos testes.

## 8. Explicação individual de um teste

**Teste explicado: TU02 — `test_pedido_abaixo_do_valor_minimo_retorna_false`**

O teste passa o valor 20 para `pedido_atingiu_valor_minimo` e afirma que o retorno é exatamente `False` (`assert resultado is False`). Ele cobre o comportamento alternativo da regra: um pedido abaixo de R$ 30,00 não pode ser tratado como válido. O valor foi escolhido por ser claramente inferior ao mínimo, o que separa o comportamento da borda testada em TU04.

A falha desse teste foi o ponto central do ciclo de TDD: como a implementação inicial retornava `True` para qualquer entrada, o teste expôs que a comparação com o valor mínimo ainda não existia. A correção (`valor_pedido >= VALOR_MINIMO_PEDIDO`) fez o teste passar e manteve o TU01 aprovado, mostrando que os dois comportamentos são compatíveis.

## 9. Diferenciais implementados

- terceiro teste unitário e teste de fronteira com `pytest.mark.parametrize`;
- uso de `pytest.raises` para verificar exceção;
- cenário BDD em Gherkin documentado;
- segundo teste funcional (TF02);
- screenshots da execução salvos em `evidencias/`, gerados com `python -m pytest -v --screenshot=on --output=evidencias`;
- registro da falha encontrada e corrigida no TF02.

## 10. Uso de inteligência artificial

**Ferramenta utilizada:** OpenCode (agente local com modelo Big Pickle).

**Como a ferramenta foi utilizada:** a ferramenta foi usada como apoio, não como substituta da autoria. Ela auxiliou na exploração inicial da interface do LocalEats, na geração de uma primeira versão dos arquivos de teste e na execução dos comandos do pytest. A partir dessa primeira versão, o integrante revisou o código, conferiu os locators e textos na interface real, ajustou o que não correspondia ao sistema e validou o comportamento com execuções sucessivas do pytest.

**Uma sugestão que precisou ser alterada ou rejeitada:** a primeira versão do teste funcional localizava os campos de formulário por rótulo (`page.get_by_label("Nome Completo")`). O LocalEats não associa os elementos `<label>` aos `<input>`, e o Playwright ficou aguardando o locator até estourar o tempo limite. A sugestão foi rejeitada e os campos passaram a ser localizados pelos `id` reais da página (`#regName`, `#regEmail`, `#regPassword`).

**Como o código sugerido foi verificado:** cada etapa foi revisada e executada com `python -m pytest -v`. O ciclo de TDD teve as falhas observadas e registradas na seção 4.2, e a suíte final foi executada até o resultado `8 passed`, cuja saída está em `relatorio-pytest.txt`. Além da execução automatizada, o fluxo foi validado manualmente na interface real: login, conferência do texto do badge, contagem de restaurantes na página inicial e aplicação do filtro "Japonesa". Os textos e elementos usados nas assertions foram conferidos na interface antes de entrar no código.
