#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mini-projet — Étape 3 : encoder des occurrences avec des modèles BERT.

Objectif
--------
À partir du fichier `mini_projet/data/occurrences.jsonl` (étape 2), ce script calcule
un vecteur par occurrence avec :
- CamemBERT
- FlauBERT

Le vecteur d'une occurrence correspond au mot cible dans son contexte :
on prend la moyenne des vecteurs des sous-tokens qui composent ce mot.

Sorties
-------
Dans `--out_dir` (par défaut `mini_projet/data`) :
- `embeddings_camembert.npy` : matrice (N_occurrences, dim)
- `embeddings_flaubert.npy`  : matrice (N_occurrences, dim)
- `embeddings_meta.jsonl`    : une ligne par occurrence et par modèle (mapping vers la ligne du .npy)

Pré-requis
----------
Ce script utilise HuggingFace Transformers + PyTorch + NumPy.
Installation typique (à adapter à votre environnement) :
  pip install transformers torch numpy

Exemple
-------
Depuis la racine du dépôt :
  python3 mini_projet/scripts/3.encoder_embeddings.py \\
    --occurrences mini_projet/data/occurrences.jsonl \\
    --out_dir mini_projet/data \\
    --models camembert flaubert \\
    --batch_size 16 \\
    --device auto
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Literal, Mapping, Sequence, Tuple


ModelKey = Literal["camembert", "flaubert"]


@dataclass(frozen=True)
class OccurrenceRecord:
    """Données minimales nécessaires pour encoder une occurrence."""

    occurrence_id: str
    target: str
    left_context_tokens: List[str]
    target_token: str
    right_context_tokens: List[str]
    context_text: str

    @property
    def tokens(self) -> List[str]:
        """Tokens du contexte (gauche + cible + droite), dans l'ordre."""
        return list(self.left_context_tokens) + [self.target_token] + list(self.right_context_tokens)

    @property
    def target_word_index(self) -> int:
        """Index (en mots) du mot cible dans `tokens`."""
        return len(self.left_context_tokens)


def parse_args() -> argparse.Namespace:
    """Lit les options de ligne de commande."""
    p = argparse.ArgumentParser(
        description="Encoder des occurrences (mots en contexte) avec CamemBERT/FlauBERT."
    )
    p.add_argument(
        "--occurrences",
        type=str,
        default="mini_projet/data/occurrences.jsonl",
        help="Chemin vers le fichier occurrences.jsonl (étape 2).",
    )
    p.add_argument(
        "--out_dir",
        type=str,
        default="mini_projet/data",
        help="Dossier de sortie.",
    )
    p.add_argument(
        "--models",
        nargs="+",
        default=["camembert", "flaubert"],
        choices=["camembert", "flaubert"],
        help="Modèles à utiliser.",
    )
    p.add_argument(
        "--batch_size",
        type=int,
        default=16,
        help="Taille des batchs (plus grand = plus rapide, mais plus de mémoire).",
    )
    p.add_argument(
        "--device",
        type=str,
        default="auto",
        choices=["auto", "cpu", "cuda"],
        help="Où calculer : cpu, cuda, ou auto.",
    )
    p.add_argument(
        "--max_length",
        type=int,
        default=256,
        help="Longueur max en sous-tokens (sécurité).",
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


def read_occurrences(path: Path) -> List[OccurrenceRecord]:
    """Charge les occurrences du JSONL en objets Python."""
    items: List[OccurrenceRecord] = []
    for obj in iter_jsonl(path):
        items.append(
            OccurrenceRecord(
                occurrence_id=str(obj["occurrence_id"]),
                target=str(obj["target"]),
                left_context_tokens=list(obj["left_context_tokens"]),
                target_token=str(obj["target_token"]),
                right_context_tokens=list(obj["right_context_tokens"]),
                context_text=str(obj["context_text"]),
            )
        )
    return items


def chunked(items: Sequence[OccurrenceRecord], batch_size: int) -> Iterator[List[OccurrenceRecord]]:
    """Découpe une liste en batchs de taille `batch_size`."""
    for i in range(0, len(items), batch_size):
        yield list(items[i : i + batch_size])


def pick_device(device_choice: str) -> str:
    """Choisit un device PyTorch."""
    if device_choice in {"cpu", "cuda"}:
        return device_choice
    # auto
    try:
        import torch

        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"


def get_model_specs() -> Dict[ModelKey, str]:
    """
    Noms HuggingFace des modèles.

    Remarque : vous pouvez remplacer ces noms par d'autres variantes si besoin.
    """
    return {
        "camembert": "camembert-base",
        "flaubert": "flaubert/flaubert_base_cased",
    }


def build_subtokens_with_word_mapping(
    tokenizer: Any, words: Sequence[str]
) -> Tuple[List[int], List[int], List[List[int]]]:
    """
    Tokenise une liste de mots et construit un mapping mot -> positions de sous-tokens.

    Pourquoi cette fonction ?
    - Les tokenizers ne donnent pas toujours un alignement simple mot <-> sous-tokens.
    - Ici, notre contexte est reconstruit avec des espaces, donc on peut imiter cela :
      on tokenise chaque mot, en ajoutant un espace avant (sauf le premier).

    Sorties
    -------
    - input_ids : ids sans tokens spéciaux
    - attention_mask : 1 pour chaque id
    - word_to_positions : pour chaque mot i, la liste des positions (dans la séquence sans spéciaux)
    """
    all_ids: List[int] = []
    word_to_positions: List[List[int]] = []

    for i, w in enumerate(words):
        piece: str = w if i == 0 else f" {w}"
        subtoks: List[str] = tokenizer.tokenize(piece)
        sub_ids: List[int] = tokenizer.convert_tokens_to_ids(subtoks)
        start: int = len(all_ids)
        all_ids.extend(sub_ids)
        positions: List[int] = list(range(start, start + len(sub_ids)))
        word_to_positions.append(positions)

    attn: List[int] = [1] * len(all_ids)
    return all_ids, attn, word_to_positions


def add_special_tokens(
    tokenizer: Any, input_ids: List[int], attention_mask: List[int]
) -> Tuple[List[int], List[int], int]:
    """
    Ajoute les tokens spéciaux du modèle (début/fin de séquence).

    On retourne aussi `shift` : combien de tokens spéciaux sont ajoutés au début,
    pour pouvoir décaler les positions des sous-tokens du mot cible.
    """
    # Dans la pratique, CamemBERT/FlauBERT ajoutent un token au début et un à la fin.
    # Certaines versions de transformers/tokenizers n'exposent pas la même API, donc
    # on prévoit plusieurs chemins de compatibilité.
    built: List[int]
    shift: int

    # 1) API "classique"
    fn = getattr(tokenizer, "build_inputs_with_special_tokens", None)
    if callable(fn):
        try:
            built = fn(input_ids)  # type: ignore[misc]
        except TypeError:
            # Certaines implémentations attendent (token_ids_0, token_ids_1=None)
            built = fn(input_ids, None)  # type: ignore[misc]
        shift = max(0, len(built) - len(input_ids))
        # On suppose 1 token en début si on a au moins +1 token
        shift = 1 if shift >= 1 else 0
        return built, [1] * len(built), shift

    # 2) API alternative : prepare_for_model
    fn2 = getattr(tokenizer, "prepare_for_model", None)
    if callable(fn2):
        prepared = fn2(
            input_ids,
            add_special_tokens=True,
            return_attention_mask=True,
            truncation=False,
        )
        built = list(prepared["input_ids"])
        built_mask = list(prepared.get("attention_mask", [1] * len(built)))
        shift = max(0, len(built) - len(input_ids))
        shift = 1 if shift >= 1 else 0
        return built, built_mask, shift

    # 3) Fallback manuel (suffisant pour CamemBERT/FlauBERT / RoBERTa-like)
    bos = getattr(tokenizer, "bos_token_id", None) or getattr(tokenizer, "cls_token_id", None)
    eos = getattr(tokenizer, "eos_token_id", None) or getattr(tokenizer, "sep_token_id", None)
    if bos is None or eos is None:
        raise AttributeError(
            "Impossible d'ajouter les tokens spéciaux: tokenizer sans "
            "build_inputs_with_special_tokens/prepare_for_model et sans bos/eos_token_id."
        )
    built = [int(bos)] + list(input_ids) + [int(eos)]
    built_mask = [1] * len(built)
    shift = 1
    return built, built_mask, shift


def mean_pool_hidden(hidden: Any, positions: Sequence[int]) -> Any:
    """Moyenne des vecteurs aux positions données (PyTorch tensor)."""
    import torch

    if not positions:
        raise ValueError("Impossible de moyenner : aucune position de sous-token n'a été trouvée.")
    idx = torch.tensor(list(positions), dtype=torch.long, device=hidden.device)
    return hidden.index_select(dim=0, index=idx).mean(dim=0)


def write_jsonl(path: Path, items: Iterable[Mapping[str, Any]]) -> None:
    """Écrit un JSONL : 1 objet JSON par ligne."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for obj in items:
            f.write(json.dumps(dict(obj), ensure_ascii=False) + "\n")


def main() -> None:
    args = parse_args()

    occurrences_path = Path(args.occurrences)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Import tardif pour avoir un message d'erreur plus clair si les paquets manquent.
    try:
        import numpy as np
        import torch
        from transformers import AutoModel, AutoTokenizer
    except Exception as e:  # pragma: no cover
        raise SystemExit(
            "Dépendances manquantes. Installez au moins : transformers, torch, numpy.\n"
            f"Détail : {e}"
        )

    device_str: str = pick_device(str(args.device))
    device = torch.device(device_str)

    occs: List[OccurrenceRecord] = read_occurrences(occurrences_path)
    if not occs:
        raise SystemExit(f"Aucune occurrence trouvée dans {occurrences_path}")

    model_specs: Dict[ModelKey, str] = get_model_specs()
    selected_models: List[ModelKey] = [m for m in list(args.models) if m in model_specs]  # type: ignore[comparison-overlap]

    # On produit un meta.jsonl commun (une ligne = (occurrence, modèle, ligne dans la matrice)).
    meta_rows: List[Dict[str, Any]] = []

    for model_key in selected_models:
        model_name: str = model_specs[model_key]

        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModel.from_pretrained(model_name)
        model.eval()
        model.to(device)

        vectors: List["np.ndarray"] = []

        for batch in chunked(occs, batch_size=int(args.batch_size)):
            # Encodage "maison" pour garder un mapping mot -> sous-tokens.
            encoded_items: List[Dict[str, Any]] = []
            batch_word_maps: List[List[List[int]]] = []
            batch_shifts: List[int] = []

            for occ in batch:
                # Tokenisation basée sur les tokens déjà fournis par l'étape 2.
                ids, attn, word_to_pos = build_subtokens_with_word_mapping(tokenizer, occ.tokens)
                ids, attn, shift = add_special_tokens(tokenizer, ids, attn)

                # Sécurité : on tronque si nécessaire (fenêtre courte => rare).
                if len(ids) > int(args.max_length):
                    ids = ids[: int(args.max_length)]
                    attn = attn[: int(args.max_length)]

                encoded_items.append({"input_ids": ids, "attention_mask": attn})
                batch_word_maps.append(word_to_pos)
                batch_shifts.append(shift)

            padded = tokenizer.pad(
                encoded_items,
                padding=True,
                return_tensors="pt",
            )
            padded = {k: v.to(device) for k, v in padded.items()}

            with torch.no_grad():
                out = model(**padded)
                # (batch, seq_len, hidden_dim)
                last_hidden = out.last_hidden_state

            for i, occ in enumerate(batch):
                # Positions des sous-tokens correspondant au mot cible.
                word_to_pos = batch_word_maps[i]
                shift = batch_shifts[i]
                target_word_idx = occ.target_word_index

                positions_wo_specials: List[int] = (
                    word_to_pos[target_word_idx] if 0 <= target_word_idx < len(word_to_pos) else []
                )
                positions: List[int] = [p + shift for p in positions_wo_specials]

                vec_t = mean_pool_hidden(last_hidden[i], positions)
                vec = vec_t.detach().cpu().numpy().astype("float32")

                row_index: int = len(vectors)
                vectors.append(vec)
                meta_rows.append(
                    {
                        "occurrence_id": occ.occurrence_id,
                        "target": occ.target,
                        "model": model_key,
                        "model_name": model_name,
                        "row": row_index,
                        "n_subtokens_target": len(positions_wo_specials),
                    }
                )

        mat = np.stack(vectors, axis=0)
        out_path = out_dir / f"embeddings_{model_key}.npy"
        np.save(out_path, mat)
        print(f"[{model_key}] écrit : {out_path}  shape={mat.shape}")

    meta_path = out_dir / "embeddings_meta.jsonl"
    write_jsonl(meta_path, meta_rows)
    print(f"meta écrit : {meta_path}  lignes={len(meta_rows)}")


if __name__ == "__main__":
    main()

