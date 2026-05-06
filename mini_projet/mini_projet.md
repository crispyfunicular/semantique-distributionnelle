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

## Choix méthodologiques effectués
Comment dit précédemment nous avons choisi in corpus composé de 29 œuvres littéraires et argumentaires français, qui abordent de sujet comment l’amour, la mort, la politique, la religion etc. Si bien que notre choix peut mobiliser une grande diversité lexicale, il faut remarquer que notre mesure porte uniquement sur les sens présents dans ce corpus. Un mot peut donc être très polysémique dans un dictionnaire, mais apparaître dans le corpus avec un nombre plus restreint d’usages. De même, nous avons choisi de travailler sur des formes lexicales exactes plutôt que sur des lemmes. Ce choix permet de conserver un protocole simple et reproductible, sans dépendre d’un outil externe de lemmatisation ou d’étiquetage morphosyntaxique. 
En outre, le paramètre `k` correspond au nombre de mots conservés à gauche et à droite du mot cible. Dans notre run final, nous avons retenu `k = 10`, soit dix mots à gauche et dix mots à droite de chaque occurrence. Ce choix s’appuie sur les réflexions du TP2, consacré à l’influence de la taille du contexte dans les représentations distributionnelles. Ce TP montrait que la taille de la fenêtre pouvait modifier les voisins obtenus par similarité cosinus et donc les propriétés linguistiques capturées. Même si notre projet utilise des embeddings contextuels BERT plutôt que des embeddings statiques par cooccurrences, la taille du contexte reste importante : une fenêtre trop courte peut manquer d’indices sémantiques, tandis qu’une fenêtre trop large peut introduire du bruit. La fenêtre de dix mots constitue donc un compromis.

### Choix des modèles : CamemBERT et FlauBERT
Nous avons utilisé deux modèles BERT adaptés au français : CamemBERT et FlauBERT. Ces modèles sont tous deux des encodeurs contextuels : ils produisent, pour un même mot, des représentations vectorielles différentes selon le contexte d’occurrence. C’est précisément cette propriété que nous exploitons pour mesurer la variation sémantique.

| | **CamemBERT** | **FlauBERT** |
|---|---|---|
| Référence | Martin et al. (2020) | Le et al. (2020) |
| Architecture de base | RoBERTa (encodeur Transformer) | Transformer encodeur (XLM-like) |
| Données d'entraînement | OSCAR + Wikipedia FR (~138 Go) | CCNet FR (~71 Go, filtré par perplexité) |
| Tokenisation | SentencePiece BPE (~32k tokens) | BPE (~68k tokens) |
| Dimension des embeddings | 768 | 768 |
| Couches / têtes d'attention | 12 / 12 | 12 / 12 |

Nous utilisons ces modèles sans fine-tuning : les embeddings sont extraits directement à partir de la dernière couche cachée. Pour chaque occurrence, nous récupérons la représentation du mot cible. Lorsque le mot est segmenté en plusieurs sous-tokens, les vecteurs correspondants sont moyennés afin d’obtenir un seul embedding par occurrence.

Même si les deux modèles sont utilisés dans le pipeline, nous retenons CamemBERT comme modèle principal pour l’analyse finale. Dans nos expérimentations, CamemBERT produit des scores plus différenciés entre les mots cibles, tandis que FlauBERT donne des scores plus resserrés, ce qui rend l’interprétation moins nette.

Le classement final obtenu avec CamemBERT est le suivant :

| Rang | Mot | Score `cosine_std` |
|---:|---|---:|
| 1 | `voix` | 0.141 |
| 2 | `pied` | 0.125 |
| 3 | `cour` | 0.124 |
| 4 | `porte` | 0.116 |
| 5 | `feu` | 0.114 |
| 6 | `entendre` | 0.111 |
| 7 | `passer` | 0.092 |
| 8 | `campagne` | 0.088 |
| 9 | `baron` | 0.040 |

Ce classement est globalement cohérent avec notre hypothèse : les mots `voix`, `pied`, `cour`, `porte` et `feu`, qui présentent des emplois variés, obtiennent les scores les plus élevés. À l’inverse, `baron`, utilisé comme contrôle à faible polysémie, obtient le score le plus faible.


### Comportement comparé des deux modèles

CamemBERT produit des embeddings relativement plus « concentrés » : les cosinus moyens restent globalement élevés, entre environ 0.69 et 0.92 selon les mots. Cette concentration permet de mieux interpréter les différences de dispersion entre les cibles. Par exemple, baron présente une moyenne très élevée (0.920) et un écart-type très faible (cosine_std = 0.040), ce qui correspond bien à son rôle de contrôle à faible polysémie. À l’inverse, des mots comme voix, pied, cour, porte ou feu obtiennent des écarts-types plus élevés, entre 0.114 et 0.141, ce qui suggère une plus forte variation contextuelle.

FlauBERT, en revanche, produit des embeddings globalement plus dispersés : les cosinus moyens sont plus bas, entre environ 0.48 et 0.63, et les écarts-types sont beaucoup plus resserrés, autour de 0.215 à 0.250. Cette dispersion générale rend le score cosine_std moins discriminant entre les cibles. Par exemple, avec FlauBERT, baron obtient un score de 0.239, proche de celui de mots plus variables comme passer (0.239) ou porte (0.250). Cela rend l’interprétation linguistique moins nette que pour CamemBERT.

Ainsi, dans notre protocole, CamemBERT est retenu comme modèle principal d’analyse, non parce qu’il serait nécessairement supérieur à FlauBERT de manière générale, mais parce qu’il produit ici une hiérarchie plus interprétable pour notre score de dispersion. FlauBERT est conservé comme point de comparaison, mais ses scores semblent davantage refléter une dispersion globale de l’espace vectoriel qu’une distinction claire entre les degrés de polysémie des mots cibles.

## Discussion des résultats

### Score de polysémie : rappel de la mesure

Le classement obtenu avec CamemBERT montre que certains mots, comme `voix` (0.141), `pied` (0.125), `cour` (0.124), ou encore `feu` (0.114), présentent des scores, l'**écart-type des similarités cosinus 2-à-2**, de dispersion relativement élevés. Ces valeurs indiquent une plus grande variation contextuelle des embeddings, que l’on peut rapprocher d’une plus grande diversité sémantique.

D’un point de vue linguistique, cette variation peut être mise en relation avec l’idée que le sens d’un mot ne dépend pas uniquement de son contenu lexical isolé, mais aussi de son environnement linguistique. Dans sa thèse, Évelyne Saunier montre notamment que l’interprétation d’un mot se construit en interaction avec le contexte dans lequel il apparaît : le mot joue un rôle précis dans l’interprétation de l’énoncé où il figure. Cette perspective permet de mieux comprendre pourquoi un même terme peut recevoir des valeurs différentes selon ses emplois.

Par exemple, `voix` peut renvoyer, selon le contexte, au son produit par la parole, à une opinion ou à une forme d’influence. De même, `pied` peut désigner une partie du corps, une base ou apparaître dans des expressions figées. `Cour` peut renvoyer à un espace extérieur, à une cour royale ou à l’expression « faire la cour ». Ces variations d’usage expliquent pourquoi ces mots obtiennent des scores de dispersion plus élevés avec CamemBERT.

Cependant, certains cas intéressants, comme `passer`, `entendre`, `porte` et `campagne`, montrent aussi les limites du score. Ces mots ne se laissent pas interpréter uniquement à partir de leur rang dans le classement, car leur dispersion dépend à la fois de leur polysémie, de leurs constructions syntaxiques et des usages effectivement présents dans le corpus.

Le cas de `passer` est révélateur. D’un point de vue linguistique, l’invariant de `passer` peut être compris comme l’idée d’un passage ou d’une transition, c’est-à-dire le fait de minimiser une rupture en l’inscrivant dans un mouvement continu. Cette valeur générale explique que le verbe puisse s’appliquer à des déplacements physiques, à des successions temporelles ou encore à des transmissions d’objets. Pourtant, dans nos résultats, `passer` n’obtient pas un score aussi élevé que certains noms comme `voix`, `pied` ou `cour`. Cela peut s’expliquer par le fait que notre extraction porte sur la forme exacte `passer`, et non sur l’ensemble des formes conjuguées du verbe. Le score mesure donc la dispersion des occurrences réellement extraites, et non toute la richesse sémantique du lemme.

`Entendre` présente une autre limite. Le mot est principalement associé à deux grands emplois, percevoir par l’ouïe et comprendre, mais il obtient malgré tout un score relativement élevé. Cela montre que le score peut aussi être sensible à la diversité des contextes syntaxiques ou discursifs, et pas seulement au nombre de sens distingués linguistiquement. `Porte` est également un cas problématique, car la forme peut correspondre au nom `porte`, mais aussi à une forme conjuguée du verbe `porter`. Son score élevé peut donc refléter une véritable variation sémantique, mais aussi une ambiguïté morphosyntaxique. Sans lemmatisation ni étiquetage grammatical, le score mélange ces différents emplois.

Enfin, `campagne` obtient un score plus faible, alors que le mot possède au moins deux grands sens : l’espace rural et la campagne militaire ou politique. Cela suggère que certains sens sont peut-être moins représentés dans le corpus, ou que les occurrences extraites restent proches dans leurs contextes d’emploi. Ce cas rappelle que notre score ne mesure pas directement le nombre de sens disponibles dans une ressource lexicale, mais la variation des usages observés dans le corpus.

### Corrélation avec la mesure externe

Afin d’évaluer si le score `cosine_std` correspond à une mesure linguistique de la polysémie, nous l’avons comparé à une mesure externe fondée sur des macro-sens. Chaque mot cible a reçu un score externe correspondant au nombre de grands emplois distingués manuellement : par exemple, `baron` reçoit un score faible, tandis que `feu` ou `passer` reçoivent un score plus élevé.

La corrélation obtenue est positive mais modérée : Spearman ρ = 0.422 qui compare les rangs, notamment l'ordre des mots dans les deux classements; et Pearson r = 0.603 qui compare les valeur numériques,  indiquent que les mots associés à davantage de macro-sens tendent globalement à avoir des embeddings plus dispersés. Cependant, les p-values obtenues ne permettent pas de conclure à une corrélation statistiquement significative. Cette absence de significativité peut s’expliquer par la taille réduite de notre échantillon, limité à neuf mots.

Ces résultats suggèrent donc que le score fondé sur les embeddings contextuels correspond partiellement à la polysémie linguistique, sans s’y réduire complètement. Il mesure plutôt la dispersion des usages attestés dans le corpus, qui dépend à la fois du nombre de sens possibles, de leur fréquence dans les textes et de la diversité des contextes dans lesquels les mots apparaissent.

### Mesure externe par macro-sens

Nous avons choisi de comparer notre score à une mesure externe fondée sur des macro-sens plutôt qu’à un décompte exhaustif des acceptions dictionnairiques. Ce choix permet de regrouper des nuances proches dans de grands emplois sémantiques plus facilement comparables aux représentations distributionnelles. Les dictionnaires distinguent souvent des sous-sens très fins, qui ne correspondent pas nécessairement à des groupes séparables dans l’espace des embeddings.

Cette mesure reste donc volontairement simplifiée. Elle ne prétend pas épuiser la polysémie des mots étudiés, mais elle fournit un point de comparaison linguistique permettant de tester si les mots considérés comme plus polysémiques présentent aussi une plus grande dispersion contextuelle.

### Observations

Cette étude met en évidence que la dispersion des embeddings contextuels permet d’approcher partiellement la variation sémantique des mots en contexte, mais qu’elle ne correspond pas directement à une mesure exhaustive de la polysémie. On peut constater diverses observations qui vont ensuite nous permettre de relever les limites de notre étude :

**1. CamemBERT : une hiérarchie interprétable.**  
`Baron`, utilisé comme contrôle à faible polysémie dans le corpus littéraire, obtient le score le plus faible (`cosine_std` = 0.040). À l’inverse, `voix` (0.141), `pied` (0.125), `cour` (0.124), `porte` (0.116) et `feu` (0.114) obtiennent les scores les plus élevés. Le score de `voix` est ainsi environ 3,5 fois supérieur à celui de `baron`, et ceux de `pied` et `cour` environ trois fois supérieurs.

Cet écart est clair et linguistiquement motivé : `baron` renvoie majoritairement à un noble ou à une personne appelée ainsi, tandis que les autres mots présentent des emplois plus variés. CamemBERT permet donc de distinguer un mot relativement homogène de mots à plus forte variation contextuelle.


**2. FlauBERT : une dispersion moins discriminante.**  
Avec FlauBERT, les scores `cosine_std` sont plus resserrés entre les mots. `Baron` obtient par exemple un score de 0.239, très proche de `passer` (0.239) et de `porte` (0.250). Cette proximité est problématique, car `baron` devait fonctionner comme contrôle à faible polysémie. Contrairement à CamemBERT, FlauBERT ne distingue donc pas nettement les mots attendus comme homogènes des mots plus variables. Dans notre protocole, ses embeddings semblent présenter une dispersion générale plus forte, ce qui rend le score moins discriminant pour l’analyse de la polysémie.

**3. La mesure ne se corrèle pas directement avec le nombre de sens lexicographiques.**  
D'après le Wiktionnaire, `esprit` possède **13 acceptions** et `porte` **11** — soit légèrement plus pour `esprit`. Pourtant, CamemBERT classe `porte` *devant* `esprit` (run `resultats_1` : 0.094 vs 0.065). Deux facteurs l'expliquent :
- `porte` est aussi une **forme verbale** de *porter* (présent 1re/3e sg.) : sans filtrage POS, le modèle mélange les contextes nominaux et verbaux, ce qui gonfle artificiellement la dispersion.
- Les acceptions d'`esprit` dans un corpus littéraire restent dans un champ thématique étroit (intellect, pensée, caractère) ; les sens plus marginaux (Esprit-Saint, esprits chimiques…) sont peu représentés.

**4. Validation qualitative par les paires extrêmes (`porte`, CamemBERT).**  
Les paires d'occurrences les plus *éloignées* (cos ≈ 0.43) opposent bien des usages distincts :
- *sens nominal concret* : « il vit une **porte** ouverte et prit vivement la main d'emilie »
- *emploi verbal* : « celui de mont franklin à ce lac nous **porte** en ce moment »

Les paires les plus *proches* (cos ≈ 0.97) sont toutes au sens nominal physique (battant de porte). Ce contraste confirme que la dispersion reflète une vraie variation sémantique — même si une partie est imputable à l'ambiguïté POS.

### Limites de l’étude (à completer ou réformuler)

- Cette étude présente plusieurs limites. La première concerne la taille de l’échantillon : l’analyse finale porte sur neuf mots cibles, ce qui permet d’observer des tendances, mais limite la portée statistique des résultats. Cela explique notamment que les corrélations obtenues avec la mesure externe soient positives, mais non significatives.

- Une deuxième limite tient au choix d’une extraction par formes lexicales exactes, sans lemmatisation ni étiquetage morphosyntaxique. Les différentes formes fléchies d’un même verbe ne sont donc pas regroupées, et certaines formes ambiguës peuvent mélanger plusieurs catégories grammaticales. C’est notamment le cas de `porte`, qui peut correspondre au nom ou à une forme du verbe `porter`.

- Les résultats dépendent également du corpus utilisé. Notre corpus littéraire et argumentatif offre une diversité d’emplois, mais il ne couvre pas nécessairement tous les sens possibles des mots. Le score mesure donc les usages attestés dans ce corpus, et non la polysémie complète d’un mot dans la langue.

- Enfin, le score `cosine_std` doit être interprété avec prudence. Il mesure une dispersion des embeddings contextuels, qui peut refléter la polysémie, mais aussi des différences syntaxiques, stylistiques ou thématiques. Les différences observées entre CamemBERT et FlauBERT montrent également que cette mesure dépend de la géométrie propre au modèle utilisé.

