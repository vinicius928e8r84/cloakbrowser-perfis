## Summary

## Evidence

## Merge Danger

**Door:**

**Blast Radius:**

**Atenção:**

**Categoria:**

Closes https://github.com/vinicius928e8r84/cloakbrowser-perfis/issues/N

<!--
O check "Registro da PR" (.github/workflows/registro-da-pr.yml, scripts/freios/registro_da_pr.py) confere, no head exato da PR.
O que está em comentário de HTML, em bloco de código ou em citação (>) não conta.

1. Atenção: uma linha "Atenção: BAIXA", "Atenção: MÉDIA" ou "Atenção: ALTA" (o valor sozinho na linha).
   ALTA é obrigatória se a PR mexe em .github/, .githooks/, scripts/freios/, AGENTS.md, CLAUDE.md ou nos arquivos do backend
   que guardam perfis, banco, trava e lançador do navegador (CAMINHOS_SENSIVEIS em scripts/freios/registro_da_pr.py),
   e exige a seção "Prova real" (item 5).

2. Categoria: uma linha "Categoria: <valor>" com um valor de scripts/freios/categorias.json
   (freio, conserto, recurso, limpeza, refatoração, plano, pesquisa).

3. Issue: uma linha "Closes <URL completa da issue>" por issue que a PR fecha, "Parte de <URL completa da issue>" para um passo
   de uma série (https://github.com/vinicius928e8r84/cloakbrowser-perfis/issues/<N>; o número solto não vale),
   ou "Sem issue" sozinho na linha. Troque a linha Closes de cima por uma dessas.

4. Revisão independente: um comentário de revisão da PR, de quem pode escrever no repositório, com as linhas

   Veredito: CLEAN
   Head: <SHA inteiro do head, 40 caracteres: git rev-parse HEAD>
   Autor: <quem escreveu a mudança>
   Revisor: <quem revisou; não é o autor nem quem abriu a PR>
   Risco: <BAIXA, MÉDIA ou ALTA: o risco que o revisor viu>

   Vale o registro mais recente com o head exato. Um commit novo muda o head: revise de novo. Se o revisor registrar
   Risco: ALTA, a PR conta como ALTA mesmo com o corpo dizendo BAIXA ou MÉDIA. Um registro publicado como comentário
   simples não roda o check de novo; publique como revisão:
   python -m scripts.freios.registrar_na_pr revisao --pr <número> --head <SHA> --autor <quem> --revisor <quem> --risco baixa|media|alta --publicar

5. Prova real, com atenção ALTA: a seção abaixo, com uma única linha Head: com o SHA inteiro e uma explicação de pelo menos
   40 caracteres do que foi rodado de verdade e do que apareceu. NÃO COBERTO e BLOQUEADA invalidam a seção.

   ## Prova real

   PROVADO 100% REAL
   Head: <SHA inteiro do head>

   <o que você rodou e o que apareceu>

   python -m scripts.freios.registrar_na_pr prova --pr <número> --head <SHA> --cobertura total --nota <arquivo> --publicar
   escreve a seção com o head lido no GitHub.

O check confere o artefato e o SHA, não que a revisão ou a prova aconteceram.
-->
