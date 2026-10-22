"""Fingerprint e guardas de rastreabilidade do experimento 8."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]
PASTA = Path(__file__).resolve().parent
CONFIGURACAO = PASTA / "configuracao-congelada.json"
REGISTROS = ROOT / "resultados" / "execucoes"


def _git(*argumentos: str) -> str:
    return subprocess.run(
        ["git", *argumentos], cwd=ROOT, check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def codigo_fingerprint() -> dict:
    fontes = [
        ROOT / "ranhuras" / "__init__.py",
        ROOT / "experimentos" / "comum" / "legado.py",
        ROOT / "docs" / "protocolo.md",
        ROOT / "docs" / "04-proximos-passos.md",
        ROOT / "requirements.txt",
        PASTA / "PREREGISTRO.md",
        *PASTA.glob("*.py"),
    ]
    hashes = {}
    acumulado = hashlib.sha256()
    for arquivo in sorted(set(fontes)):
        relativo = arquivo.relative_to(ROOT).as_posix()
        digest = hashlib.sha256(arquivo.read_bytes()).hexdigest()
        hashes[relativo] = digest
        acumulado.update(relativo.encode("utf-8"))
        acumulado.update(b"\0")
        acumulado.update(bytes.fromhex(digest))
    return {"sha256": acumulado.hexdigest(), "arquivos": hashes}


def exigir_arvore_limpa() -> str:
    if _git("status", "--porcelain"):
        raise RuntimeError("a execução exige árvore Git limpa")
    return _git("rev-parse", "HEAD")


def carregar_configuracao() -> dict:
    if not CONFIGURACAO.is_file():
        raise FileNotFoundError("execute e versione a calibração antes do teste")
    _git("ls-files", "--error-unmatch",
         CONFIGURACAO.relative_to(ROOT).as_posix())
    config = json.loads(CONFIGURACAO.read_text(encoding="utf-8"))
    if config.get("experimento") != "08-retorno-rapido":
        raise ValueError("configuração pertence a outro experimento")
    if not config.get("executavel_confirmatorio"):
        raise RuntimeError("calibração não autorizou execução confirmatória")
    if config.get("fingerprint_codigo") != codigo_fingerprint():
        raise RuntimeError("código ou protocolo mudou após a calibração")
    commit = config.get("git", {}).get("commit")
    if not commit:
        raise RuntimeError("configuração não registra o commit de calibração")
    subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit, "HEAD"],
        cwd=ROOT, check=True, capture_output=True,
    )
    return config
