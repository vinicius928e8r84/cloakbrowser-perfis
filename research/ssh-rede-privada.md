# O SSH da rede privada deixa a conta de arquivos só com arquivos?

Pesquisa do ticket [O SSH da rede privada deixa a conta de arquivos só com arquivos?](https://github.com/vinicius928e8r84/cloakbrowser-perfis/issues/34), feita em 2026-11-27. Fontes: a documentação do Tailscale (lida nesse dia), o código do Tailscale no commit [`72a7f41`](https://github.com/tailscale/tailscale/tree/72a7f41564816f6e3070c3bc87764ab54167e2cd) (2026-11-26), a documentação e o código do restic no commit [`f25ec9a`](https://github.com/restic/restic/tree/f25ec9a5ab18fbb6797ab336b995d6639d62c4d4), o manual do `sshd_config` do OpenSSH e o manual do `nologin` do util-linux. Também houve um teste de verdade num contêiner (seção "Teste"); nada foi mexido no servidor nem na rede privada do dono.

"Rede privada" é o Tailscale; "SSH da rede privada" é o Tailscale SSH; "conta de arquivos" é a conta do servidor só para os perfis, decidida em [O que roda no servidor para guardar perfis e travas?](https://github.com/vinicius928e8r84/cloakbrowser-perfis/issues/7).

## Resposta curta

- **Sim, com uma condição: a conta de arquivos tem como shell o `nologin`.** Assim, pelo Tailscale SSH, ela não roda comando nem abre terminal, e o SFTP continua funcionando, servido pelo próprio Tailscale. O restic e a trava (criar a pasta uma vez) funcionam por esse SFTP. Testado num contêiner com o `tailscaled` compilado do código atual.
- **A regra do Tailscale não tem como dizer "só SFTP".** Ela diz só quem entra, em que máquina e como qual conta. O que segura a conta é o `nologin` no servidor. O `sshd_config` (onde ficariam `ForceCommand internal-sftp` e `ChrootDirectory`) não vale para o Tailscale SSH.
- **"Na pasta dela" vale para gravar, não para ler.** O SFTP do Tailscale não prende a conta numa pasta: ela grava só onde as permissões deixam, mas lê qualquer arquivo do servidor que seja legível por todos.
- **Repasse de portas**: a regra do Tailscale não o liga nem desliga, e a documentação não diz o que vale por padrão. Desliga-se no servidor com `TS_SSH_DISABLE_FORWARDING=true` (vale para todo o Tailscale SSH daquela máquina). Precisa ser testado na rede de verdade.
- **A regra "o sócio só chega a este servidor, só como a conta de arquivos"** se escreve com o servidor marcado por uma etiqueta (`tag:`), uma permissão de rede só para a porta 22 e uma regra `ssh` com `users: ["<conta de arquivos>"]`. Cabe no plano grátis em número de usuários e de máquinas com SSH, mas **o plano grátis é só para uso não comercial**.
- **O Manager vê sozinho, sem token**, pelo `tailscale status --json` do próprio Mac: se o Mac está na rede privada, o nome e o ID dele, e se o servidor está ligado e com SSH. **Ele não consegue tirar um Mac da rede**: isso é sempre no painel do Tailscale.
- **O plano B (usuário e senha da conta de arquivos) não é necessário.**

## 1. O restic funciona pelo Tailscale SSH?

Sim.

- O restic, no backend `sftp`, chama o `ssh` do sistema com `-s sftp`, ou outro programa dado em `-o sftp.command` ([`sftp.go`, `buildSSHCommand`](https://github.com/restic/restic/blob/f25ec9a5ab18fbb6797ab336b995d6639d62c4d4/internal/backend/sftp/sftp.go#L236); [documentação, seção SFTP](https://github.com/restic/restic/blob/f25ec9a5ab18fbb6797ab336b995d6639d62c4d4/doc/030_preparing_a_new_repo.rst)). Um caminho sem `/` no começo é relativo à pasta da conta.
- O Tailscale SSH pega a porta 22 do endereço do servidor na rede privada e "implementa o SFTP, o que deixa SCP e SFTP funcionarem" ([Tailscale SSH, "Authentication and authorization"](https://tailscale.com/kb/1193/tailscale-ssh)). A autenticação é do tipo `none`: o `ssh` do macOS não precisa de chave nem de senha.
- O cliente pode ser qualquer variante do Tailscale no Mac. Só a da App Store não tem o comando `tailscale ssh`; com ela usa-se o `ssh` comum ([variantes do macOS](https://tailscale.com/kb/1065/macos-variants)). O servidor precisa ser Linux (ou o `tailscaled` de código aberto no macOS).
- A chave do servidor: o `tailscale ssh` escreve um `known_hosts` próprio com as chaves que o `tailscale status --json` traz em `sshHostKeys` e chama o `ssh` com `StrictHostKeyChecking yes` ([`cli/ssh.go`](https://github.com/tailscale/tailscale/blob/72a7f41564816f6e3070c3bc87764ab54167e2cd/cmd/tailscale/cli/ssh.go#L99-L113), [`genKnownHosts`](https://github.com/tailscale/tailscale/blob/72a7f41564816f6e3070c3bc87764ab54167e2cd/cmd/tailscale/cli/ssh.go#L178)). O Manager pode fazer o mesmo e passar ao restic um `sftp.command` com esse `known_hosts`, o que serve às três variantes.
- No teste, o restic 0.18 criou o repositório, fez duas versões, listou, restaurou e conferiu (`check`: sem erros) pelo SFTP do Tailscale, entrando como uma conta com `nologin`.

## 2. A conta fica só com arquivos?

Sim, se o shell dela for o `nologin`. É uma conclusão lida no código e confirmada no teste, não uma promessa escrita na documentação.

**O que a regra do Tailscale consegue dizer.** Uma regra `ssh` tem `action`, `src`, `dst`, `users`, `checkPeriod` e `acceptEnv` ([Tailscale SSH](https://tailscale.com/kb/1193/tailscale-ssh)); nada sobre quais comandos rodam. A própria documentação diz que o Tailscale SSH "pode não servir para máquinas em que se usa `authorized_keys` para limitar os comandos" (seção "OS user authentication on the client"). E ela não lê o `sshd_config` nem o `authorized_keys` (mesma página, "Transition from your existing SSH client"), então `ForceCommand internal-sftp` e `ChrootDirectory` ([`sshd_config(5)`](https://man.openbsd.org/sshd_config.5)) não valem para quem entra pelo Tailscale SSH.

**Como o Tailscale SSH roda cada pedido** ([`incubator.go`](https://github.com/tailscale/tailscale/blob/72a7f41564816f6e3070c3bc87764ab54167e2cd/ssh/tailssh/incubator.go)):

- Terminal ou comando: roda o shell da conta, com `-l` ou `-c <comando>` (`handleSSHInProcess`, linha 726, e `shellArgs`, linha 1420), ou passa por `su -l <conta> -c <comando>` (`trySU`, linha 633). Os dois caminhos usam o shell da conta.
- SFTP: no Linux, antes tenta `su -l <conta> -c true`; se isso falha, serve o SFTP dentro do próprio processo do Tailscale, já com a conta e na pasta dela (`findSU`, linha 679; `handleSFTPInProcess`, linha 526). O servidor de SFTP é o `github.com/pkg/sftp` sem opção nenhuma ([`sftp.go`](https://github.com/tailscale/tailscale/blob/72a7f41564816f6e3070c3bc87764ab54167e2cd/ssh/tailssh/sftp.go)).
- O `nologin` "mostra que a conta não está disponível e sai com erro"; sai sempre com 1 e ignora `-c` e `-l` ([`nologin(8)`](https://github.com/util-linux/util-linux/blob/e57914591653c66e616716ac2d3db8d702bf4b1c/login-utils/nologin.8.adoc)).

Logo, com o `nologin`: terminal e comando batem no `nologin` e param; a sondagem do `su` falha, e o SFTP é servido pelo Tailscale. Isso também vale no modo antigo do Tailscale SSH ("v1"), que serve o SFTP sempre dentro do processo (`shouldAttemptLoginShell`).

**O que sobra:**

- **Ler fora da pasta.** O SFTP não prende a conta na pasta dela. No teste, ela leu um arquivo legível por todos na pasta de outra conta, e não conseguiu gravar lá ("Permission denied"). Vale conferir que as pastas do dono e o que mais importa no servidor estão fechadas para as outras contas (por exemplo, `chmod 750` ou `700`).
- **Repasse de portas** (`ssh -L` ou `-R`, que funcionam sem shell). O Tailscale só deixa se a decisão que vem do painel trouxer `AllowLocalPortForwarding` ou `AllowRemotePortForwarding` ([`tailcfg.SSHAction`](https://github.com/tailscale/tailscale/blob/72a7f41564816f6e3070c3bc87764ab54167e2cd/tailcfg/tailcfg.go#L2782)); a regra escrita pelo dono não tem esses campos, e a documentação não diz o que o painel manda. No servidor, `TS_SSH_DISABLE_FORWARDING=true` desliga o repasse para todo o Tailscale SSH da máquina ([`tailssh.go`, linhas 57 e 685-700](https://github.com/tailscale/tailscale/blob/72a7f41564816f6e3070c3bc87764ab54167e2cd/ssh/tailssh/tailssh.go#L57)). No pacote para Linux, o serviço lê as variáveis de `/etc/default/tailscaled` ([`tailscaled.service`](https://github.com/tailscale/tailscale/blob/72a7f41564816f6e3070c3bc87764ab54167e2cd/cmd/tailscaled/tailscaled.service)). É uma chave do código, não da documentação. **Precisa de teste na rede de verdade**: `ssh -N -L 9999:localhost:22 <conta de arquivos>@<servidor>` tem de ser recusado.
- **Qualquer programa do Mac entra.** Sem chave, qualquer usuário ou programa de um Mac autorizado chega à conta de arquivos (Tailscale SSH, "OS user authentication on the client"). É o mesmo que já se aceitava com uma chave SSH guardada no Mac.
- **Depende do comportamento do código.** Uma versão futura do Tailscale no servidor pode mudar o caminho do SFTP. O teste das seções "Teste" e "O que testar no servidor" deve ser refeito depois de atualizar o Tailscale do servidor.

**Como se escreve no servidor** (uma vez, pelo dono):

```
sudo useradd -m -s /usr/sbin/nologin <conta de arquivos>    # conta nova
sudo usermod -s /usr/sbin/nologin <conta de arquivos>       # ou, se ela já existe
```

## 3. A regra "o sócio só chega a este servidor, e só como a conta de arquivos"

**O servidor precisa de uma etiqueta.** Pela documentação, as únicas ligações SSH permitidas são de um usuário para os próprios aparelhos, para um aparelho com etiqueta, ou para um aparelho com etiqueta compartilhado com ele; o destino de uma regra `ssh` é uma etiqueta, `autogroup:self` ou o próprio usuário ([Tailscale SSH, "Order of evaluation"](https://tailscale.com/kb/1193/tailscale-ssh); [sintaxe da política, `ssh`](https://tailscale.com/kb/1337/policy-syntax)). Pôr a etiqueta tira o servidor do nome do dono: as regras com `autogroup:self` deixam de valer para ele.

**Duas formas de o sócio entrar**, as duas no plano grátis:

| | Compartilhar o servidor com o sócio | Convidar o sócio como membro |
|---|---|---|
| Conta do sócio | a rede privada dele, à parte | entra na rede do dono |
| O que ele vê | só o servidor, "e nada mais" ([compartilhamento](https://tailscale.com/kb/1084/sharing)) | o que a política deixar; a política padrão deixa tudo |
| Tirar um Mac do sócio | o dono só corta o compartilhamento inteiro; um Mac só, o próprio sócio tira na rede dele | o dono tira o aparelho exato |
| Conta como usuário do plano | a documentação não diz | sim |

Rascunho da política para o compartilhamento (`<conta de arquivos>`, os e-mails e a etiqueta são marcadores):

```jsonc
{
  "tagOwners": { "tag:perfis": ["<e-mail do dono>"] },
  "grants": [
    { "src": ["<e-mail do dono>"], "dst": ["*"], "ip": ["*"] },
    { "src": ["<e-mail do sócio>"], "dst": ["tag:perfis"], "ip": ["22"] }
  ],
  "ssh": [
    { "action": "accept", "src": ["<e-mail do dono>", "<e-mail do sócio>"],
      "dst": ["tag:perfis"], "users": ["<conta de arquivos>"] },
    { "action": "check", "src": ["<e-mail do dono>"],
      "dst": ["tag:perfis"], "users": ["<conta de administrador do dono>"] }
  ]
}
```

Notas da documentação para essa regra:

- `autogroup:shared` (quem aceitou um compartilhamento) vale como origem de permissão de rede, mas **não como origem de regra `ssh`**; nesta usa-se o e-mail do sócio ([seletores](https://tailscale.com/kb/1396/targets)).
- Uma regra com `"src": ["*"]` vale também para quem recebeu compartilhamento ([compartilhamento](https://tailscale.com/kb/1084/sharing)); e `autogroup:member` numa regra `ssh` inclui quem recebeu o servidor compartilhado (Tailscale SSH, `src`). Se a política atual do dono tem `*` ou `autogroup:member` como origem, isso precisa sair, ou o sócio ganha mais do que a porta 22.
- `users` lista só contas que já existem no servidor; `autogroup:nonroot` daria todas as contas que não são root (Tailscale SSH, "Important note about autogroup:nonroot").
- A política aceita testes que conferem as regras de SSH ao salvar (Tailscale SSH, "SSH tests"); vale um "o sócio não entra como <conta de administrador do dono>".
- Mudança na política chega ao servidor em segundos e derruba as ligações que ela tirou (Tailscale SSH, "User revocation").

**Cuidado ao ligar** (Tailscale SSH, "Advertise SSH on the host" e "Transition"): `tailscale set --ssh` no servidor faz o Tailscale tomar a porta 22 do endereço da rede privada, e as ligações SSH abertas por esse endereço travam. Se hoje o dono entra no servidor pelo endereço da rede privada com o OpenSSH, depois de ligar ele passa a entrar pelo Tailscale SSH, como a conta que a política deixar: a regra da conta de administrador precisa estar salva antes, e convém ter outro caminho de entrada. O `sshd_config` e as chaves de hoje não mudam e seguem valendo por fora da rede privada.

**Plano grátis** ([preços](https://tailscale.com/pricing), pela tabela da página): até 6 usuários, aparelhos ilimitados, 50 aparelhos com etiqueta, "Basic Tailscale SSH" com até 5 máquinas; o compartilhamento é de todos os planos ([compartilhamento](https://tailscale.com/kb/1084/sharing)). O modo `check` com tempo diferente do padrão é de plano pago. Mas a página de preços diz que o plano Personal "só serve para uso não comercial"; o plano Standard custa 8 dólares por usuário por mês.

## 4. O que o Manager vê sozinho, sem token da rede privada

O Tailscale de cada Mac traz a linha de comando (na variante do site, em `/Applications/Tailscale.app/Contents/MacOS/Tailscale`; [CLI](https://tailscale.com/kb/1080/cli)), e `tailscale status --json` fala com o Tailscale local, sem token. Os campos ([`ipnstate.go`](https://github.com/tailscale/tailscale/blob/72a7f41564816f6e3070c3bc87764ab54167e2cd/ipn/ipnstate/ipnstate.go)):

- `BackendState`: `Running` quando o Mac está na rede; outro valor (por exemplo, precisando entrar, ou parado) vira "Entre na rede privada primeiro".
- `Self`: `HostName`, `DNSName` e `ID` (ID estável do aparelho) do próprio Mac, e o usuário dele em `User`. É o que o Manager pode gravar na pasta do servidor ao entrar e mostrar no cadeado e em Configurações › Compartilhamento.
- O servidor em `Peer`: `Online`, `sshHostKeys` (se vazio, o SSH da rede privada não está ligado ou a política não deixa), `Tags` e `ShareeNode`.

"Testar conexão" pode então: ler o estado; achar o servidor pelo nome configurado; escrever o `known_hosts` com as chaves dele; abrir um SFTP como a conta de arquivos e criar e apagar uma pasta de teste. Cada falha tem uma frase própria: fora da rede, servidor desligado, SSH não ligado ou política sem regra, conta recusada.

"Tirar um Mac": o Manager **não tira** um aparelho da rede privada; sem token, isso é no painel do Tailscale (Machines › Remove; ou cortar o compartilhamento do sócio). Ele pode mostrar o nome e o ID do Mac a tirar e onde clicar. Um Mac já tirado só se nota quando ele mesmo tenta entrar e falha: os outros Macs não sabem disso sozinhos.

## Teste

Num contêiner Debian, com o `tailscaled` compilado do commit `72a7f41` e chamado como o Tailscale SSH o chama para cada pedido (`tailscaled be-child ssh ...`, os mesmos argumentos que `newIncubatorCommand` monta), para uma conta com `/usr/sbin/nologin`. Isso testa o servidor de SSH do Tailscale no servidor; não testa o painel, a política, a rede nem o Mac.

| Pedido | Resultado |
|---|---|
| `su -l <conta> -c true` (a sondagem) | "This account is currently not available.", sai com 1 |
| comando (`id`) | recusado, sai com 1 |
| terminal | recusado, sai com 1 |
| SFTP: `pwd` | a pasta da conta |
| SFTP: criar a mesma pasta duas vezes | a primeira cria, a segunda falha (a trava funciona) |
| SFTP: gravar e listar um arquivo dentro da pasta | funciona |
| SFTP: ler arquivo legível por todos de outra conta | **funciona** (não há prisão na pasta) |
| SFTP: gravar na pasta de outra conta | recusado ("Permission denied") |
| restic `init`, duas versões, `snapshots`, `restore`, `check` | tudo funciona, "no errors were found" |
| controle: mesma conta com `/bin/bash`, comando `id` | roda (a diferença é o `nologin`) |

Para o restic, o `sftp.command` foi o próprio `tailscaled be-child ssh ... --sftp`; o `sftp` do OpenSSH foi ligado ao mesmo comando com `sftp -D`.

## O que testar no servidor, com a rede de verdade

Feito pelo dono depois de ligar, com um Mac de cada um:

1. `sftp <conta de arquivos>@<servidor>` funciona sem pedir senha, dos dois Macs.
2. `ssh <conta de arquivos>@<servidor>` e `ssh <conta de arquivos>@<servidor> id` são recusados.
3. `ssh -N -L 9999:localhost:22 <conta de arquivos>@<servidor>` é recusado (se não for, ligar `TS_SSH_DISABLE_FORWARDING=true`).
4. Do Mac do sócio, `ssh <conta de administrador do dono>@<servidor>` é recusado, e nenhum outro aparelho do dono responde.
5. Repetir 1 a 3 depois de cada atualização do Tailscale no servidor.
