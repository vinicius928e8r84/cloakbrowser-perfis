import ast
import re
from pathlib import Path

from scripts.freios.contexto import Achado

ID = "depuracao"
TITULO = "Nenhum print() nem console.log esquecido no código"
CONSERTO = (
    "Apague o print() ou o console.log: era depuração. Se o arquivo Python é um script de linha de comando e imprimir é o "
    "trabalho dele, dê a ele o ponto de entrada (if __name__ == \"__main__\":), que o libera. "
    "Um arquivo que imprime de propósito sem ter ponto de entrada (todo arquivo JS ou TS que usa console.log) entra em "
    "scripts/freios/excecoes.json, categoria depuracao, com o motivo, só por PR revisada pelo dono. "
    "console.warn, console.error, console.info e console.debug não são barrados. "
    "Só o print() e o console.log novos reprovam: o que já estava na main fica no teto dela."
)
BOM = "﻿"
EXTENSOES_JS = {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".mts"}
CONSOLE_LOG = re.compile(r"(?<![\w$.])console\s*\.\s*log\s*\(")


def _e_a_guarda(no):
    if not isinstance(no, ast.If) or not isinstance(no.test, ast.Compare):
        return False
    teste = no.test
    pontas = [teste.left, *teste.comparators]
    nomes = [p.id for p in pontas if isinstance(p, ast.Name)]
    textos = [p.value for p in pontas if isinstance(p, ast.Constant)]
    return len(teste.ops) == 1 and isinstance(teste.ops[0], ast.Eq) and nomes == ["__name__"] and textos == ["__main__"]


def _e_print(no):
    return isinstance(no, ast.Call) and isinstance(no.func, ast.Name) and no.func.id == "print"


def _linhas_dos_prints(texto, caminho):
    try:
        arvore = ast.parse(texto.lstrip(BOM), caminho)
    except (SyntaxError, ValueError):
        return []
    if any(_e_a_guarda(no) for no in arvore.body):
        return []
    return sorted(no.lineno for no in ast.walk(arvore) if _e_print(no))


def _linhas_dos_console_log(texto):
    return [numero for numero, linha in enumerate(texto.split("\n"), start=1) for _ in CONSOLE_LOG.finditer(linha)]


def _achados_do_arquivo(caminho, texto):
    if Path(caminho).suffix.lower() == ".py":
        return [Achado(ID, caminho, "print() esquecido", linha) for linha in _linhas_dos_prints(texto, caminho)]
    return [Achado(ID, caminho, "console.log esquecido", linha) for linha in _linhas_dos_console_log(texto)]


def verificar(ctx):
    achados = []
    for entrada in ctx.entradas_com_extensao({".py"} | EXTENSOES_JS):
        if ctx.excecao(ID, entrada.caminho):
            continue
        texto = ctx.texto(entrada)
        if texto is not None:
            achados += _achados_do_arquivo(entrada.caminho, texto)
    return achados
