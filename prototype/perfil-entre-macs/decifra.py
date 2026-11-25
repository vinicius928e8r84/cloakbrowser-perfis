# Prova fora do Mac: decifra com a chave fixa de teste do Chromium ("mock_password").
import hashlib, sqlite3, sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
CHAVE = hashlib.pbkdf2_hmac("sha1", b"mock_password", b"saltysalt", 1003, 16)
def dec(b):
    if b[:3] != b"v10": return None, b[:3]
    d = Cipher(algorithms.AES(CHAVE), modes.CBC(b" " * 16)).decryptor()
    p = d.update(b[3:]) + d.finalize()
    if not 1 <= p[-1] <= 16: return None, "padding"
    return p[:-p[-1]], "v10"
for base in sys.argv[1:]:
    c = sqlite3.connect(f"file:{base}/Default/Cookies?mode=ro", uri=True)
    for host, nome, val in c.execute("select host_key, name, encrypted_value from cookies where name='teste'"):
        p, pre = dec(val)
        ok = p is not None and p.endswith(b"viagem")
        print(base.split("/")[-1], "cookie", host, nome, "prefixo", pre, "decifrou e bate:", ok)
    l = sqlite3.connect(f"file:{base}/Default/Login Data?mode=ro", uri=True)
    for url, user, pw in l.execute("select origin_url, username_value, password_value from logins"):
        p, pre = dec(pw)
        print(base.split("/")[-1], "senha", url, user, "prefixo", pre, "decifrou e bate:", p == b"senha-de-teste-wf9")
