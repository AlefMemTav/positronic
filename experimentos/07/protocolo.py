"""Guardas de execução e impressão digital do código do experimento 7."""
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
    fontes_congeladas = [
        ROOT / "ranhuras" / "__init__.py",
        ROOT / "experimentos" / "comum" / "legado.py",
        ROOT / "experimentos" / "06" / "modelos.py",
        ROOT / "requirements.txt",
    ]
    python_version = ROOT / ".python-version"
    if python_version.exists():
        fontes_congeladas.append(python_version)
    arquivos = sorted([
        *PASTA.rglob("*.py"), PASTA / "PREREGISTRO.md", *fontes_congeladas
    ])
    hashes = {}
    acumulado = hashlib.sha256()
    for arquivo in arquivos:
        relativo = arquivo.relative_to(ROOT).as_posix()
        conteudo = arquivo.read_bytes()
        digest = hashlib.sha256(conteudo).hexdigest()
        hashes[relativo] = digest
        acumulado.update(relativo.encode("utf-8"))
        acumulado.update(b"\0")
        acumulado.update(bytes.fromhex(digest))
    return {"sha256": acumulado.hexdigest(), "arquivos": hashes}


def exigir_arvore_limpa() -> str:
    status = _git("status", "--porcelain")
    if status:
        raise RuntimeError(
            "execução bloqueada: a árvore Git precisa estar limpa antes de iniciar"
        )
    return _git("rev-parse", "HEAD")


def carregar_configuracao(*, exigir_tracked: bool = True) -> dict:
    if not CONFIGURACAO.is_file():
        raise FileNotFoundError(f"configuração congelada ausente: {CONFIGURACAO}")
    if exigir_tracked:
        _git("ls-files", "--error-unmatch", CONFIGURACAO.relative_to(ROOT).as_posix())
    config = json.loads(CONFIGURACAO.read_text(encoding="utf-8"))
    if config.get("experimento") != "07-heterocedasticidade":
        raise ValueError("configuração congelada pertence a outro experimento")
    if not config.get("executavel_confirmatorio"):
        raise RuntimeError("gate de margem falhou; teste confirmatório não pode ser aberto")
    if config.get("fingerprint_codigo") != codigo_fingerprint():
        raise RuntimeError("código ou pré-registro mudou após a calibração")
    commit_calibracao = config.get("git", {}).get("commit")
    if not commit_calibracao:
        raise RuntimeError("configuração não registra o commit usado na calibração")
    subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit_calibracao, "HEAD"],
        cwd=ROOT, check=True, capture_output=True,
    )
    return config


def exigir_registro_primario_commitado() -> None:
    candidatos = sorted(REGISTROS.glob("07-primario-*.json"))
    if not candidatos:
        raise RuntimeError("a análise primária ainda não foi registrada")
    resumo_primario = None
    for arquivo in candidatos:
        try:
            conteudo = json.loads(arquivo.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if conteudo.get("experimento") != "07-primario":
            continue
        resultado = subprocess.run(
            ["git", "ls-files", "--error-unmatch", arquivo.relative_to(ROOT).as_posix()],
            cwd=ROOT, capture_output=True, text=True,
        )
        if resultado.returncode == 0:
            resumo_primario = conteudo
            break
    if resumo_primario is None:
        raise RuntimeError("registre e versione o resumo primário antes da grade exploratória")
    config = json.loads(CONFIGURACAO.read_text(encoding="utf-8"))
    n_esperado = int(config["dimensionamento_teste"]["n"])
    seeds = resumo_primario.get("sementes", {}).get("teste", [])
    deltas = resumo_primario.get("metricas_por_semente", {}).get("delta_pareado", [])
    if len(seeds) != n_esperado or len(deltas) != n_esperado:
        raise RuntimeError("o resumo primário commitado está incompleto")
