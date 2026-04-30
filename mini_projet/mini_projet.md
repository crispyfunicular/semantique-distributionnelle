# Sémantique distributionnelle - mini-projet
> Catalina Alvarez Ortega & Morgane Bona-Pellissier (Master 1 pluriTAL)

## Pipeline
> L'intégralité du pipeline est consultable à l'adresse : https://github.com/crispyfunicular/semantique-distributionnelle/tree/main/mini_projet

### `1.normalisation_corpus.py`
Normalise les fichiers du corpus pour éviter des incohérences d’écriture.

Ce script :
- remplace les apostrophes typographiques par une apostrophe simple ;
- remplace certaines graphies en `oe` par la ligature `œ` (liste contrôlée) ;
- réécrit les fichiers du dossier `mini_projet/corpus/` uniquement si un changement est nécessaire.

### `2.extraire_occurrences.py`
Extraction d'occurrences et de leur contexte (fenêtre de mots).

Ce script :
- cherche des mots cibles dans un corpus,
- garde k mots à gauche et k mots à droite,
- prend au plus N exemples par mot (toujours les mêmes si on garde la même seed),
- écrit les résultats dans un fichier `occurrences.jsonl` (une occurrence par ligne).

Utilisation depuis la racine :
`python3 mini_projet/scripts/2.extraire_occurrences.py --corpus mini_projet/corpus_complet.txt --targets esprit or courir porte --k 10 --n 30 --seed 42 --out_dir mini_projet/data`

Sorties (dans `mini_projet/data/`) :
- `occurrences.jsonl` : une occurrence par ligne
- `targets.json` : récap (corpus, k, n, seed, etc.)

### `3.encoder_embeddings.py`
Encodage des occurrences avec CamemBERT et/ou FlauBERT.

Ce script :
- lit `mini_projet/data/occurrences.jsonl`,
- calcule un vecteur par occurrence (moyenne des sous-tokens du mot cible),
- écrit les embeddings et un fichier de correspondance (métadonnées).

Utilisation depuis la racine :
`python3 mini_projet/scripts/3.encoder_embeddings.py --occurrences mini_projet/data/occurrences.jsonl --out_dir mini_projet/data --models camembert flaubert --batch_size 16 --device auto`

Sorties (dans `mini_projet/data/`) :
- `embeddings_camembert.npy` : matrice (N_occurrences, dim)
- `embeddings_flaubert.npy` : matrice (N_occurrences, dim)
- `embeddings_meta.jsonl` : lien entre `occurrence_id`, modèle et ligne dans la matrice

### `4.score_polysemie.py`
Calcul d'un score de polysémie à partir des embeddings.

Ce script :
- lit `embeddings_*.npy` et `embeddings_meta.jsonl`,
- calcule, pour chaque mot et pour chaque modèle, la dispersion des cosinus 2-à-2,
- écrit un fichier JSON de scores et un fichier JSON de classement (ranking).

Utilisation depuis la racine :
`python3 mini_projet/scripts/4.score_polysemie.py --data_dir mini_projet/data`

Sorties (dans `mini_projet/data/`) :
- `polysemy_scores.json` : scores par modèle et par mot
- `polysemy_ranking.json` : mots triés par score (par modèle)

### `5.visualiser_2d.py` (optionnel, pour l'oral)
Visualisation 2D des occurrences d'un mot cible (export PNG).

Par défaut : PCA 2D (rapide). Option : UMAP 2D (si installé).

Utilisation depuis la racine (exemple) :
`python3 mini_projet/scripts/5.visualiser_2d.py --data_dir mini_projet/data --model camembert --target esprit --method pca --out_dir mini_projet/data/viz --write_examples`

Sorties (dans `mini_projet/data/viz/`) :
- `<model>_<target>_<method>.png`
- (optionnel) `<model>_<target>_<method>_examples.txt` (quelques contextes)

## Choix effectués
- Choix du corpus
- Nombre maximal d'occurrences extraites par mot cible (`n`)
- Taille de la fenêtre de contexte autour du mot cible (`k`) : k mots à gauche et k mots à droite -> *citer TP2*
- FlauBERT vs CamemBERT

| | **CamemBERT** | **FlauBERT** |
|---|---|---|
| Référence | Martin et al. (2020) | Le et al. (2020) |
| Architecture de base | RoBERTa (encodeur Transformer) | Transformer encodeur (XLM-like) |
| Données d'entraînement | OSCAR + Wikipedia FR (~138 Go) | CCNet FR (~71 Go, filtré par perplexité) |
| Tokenisation | SentencePiece BPE (~32k tokens) | BPE (~68k tokens) |
| Dimension des embeddings | 768 | 768 |
| Couches / têtes d'attention | 12 / 12 | 12 / 12 |

Les deux modèles sont des **encodeurs contextuels** : ils produisent, pour un même mot, des représentations vectorielles différentes selon le contexte d'occurrence. C'est précisément cette propriété que nous exploitons pour mesurer la variation sémantique. Nous les utilisons ici sans fine-tuning (extraction directe des représentations de la dernière couche cachée).


### Comportement comparé des deux modèles
**CamemBERT** produit des embeddings plus « concentrés » (cosinus moyens ~0.80–0.92) dont la dispersion relative reflète bien les différences sémantiques inter-mots. **FlauBERT** produit des embeddings intrinsèquement plus dispersés dans toutes les directions de l'espace, ce qui atténue les différences entre cibles et rend le score `cosine_std` moins discriminant sans normalisation préalable.

## Discussion des résultats
*A reformuler*

### Score de polysémie : rappel de la mesure

Le score utilisé est l'**écart-type des similarités cosinus 2-à-2** entre les embeddings contextuels des occurrences d'un même mot. Un score élevé signale une dispersion forte → les occurrences sont représentées dans des régions variées de l'espace d'embedding → hypothèse de polysémie ou de variation sémantique importante. Un score faible signale des usages homogènes → hypothèse de monosémie ou de sens stable dans le corpus.

### Run retenu : `resultats_baron` (CamemBERT, n=100, k=10)

| Mot | n occ. | cosine_mean | **cosine_std** | cosine_min | cosine_max |
|---|---|---|---|---|---|
| `porte` | 100 | 0.799 | **0.116** | 0.270 | 0.974 |
| `feu` | 100 | 0.804 | **0.114** | 0.193 | 0.973 |
| `passer` | 100 | 0.750 | **0.092** | 0.334 | 0.960 |
| `baron` | 100 | 0.920 | **0.040** | 0.663 | 0.985 |

**Classement CamemBERT :** `porte` > `feu` > `passer` > `baron`

**Classement FlauBERT :** `porte` > `passer` ≈ `baron` ≈ `feu` (scores très resserrés, ~0.22–0.25)

### Observations
*à reformuler*


**1. CamemBERT discrimine efficacement les mots.**  
`baron`, quasi-monosémique dans un corpus littéraire (toujours le titre nobiliaire), obtient un score près de **3× inférieur** à `porte`. L'écart est clair et linguistiquement motivé.

**2. FlauBERT est peu discriminant.**  
Les scores FlauBERT sont très proches pour toutes les cibles : `baron` (0.239) n'est pas distingué de `porte` (0.250). L'espace d'embedding de FlauBERT semble intrinsèquement plus dispersé, ce qui atténue les différences inter-mots. Ce modèle n'est pas adapté à cette mesure sans normalisation préalable.

**3. La mesure ne se corrèle pas directement avec le nombre de sens lexicographiques.**  
D'après le Wiktionnaire, `esprit` possède **13 acceptions** et `porte` **11** — soit légèrement plus pour `esprit`. Pourtant, CamemBERT classe `porte` *devant* `esprit` (run `resultats_1` : 0.094 vs 0.065). Deux facteurs l'expliquent :
- `porte` est aussi une **forme verbale** de *porter* (présent 1re/3e sg.) : sans filtrage POS, le modèle mélange les contextes nominaux et verbaux, ce qui gonfle artificiellement la dispersion.
- Les acceptions d'`esprit` dans un corpus littéraire restent dans un champ thématique étroit (intellect, pensée, caractère) ; les sens plus marginaux (Esprit-Saint, esprits chimiques…) sont peu représentés.

**4. Validation qualitative par les paires extrêmes (`porte`, CamemBERT).**  
Les paires d'occurrences les plus *éloignées* (cos ≈ 0.43) opposent bien des usages distincts :
- *sens nominal concret* : « il vit une **porte** ouverte et prit vivement la main d'emilie »
- *emploi verbal* : « celui de mont franklin à ce lac nous **porte** en ce moment »

Les paires les plus *proches* (cos ≈ 0.97) sont toutes au sens nominal physique (battant de porte). Ce contraste confirme que la dispersion reflète une vraie variation sémantique — même si une partie est imputable à l'ambiguïté POS.

