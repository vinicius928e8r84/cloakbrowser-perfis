# O que forma um perfil, e o que precisa viajar entre os Macs

Pesquisa do ticket "O que forma um perfil no disco e no banco, e o que precisa viajar?" (#5), parte do mapa #3. Feita em 2026-11-25 lendo o código do fork (v0.2.2, commit `a5327f0`). Caminhos de arquivo são deste repo.

## Resposta curta

Um perfil são **três coisas** em lugares diferentes da pasta de dados do Manager (`~/Library/Application Support/CloakBrowser Manager` no Mac):

| Parte | Onde | Viaja? |
|---|---|---|
| Pasta do navegador | `profiles/<id>/` | Sim, menos o descartável (abaixo) |
| Linha no banco | `profiles.db`, tabelas `profiles` e `profile_tags` | Sim, menos o caminho da pasta |
| Arquivos anexados e downloads | `artifacts/<id>/` e linhas na tabela `artifacts` | A decidir |

Configurações gerais (`settings.json`, com a licença) e a janela (`window.json`) são da máquina e não viajam.

## 1. A pasta do navegador (`profiles/<id>/`)

- O caminho sai de `user_data_dir_for()` (`backend/database.py`): `DATA_DIR / "profiles" / <id>`.
- Dentro, `Default/` guarda o que o pedido quer manter. A lista que o próprio Manager apaga no "Reset" (`_RESET_STATE_FILES` e `_RESET_STATE_DIRS` em `backend/main.py`) é um bom mapa:
  - **cookies**: `Cookies`;
  - **histórico**: `History`, `Visited Links`, `Top Sites`, `Shortcuts`, `Favicons`;
  - **senhas**: `Login Data`;
  - **dados dos sites**: `Local Storage`, `Session Storage`, `IndexedDB`, `Service Worker`, `File System`;
  - **estado das extensões**: `Extension Rules`, `Extension Scripts`, `Extension State`.
- **Abas abertas**: o Chromium as grava em `Default/Sessions/`, e o Manager só as reabre porque passa `--restore-last-session` quando o perfil tem "restaurar sessão" ligado (`launch()` em `backend/browser_manager.py`). Então essa pasta precisa viajar e a opção precisa estar ligada.
- **Favoritos iniciais**: `_init_profile_defaults()` cria `Default/Bookmarks` na primeira abertura.
- **Descartável** (o Manager já o pula ao duplicar um perfil com estado, `_DUPLICATE_SKIP_FILES` em `backend/main.py`): `SingletonLock`, `SingletonCookie`, `SingletonSocket` (trava do Chromium; copiada, faz o outro Mac achar que o perfil já está aberto) e `last_screenshot.jpg` (prévia). Também descartáveis por natureza: `Cache`, `Code Cache`, `GPUCache` (o Chromium os refaz).
- **Tamanho** (duas pastas reais no PC Windows): 88 MB, dos quais cerca de 77 MB são `Cache`, `Code Cache` e `Service Worker`; e 8,5 MB num perfil pouco usado. Sem cache, um perfil usado fica na casa de dezenas de MB, e cresce com o uso.
- **Cifra**: cookies e senhas dependem da chave do Keychain do Mac; ver a pesquisa "Senhas e cookies continuam legíveis num perfil levado para outro Mac?" (#4).

## 2. A linha no banco (`profiles.db`)

- Esquema em `_PROFILE_SCHEMA` (`backend/database.py`). O que define a identidade e precisa ser igual nos dois Macs: `fingerprint_seed`, `proxy`, `timezone`, `locale`, `screen_width`, `screen_height`, `gpu_family`, `humanize`, `human_preset`, `geoip`, `color_scheme`, `launch_args`, `allow_3p_cookies`, `transparent_proxy`, `portable_cookies`, `search_engine`, `restore_session`. Mais o que o usuário vê: `name`, `notes`, `sort_order` e as etiquetas (`profile_tags`).
- **`user_data_dir` é um caminho absoluto** gravado na linha (`create_profile`). Ele contém a pasta pessoal do usuário (`/Users/<nome>/...`), que difere entre os dois Macs. Não pode viajar como está: no outro Mac precisa ser recalculado pelo `id`.
- **`extension_paths`** são caminhos absolutos de pastas de extensão desempacotadas na máquina, passados ao navegador a cada abertura (`launch()`, chave `extension_paths`). A pasta da extensão não fica dentro do perfil: no outro Mac o caminho não existe e a extensão some. Só o estado dela (`Extension State` e afins) mora no perfil. Levar extensões junto pede decidir onde a pasta da extensão mora (dentro do perfil, ou num lugar comum com o mesmo caminho relativo nos dois Macs).
- O sistema do perfil (Mac ou Windows) **não** está na linha: vem da máquina a cada abertura (`_build_fingerprint_args`, `platform = "macos" if host_os == "macos"`). Ver o ticket "Como o perfil fica preso ao macOS?" (#6).
- `auto_launch` abre o perfil sozinho quando o Manager inicia (`auto_launch_all`). Com trava, isso precisa passar pelo empréstimo, ou ser desligado para perfis compartilhados.

## 3. Arquivos anexados e downloads

- Moram fora da pasta do navegador, em `DATA_DIR/artifacts/<id>/` (`artifacts_root()` em `backend/artifacts.py`), com metadados na tabela `artifacts`. Downloads do navegador caem lá também (`backend/downloads.py`, `staging_dir`).
- O pedido não fala deles. Fica para o ticket "Como abrir, fechar e forçar liberação funcionam no empréstimo?" (#10) decidir se viajam.

## 4. Onde abrir e fechar acontecem (pontos de engate)

- **Abrir**: `POST /api/profiles/{id}/launch` (`backend/main.py`) chama `BrowserManager.launch()`. Antes de abrir, `launch()` já recusa perfis em uso por cópia ou reset (`_held`) e perfis ainda fechando (`_stopping`). Baixar a versão nova e pegar a trava cabem antes dessa chamada, com o perfil reservado do mesmo jeito que `hold_stopped()` faz para duplicar e resetar.
- **Fechar pelo Manager**: `POST /api/profiles/{id}/stop` chama `stop()`, que tira a última prévia e fecha o contexto.
- **Fechar pela janela, cair ou perder a licença**: `_on_browser_closed()` trata os três. A licença negada deixa um arquivo de negação que o Manager lê; janela fechada e queda não deixam nada e não se distinguem.
- **Fim de verdade**: os dois caminhos terminam em `_dispose_running()`, e só depois `_release_stopping()` tira o perfil de "fechando". Enviar a versão e soltar a trava cabem nesse ponto, quando o Chromium já terminou de gravar a pasta.
- **Manager fechado com perfis abertos**: `cleanup_all()` fecha todos ao desligar. Se o Mac desligar sem isso, nada roda, e a trava fica presa (por isso "forçar liberação").

## Fontes

Todas neste repo: `backend/database.py` (`_PROFILE_SCHEMA`, `user_data_dir_for`, `create_profile`); `backend/browser_manager.py` (`launch`, `_build_fingerprint_args`, `_init_profile_defaults`, `stop`, `_on_browser_closed`, `_dispose_running`, `hold_stopped`, `cleanup_all`, `auto_launch_all`); `backend/main.py` (`_RESET_STATE_FILES`, `_RESET_STATE_DIRS`, `_DUPLICATE_SKIP_FILES`, rotas de launch, stop e duplicate); `backend/artifacts.py`; `backend/downloads.py`; `backend/settings_store.py`; `app_entry.py` (`window.json`). Tamanhos medidos com `du` nas pastas de perfil do PC Windows.
