# Protótipo: um perfil copiado de um Mac abre no outro com tudo?

PROTÓTIPO descartável do ticket "Um perfil copiado de um Mac abre no outro com tudo?" (#9), parte do mapa #3. Feito em 2026-11-25. Não vai para a `main`.

## Resposta

**Sim, para tudo o que mora na pasta do perfil.** Um perfil copiado (pasta sem caches nem travas) abriu com as abas, o cookie, a senha salva, o histórico e o estado da extensão, e com a mesma impressão digital. Senhas e cookies foram decifrados fora do Mac, num PC Windows. Ninguém precisa copiar chave do Keychain.

O motivo: o Playwright, que o pacote `cloakbrowser` usa para abrir o navegador, sempre passa `--use-mock-keychain`, e o `cloakbrowser` 0.7.3 só desliga `--enable-automation` e `--enable-unsafe-swiftshader` (`IGNORE_DEFAULT_ARGS` em `cloakbrowser/config.py`). Com essa opção, o Chromium tranca senhas e cookies com uma chave fixa e pública, igual em qualquer máquina. Isso corrige a pesquisa "Senhas e cookies continuam legíveis num perfil levado para outro Mac?" (#4), que supunha o Keychain de cada Mac.

## Como foi testado

Só no Mac do dono: o segundo Mac não estava disponível. O navegador rodou sem janela (headless), pelo pacote oficial `cloakbrowser` e com a licença do jeito que o Manager a usa, numa pasta temporária. O banco, os perfis e o Manager do dono não foram tocados, e a pasta foi apagada no fim.

1. `prototipo_viagem.py` cria dois perfis (um com "Cookies portáteis" desligado, outro ligado), com semente fixa e uma extensão-contador num caminho fixo. Em cada um: grava um cookie persistente (httpbin), salva uma senha de teste pelo gerenciador de senhas do navegador, abre três abas e clica três vezes no contador.
2. Copia a pasta para outra pasta, sem `Singleton*`, `Cache`, `Code Cache`, `GPUCache` e `last_screenshot.jpg`, e abre a cópia.
3. Abre a cópia de novo com outra semente, para ver o que a semente controla.
4. `decifra.py` leva `Cookies` e `Login Data` da cópia para um PC Windows e os decifra com a chave fixa (`mock_password`).

## Resultado

| Item | Na cópia |
|---|---|
| Abas abertas (3) | voltaram |
| Cookie persistente | veio |
| Senha salva | veio |
| Histórico | veio |
| Extensão e o estado dela | veio (o contador seguiu de 3 para 4) |
| Impressão digital (agente, GPU do WebGL, canvas) | igual à do original |
| Decifrar senha e cookie fora do Mac | deu certo, nos dois perfis |
| Item "Chromium Safe Storage" no Keychain | nunca foi criado |

- **"Cookies portáteis"** não fez diferença: com a chave fixa, os cookies já viajam com ela ligada ou desligada.
- **Semente**: com outra semente, a GPU informada ao site mudou, e o agente e o canvas deste teste simples ficaram iguais. A GPU vem da semente, não do hardware do Mac, o que sugere a mesma impressão digital num Mac com outro chip; não foi provado.
- **Tamanho**: pasta de 9,3 MB, cópia sem caches de 8,7 MB (perfil quase vazio).
- **Tempo e memória** (sem janela, então só servem de referência): abrir levou de 0,4 s a 1,6 s; com três abas, de 9 a 13 processos e de 800 MB a 1,2 GB.

## O lado ruim

A chave fixa é pública: quem pegar a pasta de um perfil, num Mac, no servidor ou num backup, lê as senhas e os cookies dele. Isso já vale hoje, para todos os perfis. Pesa no ticket "Onde fica a chave da criptografia e como o outro usuário a recebe?" (#11): a cópia guardada no servidor precisa estar cifrada.

## O que ficou para os dois Macs

`roteiro-dois-macs.html` é o roteiro à mão para fazer com o segundo Mac. Ele confere o que este teste não alcança:

- a impressão digital num Mac com outro chip;
- o tempo de abrir e a memória com janela, nos dois Macs;
- as versões do Manager e do navegador no segundo Mac (as duas precisam ser iguais);
- o login num site que só guarda o cookie da sessão.

## Arquivos

- `prototipo_viagem.py`: o teste no Mac (roda com o Python do Manager; precisa de uma pasta `/tmp/cloak-wf9-prototipo` com a extensão em `ext/contador`).
- `decifra.py`: a prova fora do Mac.
- `roteiro-dois-macs.html`: o roteiro para os dois Macs.
