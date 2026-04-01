# TP3 — Analyse et correction des biais coloniaux (GloVe)

Ce TP entraîne un modèle GloVe sur un corpus littéraire de deux auteurs de langue anglaise, Rudyard Kipling et Joseph Conrad, afin de mettre en évidence les biais coloniaux encodés dans les représentations distributionnelles, puis les atténuer via deux stratégies complémentaires.

## Installation

```bash
pip install -r requirements.txt
python -m nltk.downloader stopwords
```

## Corpus

Le corpus est composé d'œuvres de Rudyard Kipling et de Joseph Conrad issues du domaine public (Project Gutenberg), thématisées autour de l'espace colonial britannique.

### Conrad, Joseph

| Fichier source | Titre |
|---|---|
| `conrad_darkness.txt` | *Heart of Darkness* (1899) |
| `conrad_island.txt` | *Victory: An Island Tale* (1915) |
| `conrad_jim.txt` | *Lord Jim* (1900) |
| `conrad_narcissus.txt` | *The Nigger of the "Narcissus"* (1897) |
| `conrad_outcast.txt` | *An Outcast of the Islands* (1896) |
| `conrad_typhoon.txt` | *Typhoon* (1902) |

### Kipling, Rudyard

| Fichier source | Titre |
|---|---|
| `kipling_black_white.txt` | *In Black and White* (1888) |
| `kipling_deodars.txt` | *Under the Deodars* (1888) |
| `kipling_gadsbys.txt` | *The Story of the Gadsbys* (1888) |
| `kipling_hills.txt` | *Plain Tales from the Hills* (1888) |
| `kipling_jungle.txt` | *The Jungle Book* (1894) |
| `kipling_jungle2.txt` | *The Second Jungle Book* (1895) |
| `kipling_kim.txt` | *Kim* (1901) |
| `kipling_king.txt` | *The Man Who Would Be King* (1888) |
| `kipling_life.txt` | *Life's Handicap: Being Stories of Mine Own People* (1891) |
| `kipling_light.txt` | *The Light That Failed* (1891) |
| `kipling_sea.txt` | *From Sea to Sea: Letters of Travel* (1899) |
| `kipling_soldiers.txt` | *Soldiers Three* (1888) |

Les textes bruts sont stockés dans `corpus/corpus_kipling_raw/` et `corpus/conrad_raw/`. Les fichiers lemmatisés (`corpus/kipling_lemmes.txt`, `corpus/conrad_lemmes.txt`) sont produits par `lemmatisation.py`. Le corpus fusionné (`corpus/corpus_lemmes.txt`) combine les deux auteurs.

---

## Prérequis

Le corpus doit être **préalablement lemmatisé** (une phrase par ligne, tokens séparés par des espaces). Les fichiers attendus par défaut sont :
- `corpus/kipling_lemmes.txt` — produit par `lemmatisation.py` sur le corpus Kipling
- `corpus/conrad_lemmes.txt` — produit par `lemmatisation.py` sur le corpus Conrad
- `corpus/corpus_lemmes.txt` — corpus fusionné (Kipling + Conrad)

---

## Utilisation

### Mode standard — analyse des biais bruts

Entraîne un modèle GloVe et évalue les analogies vectorielles définies dans `analogies.txt`.

```bash
python tp3.py corpus/kipling_lemmes.txt
```

**Sortie** : `resultats/kipling_lemmes_resultats.md`

---

### Mode CDA — Counterfactual Data Augmentation

Entraîne **deux modèles** (standard + augmenté) et produit un tableau comparatif côte à côte.

Le corpus augmenté est le corpus original doublé par une version miroir où les termes coloniaux polarisés sont inversés (`english` ↔ `native`, `white` ↔ `brown`, `sahib` ↔ `servant`, `england` ↔ `india`, `city` ↔ `jungle`).

```bash
python tp3.py corpus/kipling_lemmes.txt --cda
```

**Sortie** : `resultats/kipling_lemmes_comparatif_cda.md`

---

### Mode Hard Debiasing — débiaisage post-hoc des vecteurs

Prend le modèle standard entraîné et retire la **direction du biais colonial** de tous les vecteurs par projection orthogonale (algorithme de Bolukbasi et al., 2016).

L'axe du biais est calculé par PCA sur les vecteurs de différence des paires définitionnelles (`english`−`native`, `white`−`brown`, `sahib`−`servant`, `england`−`india`).

```bash
python tp3.py corpus/kipling_lemmes.txt --debiais
```

**Sortie** : `resultats/kipling_lemmes_comparatif_debiais.md`

---

### Mode triple — comparaison des trois stratégies

Combine les deux flags pour comparer **Standard / CDA / Débiaisé** dans un unique tableau à six colonnes.

```bash
python tp3.py corpus/kipling_lemmes.txt --cda --debiais
```

**Sortie** : `resultats/kipling_lemmes_comparatif_triple.md`

---

## Structure du projet

```
tp3/
├── tp3.py              # Script principal (pipeline + débiaisage)
├── lemmatisation.py    # Lemmatisation spaCy du corpus brut
├── nettoyage.py        # Nettoyage du texte brut
├── analogies.txt       # Liste des analogies vectorielles à tester
├── requirements.txt    # Dépendances Python
├── tp3.md              # Rapport (contexte, hypothèses, résultats)
├── corpus/
│   ├── corpus_kipling_raw/   # Textes bruts Kipling (Project Gutenberg)
│   ├── conrad_raw/           # Textes bruts Conrad (Project Gutenberg)
│   ├── kipling_lemmes.txt    # Corpus Kipling lemmatisé
│   ├── conrad_lemmes.txt     # Corpus Conrad lemmatisé
│   ├── corpus_lemmes.txt     # Corpus fusionné (Kipling + Conrad)
│   └── kipling_clean.txt     # Corpus Kipling nettoyé (intermédiaire)
└── resultats/
    ├── kipling_lemmes_resultats.md          # Biais bruts
    ├── kipling_lemmes_comparatif_cda.md     # Standard vs CDA
    ├── kipling_lemmes_comparatif_debiais.md # Standard vs Débiaisé
    └── kipling_lemmes_comparatif_triple.md  # Les trois côte à côte
```
