#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mini-projet — Étape 4 : score de polysémie à partir des embeddings.

Objectif
--------
Ce script lit les embeddings calculés à l'étape 3 et calcule, pour chaque mot cible,
un score de polysémie basé sur la dispersion des similarités cosinus entre occurrences
du même mot.

Définition du score (simple)
----------------------------
Pour un mot donné, on considère toutes les paires d'occurrences (i < j).
On calcule la similarité cosinus entre leurs vecteurs, puis on prend l'écart-type
de ces cosinus :
  score = std( cos(v_i, v_j) )

Plus le score est grand, plus les occurrences ont tendance à être « dispersées »,
ce qui peut correspondre à une plus grande variété de sens en contexte.

Entrées
-------
Dans `--data_dir` (par défaut `mini_projet/data`) :
- `embeddings_camembert.npy` (optionnel)
- `embeddings_flaubert.npy`  (optionnel)
- `embeddings_meta.jsonl`    (obligatoire)

Sorties
-------
- `polysemy_scores.json` : scores par modèle et par mot
- `polysemy_ranking.json` : liste des mots triés par score (par modèle)

Exemple
-------
Depuis la racine :
  python3 mini_projet/scripts/4.score_polysemie.py --data_dir mini_projet/data
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Literal, Mapping, Optional, Sequence, Tuple

ModelKey = Literal["camembert", "flaubert"]


def parse_args() -> argparse.Namespace:
    """Lit les options de ligne de commande."""
    p = argparse.ArgumentParser(description="Calculer un score de polysémie à partir des embeddings.")
    p.add_argument(
        "--data_dir",
        type=str,
        default="mini_projet/data",
        help="Dossier contenant embeddings_*.npy et embeddings_meta.jsonl.",
    )
    p.add_argument(
        "--models",
        nargs="+",
        default=["camembert", "flaubert"],
        choices=["camembert", "flaubert"],
        help="Modèles à traiter (on ignore ceux dont les fichiers manquent).",
    )
    p.add_argument(
        "--out_scores",
        type=str,
        default="polysemy_scores.json",
        help="Nom du fichier de sortie (scores).",
    )
    p.add_argument(
        "--out_ranking",
        type=str,
        default="polysemy_ranking.json",
        help="Nom du fichier de sortie (classement).",
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


def write_json(path: Path, obj: Mapping[str, Any]) -> None:
    """Écrit un JSON lisible (indenté)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(obj), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def l2_normalize(mat: "Any") -> "Any":
    """Normalise chaque ligne d'une matrice (norme L2)."""
    import numpy as np

    eps = 1e-12
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    return mat / np.maximum(norms, eps)


def cosine_pairwise_stats(vectors: "Any") -> Dict[str, Optional[float]]:
    """
    Calcule des statistiques sur les cosinus 2-à-2 (i<j) pour un ensemble de vecteurs.

    Retourne un dict avec mean/std/min/max. Si N < 2, toutes les valeurs sont nulles.
    """
    import numpy as np

    n = int(vectors.shape[0])
    if n < 2:
        return {"cosine_mean": None, "cosine_std": None, "cosine_min": None, "cosine_max": None}

    v = l2_normalize(vectors.astype("float64", copy=False))
    sim = v @ v.T  # cosinus (car vecteurs normalisés)
    iu = np.triu_indices(n, k=1)
    vals = sim[iu]

    return {
        "cosine_mean": float(np.mean(vals)),
        "cosine_std": float(np.std(vals)),
        "cosine_min": float(np.min(vals)),
        "cosine_max": float(np.max(vals)),
    }


def load_embeddings(data_dir: Path, model: ModelKey) -> Optional["Any"]:
    """Charge un fichier embeddings_<model>.npy si présent, sinon None."""
    import numpy as np

    path = data_dir / f"embeddings_{model}.npy"
    if not path.exists():
        return None
    return np.load(path)


def group_rows_by_target(meta_path: Path, model: ModelKey) -> Dict[str, List[int]]:
    """Construit un mapping target -> liste des indices de lignes dans la matrice d'embeddings."""
    groups: Dict[str, List[int]] = {}
    for obj in iter_jsonl(meta_path):
        if str(obj.get("model")) != model:
            continue
        target = str(obj.get("target"))
        row = int(obj.get("row"))
        groups.setdefault(target, []).append(row)
    return groups


def main() -> None:
    args = parse_args()

    data_dir = Path(args.data_dir)
    meta_path = data_dir / "embeddings_meta.jsonl"
    if not meta_path.exists():
        raise SystemExit(f"Fichier manquant : {meta_path}")

    scores_out: Dict[str, Any] = {"data_dir": str(data_dir), "models": {}}
    ranking_out: Dict[str, Any] = {"data_dir": str(data_dir), "models": {}}

    for model in list(args.models):
        emb = load_embeddings(data_dir, model)  # type: ignore[arg-type]
        if emb is None:
            print(f"[{model}] ignoré : embeddings_{model}.npy absent")
            continue

        groups = group_rows_by_target(meta_path, model)  # type: ignore[arg-type]
        model_scores: Dict[str, Any] = {}

        for target, rows in sorted(groups.items(), key=lambda kv: kv[0]):
            # Sécurité : on garde seulement les indices valides.
            rows_ok = [r for r in rows if 0 <= r < int(emb.shape[0])]
            vecs = emb[rows_ok, :]
            stats = cosine_pairwise_stats(vecs)
            model_scores[target] = {"n_occurrences": int(vecs.shape[0]), **stats}

        # Classement : score = cosine_std, en ignorant les valeurs nulles.
        items: List[Tuple[str, float]] = []
        for t, d in model_scores.items():
            s = d.get("cosine_std")
            if s is None:
                continue
            items.append((t, float(s)))
        items.sort(key=lambda x: x[1], reverse=True)

        scores_out["models"][model] = model_scores
        ranking_out["models"][model] = [{"target": t, "score": s} for t, s in items]

        print(f"[{model}] targets={len(model_scores)}  classés={len(items)}")

    write_json(data_dir / str(args.out_scores), scores_out)
    write_json(data_dir / str(args.out_ranking), ranking_out)
    print("OK")


if __name__ == "__main__":
    main()

