# PROTÓTIPO descartável do ticket "Um perfil copiado de um Mac abre no outro com tudo?".
# Roda no Mac, numa pasta só dele (W). Não toca no banco, nos perfis nem no Manager.
import asyncio, hashlib, json, os, re, shutil, sqlite3, subprocess, sys, time
from pathlib import Path

W = Path(sys.argv[1])
assert W.name == "cloak-wf9-prototipo" and W.is_dir()
EXT = W / "ext" / "contador"
BASE = W / (sys.argv[2] if len(sys.argv) > 2 else ".")
BASE.mkdir(exist_ok=True)
SEED, SEED_OUTRA = 54321, 12345

# Chave e binário pelo mesmo caminho que o Manager do dono usa (abrir.command), sem imprimir.
cmd = (Path.home() / "cloakbrowser" / "abrir.command").read_text()
for nome in ("CLOAKBROWSER_LICENSE_KEY", "CLOAKBROWSER_BINARY_PATH"):
    m = re.search(rf'^export {nome}="?([^"\n]+)"?$', cmd, re.M)
    os.environ[nome] = m.group(1).replace("$HOME", str(Path.home()))
os.environ["CLOAKBROWSER_SUPPRESS_FONT_WARNING"] = "1"

from cloakbrowser import launch_persistent_context_async  # noqa: E402

FP_JS = """async () => {
  const c = document.createElement('canvas'); c.width = 240; c.height = 60;
  const x = c.getContext('2d'); x.font = '18px Arial'; x.fillStyle = '#f60'; x.fillRect(5,5,100,40);
  x.fillStyle = '#069'; x.fillText('prototipo wf9', 8, 30);
  const g = document.createElement('canvas').getContext('webgl');
  const d = g && g.getExtension('WEBGL_debug_renderer_info');
  return {ua: navigator.userAgent, plat: navigator.platform, cpu: navigator.hardwareConcurrency,
    mem: navigator.deviceMemory, tela: [screen.width, screen.height, devicePixelRatio],
    fuso: Intl.DateTimeFormat().resolvedOptions().timeZone, idioma: navigator.language,
    gpu: d ? g.getParameter(d.UNMASKED_RENDERER_WEBGL) : null, canvas: c.toDataURL()};
}"""


def h(v):
    return hashlib.sha256(json.dumps(v, sort_keys=True).encode()).hexdigest()[:12]


def memoria(udd):
    linhas = subprocess.run(["ps", "-axo", "pid=,ppid=,rss=,command="], capture_output=True, text=True).stdout.splitlines()
    procs = []
    for l in linhas:
        p = l.split(None, 3)
        if len(p) == 4:
            procs.append((int(p[0]), int(p[1]), int(p[2]), p[3]))
    raiz = [p[0] for p in procs if re.search(rf"--user-data-dir={re.escape(str(udd))}( |$)", p[3]) and "Helper" not in p[3]]
    arvore, mudou = set(raiz), True
    while mudou:
        mudou = False
        for pid, ppid, _, _ in procs:
            if ppid in arvore and pid not in arvore:
                arvore.add(pid); mudou = True
    return raiz, len(arvore), round(sum(p[2] for p in procs if p[0] in arvore) / 1024)


async def abrir(udd, portatil, seed=SEED):
    args = [f"--fingerprint={seed}", "--fingerprint-platform=macos", "--fingerprint-allow-3p-cookies",
            "--fingerprint-screen-width=1920", "--fingerprint-screen-height=1080", "--restore-last-session"]
    if portatil:
        args.append("--fingerprint-portable-cookies")
    t0 = time.monotonic()
    ctx = await launch_persistent_context_async(
        user_data_dir=str(udd), headless=True, args=args, extension_paths=[str(EXT)], geoip=False,
        license_key=os.environ["CLOAKBROWSER_LICENSE_KEY"])
    negado = getattr(ctx, "_cloak_denial_path", None)
    if negado and Path(negado).exists() and Path(negado).stat().st_size:
        raise SystemExit("licença negou a abertura")
    return ctx, round(time.monotonic() - t0, 1)


async def ext_id(ctx):
    for _ in range(20):
        sw = ctx.service_workers or ctx.background_pages
        if sw:
            return sw[0].url.split("/")[2]
        await asyncio.sleep(0.5)
    # sem service worker: lê o id em chrome://extensions
    p = await ctx.new_page()
    await p.goto("chrome://extensions")
    ids = await p.evaluate("() => new Promise(r => chrome.developerPrivate.getExtensionsInfo(l => r(l.map(e => [e.id, e.name]))))")
    await p.close()
    return next(i for i, n in ids if n == "Contador de teste")


async def contador(ctx, eid):
    p = await ctx.new_page()
    await p.goto(f"chrome-extension://{eid}/popup.html")
    await p.wait_for_function("document.getElementById('n').textContent !== '?'")
    n = int(await p.text_content("#n"))
    await p.close()
    return n


async def senhas(ctx, adicionar=False):
    p = await ctx.new_page()
    await p.goto("chrome://password-manager/passwords")
    await p.wait_for_function("!!(chrome && chrome.passwordsPrivate)")
    if adicionar:
        await p.evaluate("""() => new Promise((ok, erro) => chrome.passwordsPrivate.addPassword(
          {url: 'https://senha-de-teste.example', username: 'usuario-teste', password: 'senha-de-teste-wf9',
           note: '', useAccountStore: false}, () => chrome.runtime.lastError ? erro(chrome.runtime.lastError.message) : ok()))""")
        await asyncio.sleep(1)
    lista = await p.evaluate("() => new Promise(r => chrome.passwordsPrivate.getSavedPasswordList(l => r(l.map(e => e.username))))")
    await p.close()
    return lista


async def sessao1(udd, portatil):
    ctx, t = await abrir(udd, portatil)
    pg = ctx.pages[0] if ctx.pages else await ctx.new_page()
    await pg.goto("https://httpbin.org/response-headers?Set-Cookie=teste%3Dviagem%3B%20Max-Age%3D2592000%3B%20Path%3D%2F")
    await pg.goto("https://httpbin.org/cookies")
    cookie_ok = '"teste": "viagem"' in await pg.text_content("body")
    p2 = await ctx.new_page(); await p2.goto("https://example.com/")
    p3 = await ctx.new_page(); await p3.goto("https://httpbin.org/html")
    fp = await p3.evaluate(FP_JS)
    eid = await ext_id(ctx)
    for _ in range(3):
        n = await contador(ctx, eid)
    lista = await senhas(ctx, adicionar=True)
    await asyncio.sleep(3)  # deixa o Chromium gravar sessão e cookies
    raiz, nproc, mb = memoria(udd)
    await ctx.close()
    return {"tempo_abrir_s": t, "processos": nproc, "memoria_mb": mb, "raiz": raiz, "cookie": cookie_ok,
            "contador": n, "senhas": lista, "fp": h(fp), "fp_gpu": h(fp["gpu"]), "fp_canvas": h(fp["canvas"]),
            "fp_ua": h(fp["ua"])}


async def sessao2(udd, portatil, seed=SEED):
    ctx, t = await abrir(udd, portatil, seed)
    await asyncio.sleep(3)
    abas = sorted({pg.url for pg in ctx.pages if pg.url.startswith("http")})
    pg = await ctx.new_page()
    await pg.goto("https://httpbin.org/cookies")
    cookie_ok = '"teste": "viagem"' in await pg.text_content("body")
    fp = await pg.evaluate(FP_JS)
    eid = await ext_id(ctx)
    n = await contador(ctx, eid)
    lista = await senhas(ctx)
    raiz, nproc, mb = memoria(udd)
    await ctx.close()
    hist = sqlite3.connect(f"file:{udd}/Default/History?mode=ro", uri=True)
    urls = [r[0] for r in hist.execute("select url from urls")]
    hist.close()
    return {"tempo_abrir_s": t, "processos": nproc, "memoria_mb": mb, "abas": abas, "cookie": cookie_ok,
            "contador": n, "senhas": lista, "historico": len(urls),
            "historico_example": any("example.com" in u for u in urls),
            "fp": h(fp), "fp_gpu": h(fp["gpu"]), "fp_canvas": h(fp["canvas"]), "fp_ua": h(fp["ua"])}


def copiar(origem, destino):
    pula = shutil.ignore_patterns("Singleton*", "Cache", "Code Cache", "GPUCache", "last_screenshot.jpg")
    shutil.copytree(origem, destino, ignore=pula, symlinks=True)
    return round(sum(f.stat().st_size for f in Path(origem).rglob("*") if f.is_file()) / 2**20, 1), \
        round(sum(f.stat().st_size for f in Path(destino).rglob("*") if f.is_file()) / 2**20, 1)


async def main():
    res = {}
    for nome, portatil in (("normal", False), ("portatil", True)):
        a, b = BASE / f"perfil-{nome}", BASE / f"perfil-{nome}-copia"
        r = {"s1": await sessao1(a, portatil)}
        r["mb_pasta_e_copia"] = copiar(a, b)
        r["s2_copia"] = await sessao2(b, portatil)
        res[nome] = r
    res["outra_semente"] = await sessao2(BASE / "perfil-normal-copia", False, SEED_OUTRA)
    print(json.dumps(res, ensure_ascii=False, indent=1))

asyncio.run(main())
