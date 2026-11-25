# Senhas e cookies num perfil levado para outro Mac

Pesquisa do ticket "Senhas e cookies continuam legíveis num perfil levado para outro Mac?" (#4), parte do mapa #3. Feita em 2026-11-25, só lendo fontes; nada foi rodado num Mac.

## Resposta curta

- **Não, por padrão.** No macOS o Chromium cifra cookies e senhas salvas com uma chave aleatória guardada no Keychain do usuário daquele Mac. No outro Mac a chave é outra, e esses dados chegam ilegíveis.
- **Cookies portáteis resolve só cookies.** A opção do CloakBrowser troca a chave dos cookies por uma independente da máquina, e só para cookies salvos com ela ligada. Nada nas fontes diz que cobre senhas.
- **Dois caminhos cobrem senhas e cookies juntos**, e os dois precisam ser testados num Mac:
  1. **Mesmo item "Safe Storage" nos dois Macs** (recomendado): copiar uma vez o item do Keychain de um Mac para o outro. Os dois passam a ter a mesma chave, e tudo que um cifra o outro lê. Nada muda para os sites.
  2. **`--use-mock-keychain`**: o Chromium deixa de usar o Keychain e usa uma senha fixa, pública, escrita no código. Funciona entre máquinas, mas é uma opção feita para testes e qualquer pessoa com a pasta do perfil decifra tudo.

## O que as fontes dizem

### A chave mora no Keychain de cada Mac

- O Chromium procura no Keychain um item genérico de serviço `Chromium Safe Storage` (conta `Chromium`), ou `Chrome Safe Storage` nas versões com a marca Google. Se não acha, gera uma senha aleatória de 128 bits e a grava ali. Fonte: [`components/os_crypt/common/keychain_password_mac.mm`](https://github.com/chromium/chromium/blob/main/components/os_crypt/common/keychain_password_mac.mm) (`kDefaultServiceName`, `AddRandomPasswordToKeychain`).
- Dessa senha sai a chave dos dados com prefixo `v10`. Fonte: [`components/os_crypt/async/browser/keychain_key_provider.mm`](https://github.com/chromium/chromium/blob/main/components/os_crypt/async/browser/keychain_key_provider.mm) (`kDefaultKeyTag = "v10"`).
- As senhas salvas (`Login Data`) são cifradas pelo mesmo mecanismo (OSCrypt). Fonte: [`components/password_manager/core/browser/password_store/login_database.cc`](https://github.com/chromium/chromium/blob/main/components/password_manager/core/browser/password_store/login_database.cc) (usa `os_crypt_async::Encryptor`).

Consequência: como a chave é por usuário do Mac, e não por perfil, **todos os perfis de um Mac usam a mesma chave**. Copiar o item uma vez resolve todos os perfis.

### Cookies portáteis

- README do CloakBrowser, tabela de flags: `--fingerprint-portable-cookies` "Encrypt cookies with a machine-independent key so a copied profile keeps its logins across machines. Turn it on from the first launch — it changes how cookies are written, so a cookie is only portable if this was set when it was saved." Fonte: [README do CloakHQ/CloakBrowser](https://github.com/CloakHQ/CloakBrowser#additional-flags).
- O Manager expõe isso como a caixa "Portable cookies" por perfil, desligada por padrão (`backend/browser_manager.py`, `_build_fingerprint_args`; `CHANGELOG.md`, "Transparent proxy and portable cookies, per profile").
- A flag fala só de cookies. Senhas não são mencionadas.

### `--use-mock-keychain`

- Definida em [`components/os_crypt/common/os_crypt_switches.h`](https://github.com/chromium/chromium/blob/main/components/os_crypt/common/os_crypt_switches.h): "Uses mock keychain for testing purposes, which prevents blocking dialogs from causing timeouts."
- Com ela, o Chromium usa um Keychain falso ([`crypto/apple/fake_keychain_v2.mm`](https://github.com/chromium/chromium/blob/main/crypto/apple/fake_keychain_v2.mm)) que devolve sempre a senha `mock_password`. A chave é a mesma em qualquer máquina, e qualquer pessoa a conhece.
- É uma flag do Chromium e não do CloakBrowser; o binário do CloakBrowser é um Chromium modificado, então ela deve existir, mas isso não está documentado no README do CloakBrowser.
- Ela não muda nada que um site veja: o Keychain não é exposto a páginas. Isso é dedução do código, não teste.

## O que fica para verificar num Mac

Vai para o protótipo "Um perfil copiado de um Mac abre no outro com tudo?" (#9):

1. O nome exato do item que o binário do CloakBrowser cria no Keychain (procurar por "Safe Storage" no app Acesso às Chaves depois do primeiro uso).
2. Com o mesmo item nos dois Macs, um perfil copiado abre com senhas salvas e logins.
3. Se o binário aceita `--use-mock-keychain` (só como plano B).
4. Se a impressão digital fica igual nos dois Macs com o mesmo perfil.
5. Se um perfil que já tem dados cifrados com a chave antiga continua legível depois de trocar o item do Keychain (o que acontece com perfis que já existem).

## Riscos para as próximas decisões

- Copiar o item do Keychain é um passo manual, uma vez por Mac, e a senha copiada é um segredo: vale decidir junto com o ticket "Onde fica a chave da criptografia e como o outro usuário a recebe?" (#11).
- Se um Mac já tem perfis com a chave dele, trocar o item deixa esses perfis ilegíveis. A ordem certa é escolher um Mac como origem da chave antes de criar perfis compartilhados no outro.
- `--use-mock-keychain` deixa senhas legíveis para quem pegar a pasta do perfil. Com a cópia no servidor criptografada isso só pesa nos discos dos Macs, mas é um rebaixamento real.
