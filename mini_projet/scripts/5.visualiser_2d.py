#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mini-projet — Étape 5 (optionnelle, oral) : visualisation 2D des occurrences.

Objectif
--------
Ce script produit une visualisation 2D (PNG) des occurrences d'un mot cible,
à partir des embeddings calculés à l'étape 3.

Cette étape est optionnelle : elle sert surtout à illustrer à l'oral si les
occurrences d'un mot forment (ou non) des groupes en fonction du contexte.

Méthode
-------
Par défaut : PCA 2D (rapide, simple).
Optionnel : UMAP 2D si le paquet `umap-learn` est installé.

Entrées (dans `--data_dir`)
---------------------------
- `embeddings_<model>.npy`
- `embeddings_meta.jsonl`
- (optionnel) `occurrences.jsonl` pour écrire quelques exemples de contexte

Sorties
-------
- un fichier PNG dans `--out_dir`
- (optionnel) un petit fichier texte avec 3–5 exemples de contexte

Exemple
-------
  python3 mini_projet/scripts/5.visualiser_2d.py \\
    --data_dir mini_projet/data \\
    --model camembert \\
    --target esprit \\
    --method pca \\
    --out_dir mini_projet/data/viz
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterator, List, Literal, Optional, Sequence, Tuple

ModelKey = Literal["camembert", "flaubert"]
MethodKey = Literal["pca", "umap"]


def parse_args() -> argparse.Namespace:
    """Lit les options de ligne de commande."""
    p = argparse.ArgumentParser(description="Visualisation 2D des occurrences (PCA/UMAP).")
    p.add_argument("--data_dir", type=str, default="mini_projet/data", help="Dossier des données.")
    p.add_argument("--model", type=str, required=True, choices=["camembert", "flaubert"], help="Modèle.")
    p.add_argument("--target", type=str, required=True, help="Mot cible à visualiser (ex: esprit).")
    p.add_argument(
        "--method",
        type=str,
        default="pca",
        choices=["pca", "umap"],
        help="Méthode de réduction en 2D.",
    )
    p.add_argument("--out_dir", type=str, default="mini_projet/data/viz", help="Dossier de sortie.")
    p.add_argument("--max_points", type=int, default=300, help="Limiter le nombre de points (lisibilité).")
    p.add_argument(
        "--write_examples",
        action="store_true",
        help="Écrire un petit fichier texte avec quelques contextes.",
    )
    return p.parse_args()


def iter_jsonl(path: Path) -> Iterator[Dict[str, Any]]:
    """Itère sur un fichier JSONL (1 objet JSON par ligne)."""
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def l2_normalize(mat: "Any") -> "Any":
    """Normalise chaque ligne d'une matrice (norme L2)."""
    import numpy as np  # type: ignore[import-not-found]

    eps = 1e-12
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    return mat / np.maximum(norms, eps)


def pca_2d(vectors: "Any") -> "Any":
    """
    PCA 2D avec NumPy (SVD).

    Entrée : (N, D)
    Sortie : (N, 2)
    """
    import numpy as np  # type: ignore[import-not-found]

    x = vectors.astype("float64", copy=False)
    x = x - np.mean(x, axis=0, keepdims=True)
    # SVD : x = U S Vt
    _, _, vt = np.linalg.svd(x, full_matrices=False)
    w = vt[:2].T  # (D, 2)
    return x @ w


def umap_2d(vectors: "Any") -> "Any":
    """UMAP 2D si disponible."""
    try:
        import umap  # type: ignore[import-not-found]
    except Exception as e:
        raise SystemExit(
            "UMAP demandé mais `umap-learn` n'est pas installé.\n"
            "Installez-le (par ex. `pip install umap-learn`) ou utilisez --method pca.\n"
            f"Détail : {e}"
        )
    reducer = umap.UMAP(n_components=2, random_state=42)
    return reducer.fit_transform(vectors)


def load_occurrence_contexts(path: Path) -> Dict[str, str]:
    """Charge un mapping occurrence_id -> context_text (si le fichier existe)."""
    if not path.exists():
        return {}
    out: Dict[str, str] = {}
    for obj in iter_jsonl(path):
        oid = str(obj.get("occurrence_id"))
        ctx = str(obj.get("context_text"))
        out[oid] = ctx
    return out


def main() -> None:
    args = parse_args()

    data_dir = Path(args.data_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    emb_path = data_dir / f"embeddings_{args.model}.npy"
    meta_path = data_dir / "embeddings_meta.jsonl"
    if not emb_path.exists():
        raise SystemExit(f"Fichier manquant : {emb_path}")
    if not meta_path.exists():
        raise SystemExit(f"Fichier manquant : {meta_path}")

    # On importe ici (et pas en haut du fichier) pour pouvoir afficher un message simple
    # si `numpy` ou `matplotlib` ne sont pas installés, au lieu d'une erreur Python brute.
    try:
        import numpy as np  # type: ignore[import-not-found]
        import matplotlib.pyplot as plt  # type: ignore[import-not-found]
    except Exception as e:  # pragma: no cover
        raise SystemExit(
            "Dépendances manquantes pour la visualisation.\n"
            "Installez au moins : numpy, matplotlib\n"
            f"Détail : {e}"
        )

    emb = np.load(emb_path)

    rows: List[int] = []
    occ_ids: List[str] = []
    for obj in iter_jsonl(meta_path):
        if str(obj.get("model")) != str(args.model):
            continue
        if str(obj.get("target")) != str(args.target):
            continue
        row = int(obj.get("row"))
        if 0 <= row < int(emb.shape[0]):
            rows.append(row)
            occ_ids.append(str(obj.get("occurrence_id")))

    if not rows:
        raise SystemExit(f"Aucune occurrence trouvée pour target={args.target!r}, model={args.model!r}")

    # Limiter le nombre de points pour la lisibilité.
    if len(rows) > int(args.max_points):
        rows = rows[: int(args.max_points)]
        occ_ids = occ_ids[: int(args.max_points)]

    vecs = emb[rows, :]
    vecs = l2_normalize(vecs)

    method: MethodKey = str(args.method)  # type: ignore[assignment]
    if method == "pca":
        xy = pca_2d(vecs)
    else:
        xy = umap_2d(vecs)

    title = f"{args.target} — {args.model} — {method.upper()} (N={xy.shape[0]})"
    out_png = out_dir / f"{args.model}_{args.target}_{method}.png"

    plt.figure(figsize=(7, 6))
    plt.scatter(xy[:, 0], xy[:, 1], s=18, alpha=0.85)
    plt.title(title)
    plt.xlabel("dim 1")
    plt.ylabel("dim 2")
    plt.tight_layout()
    plt.savefig(out_png, dpi=160)
    plt.close()
    print(f"écrit : {out_png}")

    if bool(args.write_examples):
        occ_path = data_dir / "occurrences.jsonl"
        contexts = load_occurrence_contexts(occ_path)
        out_txt = out_dir / f"{args.model}_{args.target}_{method}_examples.txt"

        # On prend les 5 premiers points.
        examples = occ_ids[:5]
        lines: List[str] = []
        for oid in examples:
            ctx = contexts.get(oid, "(contexte indisponible : occurrences.jsonl absent)")
            lines.append(f"- {oid}\n  {ctx}\n")

        out_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"écrit : {out_txt}")


if __name__ == "__main__":
    main()

