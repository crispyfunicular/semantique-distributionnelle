# Sémantique distributionnelle - mini-projet
> Catalina Alvarez Ortega & Morgane Bona-Pellissier (Master 1 pluriTAL)

## INTRODUCTION 

Dans le cadre du cours de Sémantique distributionnelle du Master 1 en Traitement Automatique des Langues, nous avons été amenés à réaliser un mini-projet sur l’étude de la polysémie avec des embeddings contextuels. Si bien qu’existe différent notions sur le polysémie, c’est-à-dire quand la polysémie est dite régulière ou irrégulière, d’emblée celle-ci désigne la capacité d’un mot à recevoir plusieurs sens selon ses contextes d’emploi. Par exemple, un mot comme « voix » peut désigner le son produit par la parole, mais aussi une opinion ou une forme d’influence. Les modèles de langage basé sur le transformer, comme BERT, sont particulièrement adaptés à l’étude de ce phénomène, car ils ne produisent pas une représentation unique et fixe pour un mot donné. Au contraire, la représentation vectorielle d’une occurrence dépend du contexte dans lequel le mot apparaît. Ainsi, deux occurrences d’un même mot peuvent recevoir des embeddings différents si elles sont employées dans des sens ou des environnements sémantiques distincts.

L’objectif de ce projet est d’évaluer dans quelle mesure cette variation vectorielle peut être interprétée comme un indice de polysémie. Pour cela, nous travaillons à partir d’un corpus de 29 romans au format `.txt` et d’une liste de mots cibles, comprenant des noms et des verbes. Pour chaque mot, nous extrayons plusieurs occurrences en contexte, puis nous les encodons avec des modèles BERT pour le français. Nous définissons ensuite un score de polysémie fondé sur l’écart-type des similarités cosinus deux à deux entre les embeddings des occurrences d’un même mot. Un score élevé indique une forte dispersion des représentations, tandis qu’un score faible indique des usages plus homogènes. Afin de déterminer si ce score correspond effectivement à la notion linguistique de polysémie, nous le confrontons à une mesure externe fondée sur des macro-sens. Nous utilisons également des visualisations 2D par réduction de dimensionnalité afin d’observer qualitativement la distribution des occurrences dans l’espace vectoriel.


## Hypothèses

Le corpus utilisé est composé de 29 œuvres littéraires et argumentatives françaises, couvrant différents genres : roman réaliste, récit sentimental, conte, texte philosophique, texte politique, poésie et récit d’aventure. Cette diversité des differents thèmes et époques peut être intéressant pour l’étude de la variation lexicale, car les mots peuvent y apparaître dans des contextes concrets, abstraits, figurés ou spécialisés.

Nous faisons l’hypothèse que les mots fortement polysémiques ou employés dans des contextes sémantiquement variés auront des embeddings contextuels plus dispersés. Cette dispersion devrait se traduire par un score de polysémie plus élevé, calculé à partir de l’écart-type des similarités cosinus entre occurrences d’un même mot. À l’inverse, les mots dont les emplois sont plus homogènes devraient obtenir un score plus faible. Notre sélection de mots vise à tester cette hypothèse sur plusieurs types de cibles. Les noms `porte`, `feu`, `pied`, `cour`, `voix` et `campagne` présentent des emplois concrets, abstraits, institutionnels ou figurés. Les verbes `passer` et `entendre` sont également susceptibles de varier selon leur construction et leur contexte. Enfin, `baron` est utilisé comme contrôle à faible polysémie, car il devrait renvoyer majoritairement, dans ce corpus littéraire,à un noble ou à une personne appelée ainsi.

## Structure de la pipeline
> L'intégralité du pipeline est consultable à l'adresse : https://github.com/crispyfunicular/semantique-distributionnelle/tree/main/mini_projet

### 1. Normaliser le corpus 

 Le script `1.normalisation_corpus.py` parcourt les fichiers `.txt` du dossier `corpus/` et corrige certaines variations graphiques. Il remplace notamment les apostrophes typographiques par une apostrophe simple et harmonise certaines graphies en `oe` vers la ligature `œ`. En normalisant ces formes, on limite donc le bruit lié à l’encodage et à la typographie. Elle rend donc le corpus plus homogène avant l’extraction des occurrences des mots cibles.

### 2. Extraction des occurrences

Le script `2.extraire_occurrences.py` prend en entrée un corpus texte et une liste de mots cibles. Il normalise et tokenise le corpus, puis repère toutes les occurrences exactes des mots cibles. Pour chaque occurrence, Nous avons finalement retenu une fenêtre de contexte de dix mots à gauche et dix mots à droite du mot cible. Ce choix permet de donner au modèle suffisamment d’informations pour interpréter l’occurrence, sans élargir excessivement le contexte. Lorsque le nombre d’occurrences disponibles dépasse le seuil fixé, le script en tire un échantillon aléatoire reproductible grâce à une seed. Les occurrences sont ensuite sauvegardées dans un fichier `occurrences.jsonl`, tandis que les paramètres du run et le nombre d’occurrences extraites par mot sont enregistrés dans `targets.json`.

Utilisation depuis la racine :
`python3 mini_projet/scripts/2.extraire_occurrences.py --corpus mini_projet/corpus_complet.txt --targets esprit or courir porte --k 10 --n 30 --seed 42 --out_dir mini_projet/data`

Sorties (dans `mini_projet/data/`) :
- `occurrences.jsonl` : une occurrence par ligne
- `targets.json` : récap (corpus, k, n, seed, etc.)

### l'encodage des occurrences avec CamamBERT et FlauBERT

La troisième étape du pipeline consiste à encoder les occurrences extraites avec des modèles BERT pour le français. Le script `3.encoder_embeddings.py` lit le fichier `occurrences.jsonl` produit à l’étape précédente, puis calcule un embedding contextuel pour chaque occurrence du mot cible.

Nous utilisons deux modèles : CamemBERT et FlauBERT. Ces modèles produisent des représentations contextuelles, c’est-à-dire qu’une même forme lexicale peut recevoir des vecteurs différents selon son contexte d’apparition. Le script extrait spécifiquement le vecteur du mot cible dans son contexte. Comme les tokenizers de type BERT peuvent découper un mot en plusieurs sous-tokens, le script reconstruit l’alignement entre les mots du contexte et leurs sous-tokens. Lorsque le mot cible est segmenté en plusieurs sous-tokens, son embedding est obtenu en calculant la moyenne des vecteurs correspondants.

Les embeddings sont calculés à partir de la dernière couche cachée du modèle, sans fine-tuning. Le script produit une matrice d’embeddings pour chaque modèle (`embeddings_camembert.npy` et `embeddings_flaubert.npy`) ainsi qu’un fichier de métadonnées (`embeddings_meta.jsonl`) permettant de relier chaque occurrence à sa ligne dans la matrice.

Utilisation depuis la racine :
`python3 mini_projet/scripts/3.encoder_embeddings.py --occurrences mini_projet/data/occurrences.jsonl --out_dir mini_projet/data --models camembert flaubert --batch_size 16 --device auto`

Sorties (dans `mini_projet/data/`) :
- `embeddings_camembert.npy` : matrice (N_occurrences, dim)
- `embeddings_flaubert.npy` : matrice (N_occurrences, dim)
- `embeddings_meta.jsonl` : lien entre `occurrence_id`, modèle et ligne dans la matrice

### 4. Calcul d'un score de polysémie à partir des embeddings.

La quatrième étape du pipeline consiste à calculer un score de polysémie à partir des embeddings contextuels. Le script `4.score_polysemie.py` lit les matrices d’embeddings produites à l’étape précédente ainsi que le fichier `embeddings_meta.jsonl`, qui permet d’associer chaque ligne de la matrice à une occurrence et à un mot cible.

Pour chaque mot cible, le script regroupe les embeddings de ses occurrences et calcule les similarités cosinus entre toutes les paires d’occurrences. Il produit plusieurs statistiques, notamment la moyenne, le minimum, le maximum et surtout l’écart-type des similarités. Le score principal retenu est cosine_std. Un score faible indique que les occurrences sont représentées de manière homogène dans l’espace vectoriel, tandis qu’un score élevé signale une plus forte dispersion des embeddings. Ce score est donc interprété comme un indicateur de variation contextuelle, et non comme un nombre direct de sens.

Le script produit deux fichiers : polysemy_scores.json, qui contient les statistiques détaillées, et polysemy_ranking.json, qui classe les mots selon leur score de dispersion

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

