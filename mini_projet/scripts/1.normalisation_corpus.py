#!/usr/bin/env python3
"""
Normalise le texte du corpus :
- apostrophes typographiques (U+2019 etc.) → apostrophe droite ASCII '
- graphies françaises en oe → œ (mots entiers / expressions listés, sans heurter coefficient, moelle, noms propres).
"""
from __future__ import annotations

import re
from pathlib import Path

CORPUS_DIR = Path(__file__).resolve().parent / "corpus"

# Apostrophe-like → ASCII U+0027
_APOSTROPHE_MAP = str.maketrans(
    {
        "\u2019": "'",  # RIGHT SINGLE QUOTATION MARK (courant dans les .txt)
        "\u2018": "'",  # LEFT SINGLE QUOTATION MARK
        "\u02bc": "'",  # MODIFIER LETTER APOSTROPHE
        "\u02bb": "'",  # MODIFIER LETTER TURNED COMMA
    }
)

# minuscule → forme canonique avec ligature (clé = mot entier après apostrophe ASCII)
_WORD_Œ: dict[str, str] = {
    "oeuvres": "œuvres",
    "oeuvre": "œuvre",
    "oeils": "œils",
    "oeil": "œil",
    "oeufs": "œufs",
    "oeuf": "œuf",
    "coeurs": "cœurs",
    "coeur": "cœur",
    "soeurs": "sœurs",
    "soeur": "sœur",
    "noeuds": "nœuds",
    "noeud": "nœud",
    "voeux": "vœux",
    "voeu": "vœu",
    "boeufs": "bœufs",
    "boeuf": "bœuf",
    "moeurs": "mœurs",
    "choeurs": "chœurs",
    "choeur": "chœur",
    "oedipe": "œdipe",
    "oedipes": "œdipes",
    "foetus": "fœtus",
    "oesophage": "œsophage",
    "oesophages": "œsophages",
    "oedeme": "œdème",
    "oedèmes": "œdèmes",
    "oenologie": "œnologie",
    "oenologique": "œnologique",
    "oenographe": "œnographe",
    "oestrogene": "œstrogène",
    "oestrogène": "œstrogène",
    "oestrogènes": "œstrogènes",
}

# Alternation la plus longue d'abord
_Œ_WORD_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in sorted(_WORD_Œ, key=len, reverse=True)) + r")\b",
    re.IGNORECASE,
)

_PHRASES = [
    (re.compile(r"(?i)chef-d'oeuvres\b"), "chef-d'œuvres"),
    (re.compile(r"(?i)chef-d'oeuvre\b"), "chef-d'œuvre"),
    (re.compile(r"(?i)chef d'oeuvres\b"), "chef d'œuvres"),
    (re.compile(r"(?i)chef d'oeuvre\b"), "chef d'œuvre"),
]


def _case_like(original: str, replacement_lower: str) -> str:
    rep = replacement_lower
    if original.isupper():
        return rep.upper()
    if original[0].isupper():
        return rep.capitalize()
    return rep


def _replace_œ_word(m: re.Match[str]) -> str:
    w = m.group(1)
    key = w.lower()
    rep = _WORD_Œ[key]
    return _case_like(w, rep)


def _replace_manoeuvr(m: re.Match[str]) -> str:
    w = m.group(0)
    low = w.lower()
    if not low.startswith("manoeuvr"):
        return w
    rest = low[9:]
    rep_low = "manœuvr" + rest
    if w.isupper():
        return rep_low.upper()
    if w[0].isupper():
        return rep_low.capitalize()
    return rep_low


def normalize_text(text: str) -> str:
    text = text.translate(_APOSTROPHE_MAP)
    # manœuvre, manœuvrer, etc. (sans toucher à des mots hors liste)
    text = re.sub(r"(?i)manoeuvr\w*", _replace_manoeuvr, text)
    for rx, repl in _PHRASES:
        text = rx.sub(repl, text)
    text = _Œ_WORD_PATTERN.sub(_replace_œ_word, text)
    return text


def main() -> None:
    for path in sorted(CORPUS_DIR.glob("*.txt")):
        raw = path.read_text(encoding="utf-8", errors="replace")
        new = normalize_text(raw)
        if new != raw:
            path.write_text(new, encoding="utf-8")
            print("updated", path.name)
        else:
            print("unchanged", path.name)


if __name__ == "__main__":
    main()
