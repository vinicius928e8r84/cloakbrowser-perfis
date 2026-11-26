import os
import subprocess
import sys

from scripts.freios.contexto import Achado

ID = "testes"
TITULO = "Os testes dos freios passam (python -m unittest discover -s scripts/freios -t .)"
COMANDO = ["-m", "unittest", "discover", "-s", "scripts/freios", "-t", "."]
CONSERTO = "Rode python -m unittest discover -s scripts/freios -t . e conserte o teste que falha."
LINHAS_DA_SAIDA = 30


def ambiente_sem_git():
    return {nome: valor for nome, valor in os.environ.items() if not nome.startswith("GIT_")}


def verificar(ctx):
    resposta = subprocess.run(
        [sys.executable, *COMANDO],
        cwd=ctx.raiz, env=ambiente_sem_git(), capture_output=True, check=False,
    )
    if resposta.returncode == 0:
        return []
    saida = resposta.stderr.decode("utf-8", errors="replace").strip().splitlines()
    return [Achado(ID, "", "\n".join(saida[-LINHAS_DA_SAIDA:]))]
