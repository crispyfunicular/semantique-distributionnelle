#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Étape 6 : corrélation avec une mesure externe de polysémie.

Objectif
--------
Ce script compare le score de dispersion obtenu avec CamemBERT (`cosine_std`)
à une mesure externe de polysémie fondée sur des macro-sens.

Entrées
-------
Dans `--data_dir` :
- `polysemy_scores.json` : scores calculés à partir des embeddings ;
- `external_polysemy_scores.csv` : mesure externe de polysémie.

Sortie
------
- `correlation_polysemie_<model>.csv` : tableau fusionnant les scores BERT
  et la mesure externe.

Exemple
-------
Depuis la racine du dossier `mini_projet` :
  python scripts/6.correlation_externe.py --data_dir data_final --model camembert
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from scipy.stats import pearsonr, spearmanr


def parse_args() -> argparse.Namespace:
    """
    Lit les options de ligne de commande.
    """
    parser = argparse.ArgumentParser(
        description="Corréler le score de dispersion BERT avec une mesure externe de polysémie."
    )
    parser.add_argument(
        "--data_dir",
        type=str,
        default="data_final",
        help="Dossier contenant les fichiers de scores et la mesure externe.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="camembert",
        choices=["camembert", "flaubert"],
        help="Modèle à analyser.",
    )
    parser.add_argument(
        "--external",
        type=str,
        default="external_polysemy_scores.csv",
        help="Nom du fichier CSV contenant la mesure externe.",
    )
    return parser.parse_args()


def load_bert_scores(path: Path, model: str) -> pd.DataFrame:
    """
    Charge les scores de polysémie calculés à partir des embeddings.

    On extrait principalement :
    - target : mot cible ;
    - n_occurrences : nombre d'occurrences utilisées ;
    - cosine_std : score de dispersion retenu.
    """
    with path.open("r", encoding="utf-8") as f:
        scores: Dict[str, Any] = json.load(f)

    if model not in scores["models"]:
        raise SystemExit(f"Modèle absent dans {path} : {model}")

    rows: List[Dict[str, Any]] = []

    for target, values in scores["models"][model].items():
        rows.append(
            {
                "target": target,
                "n_occurrences": values["n_occurrences"],
                "cosine_mean": values["cosine_mean"],
                "cosine_std": values["cosine_std"],
                "cosine_min": values["cosine_min"],
                "cosine_max": values["cosine_max"],
            }
        )

    return pd.DataFrame(rows)


def main() -> None:
    """
    Lance la corrélation entre le score BERT et la mesure externe.
    """
    args = parse_args()

    data_dir = Path(args.data_dir)
    scores_path = data_dir / "polysemy_scores.json"
    external_path = data_dir / str(args.external)

    if not scores_path.exists():
        raise SystemExit(f"Fichier manquant : {scores_path}")

    if not external_path.exists():
        raise SystemExit(f"Fichier manquant : {external_path}")

    # Chargement des deux sources de scores.
    df_bert = load_bert_scores(scores_path, str(args.model))
    df_external = pd.read_csv(external_path)

    # Vérification minimale du fichier externe.
    required_columns = {"target", "score_externe"}
    missing_columns = required_columns - set(df_external.columns)

    if missing_columns:
        raise SystemExit(
            f"Colonnes manquantes dans {external_path} : {sorted(missing_columns)}"
        )

    # Fusion des scores BERT et des scores externes.
    df = df_bert.merge(df_external, on="target", how="inner")

    if len(df) < 3:
        raise SystemExit(
            f"Trop peu de mots communs pour calculer une corrélation : n={len(df)}"
        )

    # Calcul des corrélations.
    spearman = spearmanr(df["cosine_std"], df["score_externe"])
    pearson = pearsonr(df["cosine_std"], df["score_externe"])

    # Ajout des rangs pour faciliter l'interprétation.
    df["rang_bert"] = df["cosine_std"].rank(ascending=False, method="min").astype(int)
    df["rang_externe"] = df["score_externe"].rank(ascending=False, method="min").astype(int)

    df = df.sort_values("cosine_std", ascending=False)

    # Écriture du tableau final.
    out_path = data_dir / f"correlation_polysemie_{args.model}.csv"
    df.to_csv(out_path, index=False, encoding="utf-8")

    # Affichage terminal.
    columns_to_print = [
        "target",
        "n_occurrences",
        "cosine_std",
        "score_externe",
        "rang_bert",
        "rang_externe",
    ]

    if "commentaire" in df.columns:
        columns_to_print.append("commentaire")

    print(df[columns_to_print].to_string(index=False))
    print()
    print(f"Spearman rho = {spearman.statistic:.3f}, p-value = {spearman.pvalue:.4f}")
    print(f"Pearson r    = {pearson.statistic:.3f}, p-value = {pearson.pvalue:.4f}")
    print()
    print(f"Fichier écrit : {out_path}")


if __name__ == "__main__":
    main()