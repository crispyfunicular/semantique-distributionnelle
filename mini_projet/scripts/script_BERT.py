#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Extraction d'occurrences et de leur contexte (fenêtre de mots).

Ce script :
- cherche des mots cibles dans un corpus,
- garde k mots à gauche et k mots à droite, -> à définir
- prend au plus N exemples par mot (toujours les mêmes si on garde la même seed),
- écrit les résultats dans un fichier `occurrences.jsonl` (une occurrence par ligne).

Ensuite, un autre script pourra lire ce fichier pour calculer des vecteurs avec
CamemBERT et FlauBERT sur exactement les mêmes occurrences.

Utilisation depuis la racine : python3 mini_projet/scripts/script_BERT.py --targets esprit or courir porte --k 10 --n 30
"""

from __future__ import annotations

# Lecture des options en ligne de commande (ex: --k, --n, --targets).
import argparse

# Créer un identifiant court et stable pour chaque occurrence.
import hashlib

# Écrire les résultats dans des fichiers JSON / JSONL.
import json

# Tirer au hasard des occurrences, de façon reproductible avec une seed.
import random

# Tokeniser le texte avec une expression régulière.
import re

# Normaliser le texte (variantes Unicode, apostrophes, minuscules).
import unicodedata

# Définir un objet Occurrence et le convertir facilement en dict.
from dataclasses import asdict, dataclass

# Manipuler des chemins de fichiers sans dépendre du système.
from pathlib import Path

# Types Python (lisibilité + aide à éviter des erreurs).
from typing import Any, Dict, Iterable, Iterator, List, Mapping, Sequence


# Mot “simple” pour le français (accents, apostrophes, tirets).
_WORD_RE: re.Pattern[str] = re.compile(
    r"[a-zA-ZÀ-ÖØ-öø-ÿœŒæÆ]+(?:[’'][a-zA-ZÀ-ÖØ-öø-ÿœŒæÆ]+)?(?:-[a-zA-ZÀ-ÖØ-öø-ÿœŒæÆ]+)*"
)


@dataclass(frozen=True)
class Occurrence:
    """
    Une occurrence d'un mot cible avec son contexte.

    Champs :
    - occurrence_id : identifiant stable
    - target : mot cible (normalisé)
    - doc_id : identifiant du document (souvent le nom du fichier sans extension)
    - token_index : position du mot cible dans la liste `tokens`
    - left_context_tokens : jusqu'à k mots à gauche
    - target_token : le mot trouvé dans le corpus
    - right_context_tokens : jusqu'à k mots à droite
    - context_text : texte reconstruit (gauche + cible + droite)
    """

    occurrence_id: str
    target: str
    doc_id: str
    token_index: int
    left_context_tokens: List[str]
    target_token: str
    right_context_tokens: List[str]
    context_text: str


def normalize_text(text: str) -> str:
    """
    Normalise un texte pour faciliter la comparaison.

    Règles (simples et utiles) :
    - normalisation Unicode (NFKC)
    - minuscules
    - apostrophe typographique → apostrophe simple
    """
    normalized: str = unicodedata.normalize("NFKC", text)
    normalized = normalized.replace("’", "'")
    return normalized.lower()


def tokenize_words(text: str) -> List[str]:
    """
    Découpe un texte en une liste de mots.

    La tokenisation est volontairement basique et stable.
    """
    clean: str = normalize_text(text)
    return _WORD_RE.findall(clean)


def read_text_file(path: Path) -> str:
    """
    Lit un fichier texte en UTF-8.

    Si certains caractères posent problème, ils sont remplacés pour éviter un crash.
    """
    return path.read_text(encoding="utf-8", errors="replace")


def make_occurrence_id(doc_id: str, target: str, token_index: int, context_text: str) -> str:
    """
    Construit un identifiant stable pour une occurrence.

    On inclut :
    - doc_id, target, token_index
    - un petit hash du contexte (pour limiter les collisions)
    """
    digest: str = hashlib.sha1(context_text.encode("utf-8")).hexdigest()[:12]
    return f"{doc_id}:{target}:{token_index}:{digest}"


def iter_candidate_positions(tokens: Sequence[str], target: str) -> Iterator[int]:
    """
    Renvoie les positions où `tokens[i] == target`.

    `tokens` et `target` doivent être normalisés de la même façon.
    """
    for i, tok in enumerate(tokens):
        if tok == target:
            yield i


def build_occurrence(tokens: Sequence[str], doc_id: str, target: str, index: int, k: int) -> Occurrence:
    """
    Construit une occurrence à partir d'une position `index` dans `tokens`.

    La fenêtre est : k mots à gauche et k mots à droite.
    """
    # Contexte gauche
    left_start: int = max(0, index - k)
    left: List[str] = list(tokens[left_start:index])

    # Mot cible
    target_token: str = tokens[index]

    # Contexte droit
    right_end: int = min(len(tokens), index + 1 + k)
    right: List[str] = list(tokens[index + 1 : right_end])

    # Texte de contexte reconstruit (stable, pas forcément identique au texte d'origine)
    context_tokens: List[str] = left + [target_token] + right
    context_text: str = " ".join(context_tokens)

    occurrence_id: str = make_occurrence_id(
        doc_id=doc_id, target=target, token_index=index, context_text=context_text
    )

    return Occurrence(
        occurrence_id=occurrence_id,
        target=target,
        doc_id=doc_id,
        token_index=index,
        left_context_tokens=left,
        target_token=target_token,
        right_context_tokens=right,
        context_text=context_text,
    )


def sample_occurrences_for_target(
    tokens: Sequence[str],
    doc_id: str,
    raw_target: str,
    k: int,
    n_samples: int,
    rng: random.Random,
) -> List[Occurrence]:
    """
    Extrait des occurrences pour un mot cible, puis en sélectionne au plus `n_samples`.

    - si le mot apparaît moins de `n_samples` fois : on garde tout
    - l'échantillonnage est reproductible grâce à `rng`
    """
    target: str = normalize_text(raw_target)
    positions: List[int] = list(iter_candidate_positions(tokens, target))

    if not positions:
        return []

    # On choisit des positions au hasard, sans modifier le corpus.
    if len(positions) > n_samples:
        positions = rng.sample(positions, k=n_samples)

    occurrences: List[Occurrence] = [build_occurrence(tokens, doc_id, target, i, k) for i in positions]

    # Trier rend les fichiers plus faciles à relire (sans changer le contenu).
    occurrences.sort(key=lambda o: o.token_index)
    return occurrences


def write_jsonl(path: Path, items: Iterable[Mapping[str, Any]]) -> None:
    """
    Écrit un fichier JSONL : une ligne = un objet JSON.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for obj in items:
            f.write(json.dumps(dict(obj), ensure_ascii=False) + "\n")


def write_json(path: Path, obj: Mapping[str, Any]) -> None:
    """
    Écrit un fichier JSON lisible (indenté).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(obj), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    """
    Lit les options de ligne de commande.
    """
    parser = argparse.ArgumentParser(
        description="Extraire des occurrences de mots cibles avec une fenêtre de contexte (k mots à gauche/droite)."
    )
    parser.add_argument(
        "--corpus",
        type=str,
        default="mini_projet/corpus_complet.txt",
        help="Chemin vers le corpus (texte).",
    )
    parser.add_argument(
        "--targets",
        type=str,
        nargs="+",
        required=True,
        help="Mots cibles (ex: esprit or courir porte).",
    )
    parser.add_argument(
        "--k",
        type=int,
        default=10,
        help="Taille de la fenêtre : k mots à gauche et k mots à droite.",
    )
    parser.add_argument(
        "--n",
        type=int,
        default=30,
        help="Nombre d'exemples max par mot cible.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Graine aléatoire (pour refaire exactement le même tirage).",
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        default="mini_projet/data",
        help="Dossier de sortie.",
    )
    return parser.parse_args()


def main() -> None:
    """
    Lance l'extraction et écrit les fichiers de sortie.
    """
    args: argparse.Namespace = parse_args()

    corpus_path: Path = Path(args.corpus)
    out_dir: Path = Path(args.out_dir)

    # doc_id sert dans les identifiants d'occurrences (utile si un jour vous avez plusieurs fichiers).
    doc_id: str = corpus_path.stem

    # Lecture + tokenisation.
    text: str = read_text_file(corpus_path)
    tokens: List[str] = tokenize_words(text)

    # Tirage reproductible (même seed → même échantillon).
    rng: random.Random = random.Random(int(args.seed))

    all_occurrences: List[Occurrence] = []
    summary: Dict[str, Dict[str, int]] = {}

    # On traite chaque mot cible indépendamment.
    for raw_target in list(args.targets):
        occs: List[Occurrence] = sample_occurrences_for_target(
            tokens=tokens,
            doc_id=doc_id,
            raw_target=raw_target,
            k=int(args.k),
            n_samples=int(args.n),
            rng=rng,
        )
        all_occurrences.extend(occs)
        summary[normalize_text(raw_target)] = {"requested": int(args.n), "extracted": len(occs)}

    # Écriture des fichiers.
    occurrences_path: Path = out_dir / "occurrences.jsonl"
    targets_path: Path = out_dir / "targets.json"

    write_jsonl(occurrences_path, (asdict(o) for o in all_occurrences))
    write_json(
        targets_path,
        {
            "corpus": str(corpus_path),
            "doc_id": doc_id,
            "k": int(args.k),
            "n_per_target": int(args.n),
            "seed": int(args.seed),
            "targets_raw": list(args.targets),
            "targets_normalized": [normalize_text(t) for t in list(args.targets)],
            "summary": summary,
            "notes": [
                "Tokenisation simple (mots) + minuscules + normalisation Unicode.",
                "Fenêtre : k mots à gauche et k mots à droite.",
                "Sortie : occurrences.jsonl (1 occurrence par ligne).",
            ],
        },
    )

    # Petit récap en sortie standard (pratique quand on lance le script).
    print(f"Corpus : {corpus_path} -> {len(tokens)} mots (tokenisation simple)")
    print("Sorties :")
    print(f"- {occurrences_path} ({len(all_occurrences)} occurrences)")
    print(f"- {targets_path}")
    print("Récap :")
    for t, info in summary.items():
        print(f"- {t} : {info['extracted']} / {info['requested']}")


if __name__ == "__main__":
    main()

