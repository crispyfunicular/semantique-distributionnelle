# Sémantique distributionnelle - mini-projet
> Catalina Alvarez Ortega & Morgane Bona-Pellissier (Master 1 pluriTAL)

## Consignes
> https://www.linguist.univ-paris-diderot.fr/~amsili/Ens/LZSET06/

**Etude de la polysémie avec des embeddings contextuels**  
A partir d'embeddings contextuels obtenus avec BERT pour un certain nombre d'occurrences de noms (ou de verbes) préalablement choisis, on définit un score de polysémie basé sur l'écart-type des similarités cosinus 2 à 2 des embeddings d'un même mot. L'objectif du projet est de déterminer à quel point ce score de polysémie correspond à la notion linguistique de polysémie. Pour cela, on pourra utiliser des visualisation 2D par réduction de dimensionalité pour confirmer les intuitions, mais on devra aussi corréler cette mesure avec une autre mesure de polysémie basée sur des ressources linguistiques ou à la rigueur sur des statistiques sur grand corpus.

## Pipeline
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

## Dossier `data/` : contenu et interprétation

Le dossier `data/` contient **tous les artefacts intermédiaires et finals** du pipeline. C’est ce dossier qu’il faut copier lorsque le pipeline a été exécuté sur une machine distante pour pouvoir ensuite analyser / visualiser localement les résultats.

### Fichiers produits

- **`occurrences.jsonl`** : *1 occurrence par ligne* (JSON). Chaque entrée contient notamment :
  - `occurrence_id` : identifiant unique de l’occurrence
  - `target` : le mot cible
  - `tokens` : la fenêtre de contexte (liste de tokens) utilisée ensuite pour l’encodage
  - (selon l’étape 2) positions/index du mot cible dans `tokens`
- **`targets.json`** : récap des paramètres d’extraction (corpus, liste de cibles, `k`, `n`, `seed`, etc.). Utile pour la traçabilité/reproductibilité.
- **`embeddings_<model>.npy`** : matrice NumPy de taille `(N_occurrences, dim)` contenant **un vecteur par occurrence** (moyenne des sous-tokens du mot cible).  
  Exemples : `embeddings_camembert.npy`, `embeddings_flaubert.npy`.
- **`embeddings_meta.jsonl`** : table de correspondance (JSONL) entre les occurrences et les lignes des matrices `.npy`.  
  Chaque ligne correspond à un couple *(occurrence, modèle)* et contient typiquement :
  - `occurrence_id` et `target`
  - `model` : nom du modèle (`camembert`, `flaubert`, …)
  - `row` : index de ligne dans `embeddings_<model>.npy` (0-indexé)
  → Pour retrouver le vecteur d’une occurrence, on filtre `embeddings_meta.jsonl` puis on prend `embeddings_<model>[row]`.
- **`polysemy_scores.json`** : scores de polysémie par **modèle** et par **mot cible**.  
  Le score correspond à une **dispersion** (écart-type) des similarités cosinus \(2\)-à-\(2\) entre les embeddings des occurrences d’un même mot : plus c’est dispersé, plus le mot est “polysémique” selon cette mesure.
- **`polysemy_ranking.json`** : classement des mots cibles **du plus au moins “polysémique”** (par modèle), basé sur `polysemy_scores.json`.

## Dépendances
Pour installer les dépendances du mini-projet :
`pip install -r mini_projet/requirements.txt`

Le script 5 (visualisation, `5.visualiser_2d.py`) utilise `matplotlib` (déjà dans `requirements.txt`).
Pour utiliser UMAP (`--method umap`), installez en plus :
`pip install umap-learn`

## Analyse des résultats

Les scores/classements proviennent de `polysemy_scores.json` et `polysemy_ranking.json` (score = `cosine_std`).

### Vue d'ensemble des runs

| Run | Cibles | \(k\) | \(n\) | Remarques |
|---|---|---|---|---|
| `resultats_1` | esprit, or, courir, porte | 10 | 30 | exploration initiale ; `or` ambigu (conjonction/nom) |
| `resultats_2` | esprit, courir, porte | 10 | 100 (58 pour courir) | `courir` plafonné dans le corpus |
| `resultats_3` | porte, feu, passer | 5 | 100 | test fenêtre réduite ; `grève` absent du corpus (pb avec l'accent) |
| `resultats_baron` | porte, feu, passer, baron | 10 | 100 | run le plus abouti ; `baron` sert de pôle monosémique |

### Classements comparés

**CamemBERT** (score = `cosine_std`)

| Run | 1er | 2e | 3e | 4e |
|---|---|---|---|---|
| `resultats_1` | courir (0.101) | porte (0.094) | or (0.091) | esprit (0.065) |
| `resultats_2` | porte (0.113) | courir (0.102) | esprit (0.069) | — |
| `resultats_3` | porte (0.108) | feu (0.096) | passer (0.094) | — |
| `resultats_baron` | **porte (0.116)** | feu (0.114) | passer (0.092) | **baron (0.040)** |

**FlauBERT** (score = `cosine_std`)

| Run | 1er | 2e | 3e | 4e |
|---|---|---|---|---|
| `resultats_1` | courir (0.265) | or (0.239) | porte (0.227) | esprit (0.220) |
| `resultats_2` | courir (0.253) | esprit (0.225) | porte (0.218) | — |
| `resultats_3` | porte (0.183) | passer (0.167) | feu (0.162) | — |
| `resultats_baron` | porte (0.250) | passer (0.239) | baron (0.239) | feu (0.223) |

### Observations principales

- **CamemBERT discrimine mieux** : dans `resultats_baron`, `baron` sort nettement en bas (0.040), loin derrière les autres (0.092–0.116), ce qui valide que la mesure capte quelque chose de linguistiquement réel. Le classement `porte` ≈ `feu` > `passer` > `baron` est stable.
- **FlauBERT est peu discriminant** : les scores sont très resserrés et `baron` n'est pas distingué des mots polysémiques. L'espace d'embedding de FlauBERT semble intrinsèquement plus dispersé, ce qui atténue les différences entre cibles.
- **`porte` est la cible la plus robuste** : toujours en tête, pour les deux modèles, sur tous les runs.
- **Cibles à écarter** : `or` (mélange conjonction/nom), `courir` (plafonné à 58 occurrences dans le corpus).

### Lecture des scores

- Score **élevé** → usages hétérogènes en embedding → hypothèse de polysémie / variation sémantique forte
- Score **faible** → usages homogènes → hypothèse de monosémie / sens stable

### Présentation des résultats
#### Validation qualitative : paires d’occurrences "extrêmes"
Pour chaque cible, examiner les contextes des paires d'occurrences les plus proches et les plus éloignées (en cosinus), afin de vérifier que la dispersion reflète bien une variation de sens et non du bruit.

    **Exemple sur `porte` (CamemBERT, `resultats_1`, n=30, std=0.094) :**

    Paires les plus *éloignées* (cos ≈ 0.43–0.49) — sens distincts :
    - `il vit une porte ouverte et prit vivement la main d'emilie` (sens concret : battant physique)
    - `celui de mont franklin à ce lac nous porte en ce moment` (emploi verbal : porter vers)
    - `galerie philosophique… porte contre le duc d'epernon` (emploi figé/juridique : porter plainte)

    Paires les plus *proches* (cos ≈ 0.96–0.97) — même sens concret :
    - `il y avait près de la porte et le long des murs quelques personnes debout`
    - `la porte s'ouvrit presque aussitôt et un grand valet entra`

    **Exemple sur `esprit` (CamemBERT, `resultats_1`, n=30, std=0.065) :**

    Paires les plus *éloignées* (cos ≈ 0.65–0.67) — variation faible, même champ sémantique :
    - `répondre avec esprit aux sages représentations` (vivacité d'esprit)
    - `son esprit critique aurait pu s'exercer à miracle` (capacité intellectuelle)
    - `dans son esprit la triste prudence l'emportait` (= dans sa pensée)

    → Le cosinus minimal de `esprit` (0.65) reste bien au-dessus de celui de `porte` (0.43), ce qui
    est cohérent avec la différence de scores (std 0.065 vs 0.094) et valide la mesure.

#### Confrontation à des ressources externes
Corréler avec une ressource externe (Wiktionnaire, CNRTL, etc.), en gardant en tête que ces ressources comptent des **sens lexicographiques** qui ne se retrouvent pas forcément dans le corpus :
    - **Wiktionnaire** (indicatif) : `esprit` ≈ 13 acceptions ; `porte` ≈ 11 (attention : `porte` inclut aussi une *forme verbale* de `porter`, ce qui peut augmenter artificiellement la dispersion si l’on ne filtre pas par POS).
    - **CNRTL** (structure hiérarchique) : `esprit` (2 macro-sens → 5 acceptions principales → ~13 variations) ; `porte` (2 sens fondamentaux → 5 acceptions → ~8 nuances).

## Visualisation des résultats
Utiliser la visualisation 2D (`5.visualiser_2d.py`) comme confirmation qualitative.
