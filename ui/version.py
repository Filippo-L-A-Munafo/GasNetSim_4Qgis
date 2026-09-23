# -*- coding: utf-8 -*-
"""Identificazione del plugin e del motore di calcolo.

Il numero di versione del plugin e quello del motore GasNetSim sono
**indipendenti**: il plugin dichiara il proprio in metadata.txt, mentre il
motore viene identificato a runtime, cosi' che ogni risultato porti con se'
quale codice lo ha prodotto.

Motivo del disaccoppiamento: il plugin usa un fork di GasNetSim con modifiche
non presenti in nessuna versione rilasciata a monte (compressori, schema
staggered, correzioni al solutore). La sola stringa di versione del motore
(0.2.2) non basta quindi a identificarlo: serve anche il commit del clone da
cui viene importato, che questo modulo legge direttamente dai file di .git
senza invocare processi esterni.
"""
import configparser
import os

_PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def plugin_version() -> str:
    """Versione del plugin, letta da metadata.txt."""
    try:
        cfg = configparser.ConfigParser()
        cfg.read(os.path.join(_PLUGIN_DIR, "metadata.txt"), encoding="utf-8")
        if cfg.has_section("general"):
            return cfg["general"].get("version", "?")
    except Exception:
        pass
    return "?"


def engine_version() -> str:
    """Versione del motore GasNetSim effettivamente installato."""
    try:
        from importlib.metadata import version as _v, PackageNotFoundError
        try:
            return str(_v("GasNetSim"))
        except PackageNotFoundError:
            pass
    except Exception:
        pass
    try:
        import GasNetSim
        v = getattr(GasNetSim, "__version__", None)
        if v:
            return str(v)
    except Exception:
        pass
    return "?"


def engine_path() -> str:
    """Cartella da cui il motore viene importato: identifica il fork in uso."""
    try:
        import GasNetSim
        return os.path.dirname(os.path.abspath(GasNetSim.__file__))
    except Exception:
        return ""


def _read_git_head(repo_dir):
    """(branch, commit) letti dai file di .git. (None, None) se non disponibili.

    Lettura diretta dei file invece di invocare `git`: il motore e' spesso
    installato in modalita' editabile da un clone, ma non e' detto che git sia
    raggiungibile dall'ambiente Python di QGIS.
    """
    git_dir = os.path.join(repo_dir, ".git")
    try:
        if os.path.isfile(git_dir):  # worktree: .git e' un file con 'gitdir: ...'
            with open(git_dir, "r", encoding="utf-8") as fh:
                line = fh.read().strip()
            if line.startswith("gitdir:"):
                git_dir = line.split(":", 1)[1].strip()
                if not os.path.isabs(git_dir):
                    git_dir = os.path.join(repo_dir, git_dir)
        if not os.path.isdir(git_dir):
            return None, None
        with open(os.path.join(git_dir, "HEAD"), "r", encoding="utf-8") as fh:
            head = fh.read().strip()
        if not head.startswith("ref:"):
            return None, head[:7] or None          # HEAD staccato
        ref = head.split(":", 1)[1].strip()
        # Il nome del branch puo' contenere barre (es. improvement/xyz):
        # si toglie il solo prefisso refs/heads/, non l'ultimo segmento.
        branch = (ref.split("refs/heads/", 1)[-1] if "refs/heads/" in ref
                  else ref.rsplit("/", 1)[-1])
        ref_path = os.path.join(git_dir, *ref.split("/"))
        if os.path.exists(ref_path):
            with open(ref_path, "r", encoding="utf-8") as fh:
                return branch, fh.read().strip()[:7]
        packed = os.path.join(git_dir, "packed-refs")
        if os.path.exists(packed):
            with open(packed, "r", encoding="utf-8") as fh:
                for row in fh:
                    if row.rstrip().endswith(" " + ref):
                        return branch, row.split(" ", 1)[0][:7]
        return branch, None
    except Exception:
        return None, None


def engine_commit():
    """(branch, commit) del clone da cui il motore e' importato, se ricavabili."""
    path = engine_path()
    for _ in range(4):                      # GasNetSim/ -> radice del repo
        if not path:
            break
        branch, commit = _read_git_head(path)
        if commit or branch:
            return branch, commit
        parent = os.path.dirname(path)
        if parent == path:
            break
        path = parent
    return None, None


def engine_id() -> str:
    """Identificazione compatta del motore: versione, branch e commit."""
    ver = engine_version()
    branch, commit = engine_commit()
    if branch and commit:
        return f"GasNetSim {ver} ({branch} @ {commit})"
    if commit:
        return f"GasNetSim {ver} (@ {commit})"
    return f"GasNetSim {ver}"


def build_stamp() -> str:
    """Riga unica che identifica il codice usato per un calcolo."""
    return f"GasNetSim_4Qgis {plugin_version()} · motore {engine_id()}"


def provenance(params=None, converged=None, iterations=None, elapsed_s=None):
    """Dizionario di provenienza, scritto in run_info.json accanto ai risultati.

    Contiene tutto cio' che serve a ripetere il calcolo: codice, parametri
    numerici e fisici, esito. I risultati restano cosi' attribuibili anche
    quando i CSV vengono spostati o rielaborati.
    """
    from datetime import datetime
    branch, commit = engine_commit()
    params = params or {}
    info = {
        "plugin": {
            "name": "GasNetSim_4Qgis",
            "version": plugin_version(),
        },
        "engine": {
            "name": "GasNetSim",
            "version": engine_version(),
            "branch": branch,
            "commit": commit,
            "path": engine_path(),
        },
        "run": {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "hour": params.get("ora"),
            "converged": converged,
            "iterations": iterations,
            "elapsed_s": round(elapsed_s, 2) if elapsed_s is not None else None,
        },
        "parameters": {
            "pressure_ref_bar": (params.get("pressure_pa") / 1e5
                                 if params.get("pressure_pa") else None),
            "temperature_k": params.get("temperature_k"),
            "roughness_m": params.get("roughness_m"),
            "junction_flow_sm3_s": params.get("junction_flow"),
            "placeholder_flow_sm3_s": params.get("placeholder_flow"),
            "max_iter": params.get("max_iter"),
            "tol_sm3_s": params.get("tol"),
            "urf": params.get("urf"),
            "autocalibrate": params.get("autocal"),
            "refine": params.get("refine"),
            "gas_composition": params.get("gas_comp"),
        },
    }
    return info
