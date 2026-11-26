# Agent Instructions

This project uses **bd** (beads) for issue tracking. Run `bd onboard` to get started.

## Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --status in_progress  # Claim work
bd close <id>         # Complete work
bd sync               # Sync with git
```

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds


## Freios

`python scripts/freios/freios.py --commit` confere tamanho e comentários do que está no commit; `--tudo` confere o índice inteiro e os commits da branch (tamanho, comentários e docstrings, sintaxe de JSON, segredos, binários, ruff, ESLint e autoria). Cada verificação diz o conserto quando falha. Vale para Python, TS/TSX, JS, CSS, shell, PowerShell, YAML e TOML.

O teto de tamanho e de comentários de cada arquivo é a medida dele na `main`, no ponto em que a branch saiu dela: encolher passa, crescer reprova e arquivo novo nasce dentro dos limites (20000 bytes, 1000 linhas). Os tetos ficam em `scripts/freios/limites.json` e as exceções, com motivo, num só arquivo, `scripts/freios/excecoes.json` (que o ruff e o ESLint também leem); mudar um deles é decisão do dono. O ESLint pede `npm ci --prefix scripts/freios` uma vez; sem isso o freio avisa e pula. Ligue os ganchos uma vez por clone com `git config core.hooksPath .githooks`. Testes dos freios: `python -m unittest discover -s scripts/freios -t .`.

## Pull requests

Toda mudança entra por PR para a `main`; ninguém mescla a própria PR. O corpo segue `.github/PULL_REQUEST_TEMPLATE.md`: `Atenção:` BAIXA, MÉDIA ou ALTA, `Categoria:` (lista em `scripts/freios/categorias.json`) e uma linha `Closes <URL>`, `Parte de <URL>` ou `Sem issue`. O check "Registro da PR" exige, no head exato, uma revisão independente CLEAN (revisor diferente do autor e de quem abriu a PR) e o CI verde. ALTA exige também a seção "Prova real" com a frase PROVADO 100% REAL e o head.

Contam como ALTA, qualquer que seja o corpo: `.github/`, `.githooks/`, `scripts/freios/`, `AGENTS.md`, `CLAUDE.md` e, no backend, `backend/database.py` (banco e migrações), `backend/models.py` (perfis), `backend/browser_manager.py` (lançador do navegador e trava de perfil), `backend/artifacts.py` (sincronização de arquivos do perfil), `backend/runtime.py` (pastas de dados), `backend/main.py` (rotas de perfil) e `backend/requirements.txt` (versão do navegador). Não troque a versão do navegador nem atualize dependências sem pedido do dono: o Dependabot só atualiza GitHub Actions, e a autoria do `dependabot[bot]` só passa em ramo `dependabot/github_actions/` aberto por ele.
