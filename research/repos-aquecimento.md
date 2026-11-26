# Algum repositório do CloakHQ ou do browser-use ajuda o aquecimento?

Pesquisa do ticket [Algum repositório do CloakHQ ou do browser-use ajuda o aquecimento?](https://github.com/vinicius928e8r84/cloakbrowser-perfis/issues/21), feita em 2026-11-26 só lendo README, código e licença de cada repositório (nada instalado nem rodado). Cada link aponta para o commit lido.

"Ajudar" aqui é servir ao aquecimento já decidido no mapa: abrir o perfil, navegar com comportamento humano ligado sem mudar a opção salva, digitar uma busca no Google, clicar num resultado comum, aceitar o aviso de cookies, recusar permissões, pausar quando a pessoa mexe sem nada que um site veja, abrir a janela atrás. E sem trocar a versão do navegador, sem entrar no motor de fingerprint e sem depender de serviço pago novo.

## Resposta curta

- **Só um ajuda de verdade, e já está dentro do Manager: o CloakBrowser** (a biblioteca Python que o Manager usa para abrir perfis, versão 0.7.3). O comportamento humano dele (`humanize`) já faz mouse em curva, clique com mira, rolagem em etapas e digitação letra a letra com erro e correção, e ele lê a página num "mundo isolado" que os scripts do site não enxergam. É exatamente o que o aquecimento precisa para navegar, rolar, digitar a busca e clicar; não há nada novo para instalar.
- **O CloakBrowser-Agent serve só como exemplo de ideias**, não como peça: depende de dois serviços pagos de modelo de IA e prende o CloakBrowser abaixo da 0.7, o que trocaria a versão do navegador.
- **Os outros dez não ajudam**: são agentes de IA que pedem chave de modelo pago, cópias paradas de projetos de terceiros, uma lista de links, ou binários do motor de fingerprint (fora do escopo).

## Tabela

| Repositório | O que é | Licença | Último commit | Ajuda? |
|---|---|---|---|---|
| CloakHQ/CloakBrowser | Navegador furtivo + biblioteca Python/JS que o Manager usa | MIT (código); binário com licença própria | 2026-11-26 | **Sim, já é dependência** |
| CloakHQ/CloakBrowser-Agent | Agente que recebe um objetivo em texto e navega com o CloakBrowser | MIT | 2026-11-07 | Só ideias |
| CloakHQ/crawlee-python | Cópia (fork) do Crawlee, raspagem de sites | Apache-2.0 | 2026-03-13 | Não |
| CloakHQ/awesome-playwright | Cópia de uma lista de links sobre Playwright | CC0-1.0 | 2026-03-22 | Não |
| CloakHQ/crawl4ai | Cópia do Crawl4AI, raspagem de sites para IA | Apache-2.0 | 2026-02-20 | Não |
| CloakHQ/chromium-stealth-builds | Binários antigos do navegador (mudaram para o CloakBrowser) | todos os direitos reservados | 2026-02-25 | Não (motor de fingerprint) |
| browser-use/browser-harness | Deixa um agente de código usar o Chrome da pessoa por CDP | MIT | 2026-11-26 | Não (duas notas úteis) |
| browser-use/browser-use | Biblioteca de agente de IA para navegador + nuvem paga | MIT | 2026-11-24 | Não |
| browser-use/workflow-use | Grava e repete fluxos, com browser-use como reserva | AGPL-3.0 | 2026-10-23 | Não |
| browser-use/browser-use-pi | Agente de IA em TypeScript | MIT | 2026-11-20 | Não |
| browser-use/browser-harness-js | Ponte crua de CDP em JS, substituída pelo browser-use | MIT | 2026-11-11 | Não |
| browser-use/jev-ultrafast | Agente experimental com o modelo Jev, substituído pelo browser-use | MIT | 2026-11-11 | Não |

"Último commit" é a data do commit mais recente no ramo principal, lida na API do GitHub em 2026-11-26.

## Cada repositório

### CloakHQ/CloakBrowser — ajuda, e já está no Manager

- **O que é**: o navegador (Chromium com remendos de fingerprint) e a biblioteca que o abre. O Manager já depende dela: `cloakbrowser[geoip]>=0.7.3` em `backend/requirements.txt`, e abre cada perfil com `launch_persistent_context_async(...)`, passando `"humanize": bool(profile.get("humanize", False))` e `"human_preset"` (`backend/browser_manager.py`, linhas 439–469 na `main` deste repo). A versão lida é a 0.7.3 ([`_version.py`](https://github.com/CloakHQ/CloakBrowser/blob/09b1bf62a2fae23128772df4974a49ccac8abc5d/cloakbrowser/_version.py)), a mesma do piso do Manager.
- **Licença**: código MIT ([LICENSE](https://github.com/CloakHQ/CloakBrowser/blob/09b1bf62a2fae23128772df4974a49ccac8abc5d/LICENSE)); o binário do navegador tem licença própria, sem redistribuição ([BINARY-LICENSE.md](https://github.com/CloakHQ/CloakBrowser/blob/09b1bf62a2fae23128772df4974a49ccac8abc5d/BINARY-LICENSE.md)).
- **Vivo**: muito; último commit 2026-11-26.
- **Como ajuda o aquecimento**:
  - **Navegar, rolar, digitar e clicar como gente.** Com `humanize=True`, "All Playwright calls (`page.click()`, `page.fill()`, `page.type()`, `page.mouse.*`, `page.keyboard.*` …) are automatically replaced with human-like equivalents": mouse em curva de Bézier com leve passada do alvo, clique com ponto de mira e tempo de pressão, digitação por letra com pausas e "occasional typos with self-correction", rolagem "Accelerate → cruise → decelerate" ([README, Human Behavior](https://github.com/CloakHQ/CloakBrowser/blob/09b1bf62a2fae23128772df4974a49ccac8abc5d/README.md#L566-L601)). Digitar a busca no Google e clicar num resultado é `locator(...).fill(...)` e `locator(...).click()`; o README avisa para usar `locator`/`page.click` e não `query_selector`, que "bypass all patches" ([README](https://github.com/CloakHQ/CloakBrowser/blob/09b1bf62a2fae23128772df4974a49ccac8abc5d/README.md#L637)).
  - **Ritmo do perfil.** Há dois ritmos prontos, `default` e `careful` (mais lento, com micro-movimentos parados), e ajuste fino por `human_config` ([README](https://github.com/CloakHQ/CloakBrowser/blob/09b1bf62a2fae23128772df4974a49ccac8abc5d/README.md#L601-L631); parâmetros em [`human/config.py`](https://github.com/CloakHQ/CloakBrowser/blob/09b1bf62a2fae23128772df4974a49ccac8abc5d/cloakbrowser/human/config.py)). Bate com "no ritmo do perfil (normal se ele não tem)" de [O que é um perfil aquecido, e o que o aquecimento faz para chegar lá?](https://github.com/vinicius928e8r84/cloakbrowser-perfis/issues/8).
  - **Ligar o comportamento humano só no aquecimento, sem mudar a opção salva.** O caminho seguro é o aquecimento passar `humanize=True` na abertura (no `launch_options` daquela abertura, sem gravar no perfil). Existe também `patch_context_async(context, cfg)` para humanizar um contexto já aberto ([`human/__init__.py`](https://github.com/CloakHQ/CloakBrowser/blob/09b1bf62a2fae23128772df4974a49ccac8abc5d/cloakbrowser/human/__init__.py); [`human/patch.py` L489–503](https://github.com/CloakHQ/CloakBrowser/blob/09b1bf62a2fae23128772df4974a49ccac8abc5d/cloakbrowser/human/patch.py#L489-L503)), mas o próprio código aplica o humanize **antes** da proteção de licença "because the guard stores its wrapper on the page/context object, which shadows the class method humanize patches" ([`browser.py` L1032–1039](https://github.com/CloakHQ/CloakBrowser/blob/09b1bf62a2fae23128772df4974a49ccac8abc5d/cloakbrowser/browser.py#L1032-L1039)). Como o Manager abre com chave de licença, humanizar depois de abrir pode não pegar; por isso, ligar na abertura. Páginas sem humanize seguem o caminho normal do Playwright (o `wrapper` cai em `orig` quando a página não tem humanize; [`human/patch.py` L333–342](https://github.com/CloakHQ/CloakBrowser/blob/09b1bf62a2fae23128772df4974a49ccac8abc5d/cloakbrowser/human/patch.py#L333-L342)).
  - **Ler a página sem que o site veja.** O humanize localiza elementos "by Playwright's own selector engine running in a CDP isolated world per frame" ([`human/__init__.py`](https://github.com/CloakHQ/CloakBrowser/blob/09b1bf62a2fae23128772df4974a49ccac8abc5d/cloakbrowser/human/__init__.py#L6-L16)), e `page._stealth_world.evaluate("…")` roda qualquer leitura nesse mundo isolado ([README L635](https://github.com/CloakHQ/CloakBrowser/blob/09b1bf62a2fae23128772df4974a49ccac8abc5d/README.md#L635)). Serve para achar o botão "aceitar" do aviso de cookies, separar resultado comum de patrocinado e olhar a página sem escrever nada nela, como pede [O que acontece se alguém mexer na janela de um perfil enquanto ele aquece?](https://github.com/vinicius928e8r84/cloakbrowser-perfis/issues/18). Atenção: `_stealth_world` começa com sublinhado, é peça interna e pode mudar entre versões.
  - **Não cobre**: aviso de cookies, permissões, busca no Google e "pausar quando a pessoa mexe" não têm nada pronto; ficam com o Manager. O README sugere aquecer cookies com um perfil persistente e `--disable-http2` para sites que desafiam visitante novo ([README L1133–L1161](https://github.com/CloakHQ/CloakBrowser/blob/09b1bf62a2fae23128772df4974a49ccac8abc5d/README.md#L1133-L1161)); isso é um ajuste do navegador e foge do que o mapa decidiu, então fica só como nota.

### CloakHQ/CloakBrowser-Agent — só ideias

- **O que é**: agente que recebe um objetivo em texto e navega com o CloakBrowser; cada passo é decidido pelo modelo Jev, da TypeSafe ([README](https://github.com/CloakHQ/CloakBrowser-Agent/blob/e113844388a931031ea1f837fd4c75fa90433664/README.md)).
- **Licença**: MIT. **Vivo**: último commit 2026-11-07.
- **Por que não serve como peça**:
  - Pede "A TypeSafe API key (Jev)" e "A key for any OpenAI-compatible chat model" ([README, Requirements](https://github.com/CloakHQ/CloakBrowser-Agent/blob/e113844388a931031ea1f837fd4c75fa90433664/README.md#L73-L78)): dois serviços pagos de fora, e o aquecimento decidido sorteia sites e buscas de listas, sem modelo de IA.
  - Prende `cloakbrowser[geoip]>=0.6.3,<0.7`, "Capped at the minor: uses cloakbrowser humanize internals" ([pyproject.toml L10–L11](https://github.com/CloakHQ/CloakBrowser-Agent/blob/e113844388a931031ea1f837fd4c75fa90433664/pyproject.toml#L10-L11)). O Manager está em `>=0.7.3`; usar o agente obrigaria a trocar a versão, o que a regra do dono proíbe.
- **Ideias que valem copiar como ideia (não como código)**:
  - **Só ler pelo mundo isolado**: "Nothing is injected into the page" e, quando a página não tem humanize, "still read the DOM only from an isolated world, never the main world" ([README](https://github.com/CloakHQ/CloakBrowser-Agent/blob/e113844388a931031ea1f837fd4c75fa90433664/README.md#L68); [`browser.py` L110–L115](https://github.com/CloakHQ/CloakBrowser-Agent/blob/e113844388a931031ea1f837fd4c75fa90433664/cloak_agent/browser.py#L110-L115)).
  - **Só oferecer o que a pessoa alcança**: "Hidden, disabled, and covered elements (for example, behind a modal) aren't in the table" ([README](https://github.com/CloakHQ/CloakBrowser-Agent/blob/e113844388a931031ea1f837fd4c75fa90433664/README.md#L69)). Ajuda a não clicar em algo escondido atrás do aviso de cookies.
  - **Parar laços**: "The same action on the same page a 3rd time ends the task as `blocked`, as do three actions in a row that change nothing" ([README](https://github.com/CloakHQ/CloakBrowser-Agent/blob/e113844388a931031ea1f837fd4c75fa90433664/README.md#L71)).
  - **Rolagem humana direta**: usa o motor do humanize (`ensure_cursor` e `_wheel_burst`) para rolar ([`browser.py` L185–L190](https://github.com/CloakHQ/CloakBrowser-Agent/blob/e113844388a931031ea1f837fd4c75fa90433664/cloak_agent/browser.py#L185-L190)); são peças internas da 0.6, não garantidas na 0.7.3.
  - **Diferença com o mapa**: diante de aviso de cookies, o agente escolhe "reject/decline or close button (accept only if there is none)" ([`questions.py` L22–L31](https://github.com/CloakHQ/CloakBrowser-Agent/blob/e113844388a931031ea1f837fd4c75fa90433664/cloak_agent/questions.py#L22-L31)). O mapa decidiu o contrário para o aquecimento (clicar em "aceitar"), o que faz sentido porque o objetivo é juntar cookies; nada muda.

### CloakHQ/crawlee-python, CloakHQ/crawl4ai, CloakHQ/awesome-playwright — cópias paradas

- São forks (cópias) de projetos de terceiros (apify/crawlee-python, unclecode/crawl4ai, mxschmitt/awesome-playwright). Pela comparação do GitHub, os três têm **0 commits próprios** e estão atrás do original (625, 705 e 27 commits). Não há nada do CloakHQ neles.
- **Licenças**: Apache-2.0, Apache-2.0 e CC0-1.0. **Últimos commits**: 2026-03-13, 2026-02-20 e 2026-03-22.
- **crawlee-python e crawl4ai** são ferramentas de raspagem (baixar conteúdo de muitos sites); o aquecimento não raspa nada. O único trecho perto do aquecimento é o `remove_overlay_elements` do crawl4ai, que lida com avisos de cookies **apagando-os da página** com JavaScript rodado nela (`elem.remove()`, em [`js_snippet/remove_overlay_elements.js`](https://github.com/CloakHQ/crawl4ai/blob/aa7b05072d5b6deb9d1b85f9bb8b8561b936ac5e/crawl4ai/js_snippet/remove_overlay_elements.js)). É o oposto do decidido: não aceita (o cookie de consentimento não fica salvo) e escreve na página, que um site pode perceber.
- **awesome-playwright** é uma lista de 77 links ([README](https://github.com/CloakHQ/awesome-playwright/blob/965bac69341216e9e4d1d01094415a71f6040e28/README.md)); nenhum sobre comportamento humano, avisos de cookies ou furtividade.

### CloakHQ/chromium-stealth-builds — fora do escopo

- Binários antigos do navegador; o README diz "This repository has moved. Binary releases are now published at CloakHQ/cloakbrowser" ([README](https://github.com/CloakHQ/chromium-stealth-builds/blob/e756c28f5c207ce5cd2a0b0d2eadb922c838ec72/README.md)). O GitHub não o marca como arquivado, mas o último commit é 2026-02-25.
- **Licença**: "All Rights Reserved … Redistribution, modification, or commercial use without written consent is prohibited" ([LICENSE](https://github.com/CloakHQ/chromium-stealth-builds/blob/e756c28f5c207ce5cd2a0b0d2eadb922c838ec72/LICENSE)).
- É o motor de fingerprint (fora do escopo) e trocaria a versão do navegador. Não ajuda.

### browser-use/browser-harness — não, mas tem duas notas úteis

- **O que é**: deixa um agente de código (Claude Code, Codex, Cursor) usar o Chrome da pessoa pelo protocolo de depuração do Chrome (CDP); hoje é "the engine inside Browser Use" ([README](https://github.com/browser-use/browser-harness/blob/54f4921b39aa839af55f49bbbd2a823526a80613/README.md)). **Licença**: MIT. **Vivo**: último commit 2026-11-26.
- **Por que não**: é feito para um agente de IA escrever comandos; fala CDP cru com o Chrome, e o CloakBrowser avisa que o comportamento humano "is a wrapper-level feature" e não vale para quem conecta por CDP de fora ([README do CloakBrowser L826](https://github.com/CloakHQ/CloakBrowser/blob/09b1bf62a2fae23128772df4974a49ccac8abc5d/README.md#L826)). O Manager já tem o próprio contexto aberto e não precisa de ponte.
- **Notas úteis para a implementação** (não são decisões):
  - **Caixas `alert`/`confirm` da página**: fechar pelo CDP (`Page.handleJavaScriptDialog`) "Works even when JS is frozen" e é "Undetectable by antibot — no JS injected into the page"; trocar `window.alert` por JavaScript é "Detectable by antibot" ([interaction-skills/dialogs.md](https://github.com/browser-use/browser-harness/blob/54f4921b39aa839af55f49bbbd2a823526a80613/interaction-skills/dialogs.md)). No Playwright do Manager, o equivalente é tratar o evento `dialog` da página.
  - **Janela atrás**: "Static screenshots and normal CDP input work on the attached background tab"; quando a rolagem trava numa aba que não está visível, eles ligam por um instante `Emulation.setFocusEmulationEnabled` em vez de trazer o Chrome para a frente ([tabs.md](https://github.com/browser-use/browser-harness/blob/54f4921b39aa839af55f49bbbd2a823526a80613/interaction-skills/tabs.md); [scrolling.md](https://github.com/browser-use/browser-harness/blob/54f4921b39aa839af55f49bbbd2a823526a80613/interaction-skills/scrolling.md)). Serve de pista para "a janela abre atrás se o Mac deixar"; a nota fala de Chrome no Windows, então precisa ser provado num Mac, e emular foco muda o que a página acha do foco.

### browser-use/browser-use — não

- **O que é**: "The open-source browser agent": um modelo de IA escreve Python que roda num navegador, local ou na nuvem paga deles ([README](https://github.com/browser-use/browser-use/blob/94784c1f7ecb6b0a5f565b7f9fba59e395b7e048/README.md)). **Licença**: MIT. **Vivo**: último commit 2026-11-24 (versão 1.0.8).
- **Por que não**: cada passo depende de um modelo de IA (chave paga); fala CDP cru, sem o comportamento humano do CloakBrowser (ver acima); o próprio exemplo de integração do CloakBrowser roda o browser-use com `ChatOpenAI` ([examples/integrations/browser_use_example.py](https://github.com/CloakHQ/CloakBrowser/blob/09b1bf62a2fae23128772df4974a49ccac8abc5d/examples/integrations/browser_use_example.py)). Envia estatísticas de uso por padrão (`ANONYMIZED_TELEMETRY` vale `true` se não for desligado; [config.py L50](https://github.com/browser-use/browser-use/blob/94784c1f7ecb6b0a5f565b7f9fba59e395b7e048/browser_use/config.py#L50)), e o README pede que cada integração mande um relato a eles. O aquecimento decidido é sorteio de listas, não precisa de IA.

### browser-use/workflow-use — não

- **O que é**: grava um fluxo (ou gera com o browser-use) e o repete, caindo no browser-use quando um passo falha; "in very early development so we don't recommend using this in production" ([README](https://github.com/browser-use/workflow-use/blob/f00e27edd7f17600463ce37effa951f42ccb91c8/README.md)).
- **Licença**: **AGPL-3.0** ([LICENSE](https://github.com/browser-use/workflow-use/blob/f00e27edd7f17600463ce37effa951f42ccb91c8/LICENSE)): copiar código dele para o Manager (MIT) obrigaria abrir o Manager inteiro sob AGPL. **Vivo**: último commit 2026-10-23.
- Depende de `browser-use>=0.13.8,<0.14` ([workflows/pyproject.toml](https://github.com/browser-use/workflow-use/blob/f00e27edd7f17600463ce37effa951f42ccb91c8/workflows/pyproject.toml)) e de modelos de IA para gerar os fluxos. Não ajuda.

### browser-use/browser-use-pi — não

- **O que é**: o browser-use em TypeScript: "The agent writes JavaScript, controls Chrome" por CDP cru; o exemplo usa chave de modelo e `Browser.cloud({ apiKey })` ([README](https://github.com/browser-use/browser-use-pi/blob/3583b8a10a2cf393956ad75c32fec302b227aa32/README.md)). **Licença**: MIT. **Vivo**: último commit 2026-11-20 (versão 0.2.0).
- Mesmo motivo do browser-use: agente de IA, outra linguagem (o Manager é Python), sem o comportamento humano do CloakBrowser.

### browser-use/browser-harness-js — não

- **O que é**: ponte crua de CDP em JS ("No harness, no recipes, no rails"); o README avisa "This repo is no longer the recommended path. Use Browser Use" ([README](https://github.com/browser-use/browser-harness-js/blob/c92722eaa365d195ed1021baa3ec028161fa0373/README.md)). **Licença**: MIT. **Último commit**: 2026-11-11 (só o aviso de mudança).

### browser-use/jev-ultrafast — não

- **O que é**: o experimento original do agente com o modelo Jev, "now ultrafast mode in Browser Use" ([README](https://github.com/browser-use/jev-ultrafast/blob/cf3c406f0fc4becff8986ed4d4d37b7b9f102e45/README.md)); pede `TYPESAFE_API_KEY` e `TEXT_MODEL_API_KEY`. **Licença**: MIT. **Último commit**: 2026-11-11 (só o aviso). É o antecessor do CloakBrowser-Agent; nada a mais para o aquecimento.

## De passagem: fatos do CloakBrowser para outras partes do mapa

Lidos no mesmo README; não respondem a este ticket, mas tocam a névoa do mapa.

- **Mesmas versões nos dois Macs.** `CLOAKBROWSER_AUTO_UPDATE=false` "keep the cached build and skip update checks" ([README L650](https://github.com/CloakHQ/CloakBrowser/blob/09b1bf62a2fae23128772df4974a49ccac8abc5d/README.md#L650)); no código, com o envio congelado e um build no cache, ele usa o do cache sem perguntar ao servidor, e sem build no cache ainda baixa um ([`download.py` L483–L490](https://github.com/CloakHQ/CloakBrowser/blob/09b1bf62a2fae23128772df4974a49ccac8abc5d/cloakbrowser/download.py#L483-L490)). A mesma variável desliga o aviso de versão nova da biblioteca ([`download.py` L1064–L1071](https://github.com/CloakHQ/CloakBrowser/blob/09b1bf62a2fae23128772df4974a49ccac8abc5d/cloakbrowser/download.py#L1064-L1071)). Fixar uma versão exata (`CLOAKBROWSER_VERSION`) é "Paid Pro key only. A free key cannot pin: it ignores the pin and always gets the latest build", e "unpinned launches always use the latest available version" ([README L1209–L1225](https://github.com/CloakHQ/CloakBrowser/blob/09b1bf62a2fae23128772df4974a49ccac8abc5d/README.md#L1209-L1225)). O Manager não define nenhuma das duas variáveis hoje.
- **Licença em dois Macs.** A chave grátis dá "one concurrent session"; o Pro sobe para "5, 20, 200, 2,000, or more concurrent sessions" ([README L191–L192](https://github.com/CloakHQ/CloakBrowser/blob/09b1bf62a2fae23128772df4974a49ccac8abc5d/README.md#L191-L192)).
