# Sémantique distributionnelle - mini-projet
> Catalina Alvarez Ortega & Morgane Bona-Pellissier (Master 1 pluriTAL)

## Introduction 

Dans le cadre du cours de Sémantique distributionnelle, nous avons été amenées à étudier la polysémie à l’aide d’embeddings contextuels (ou « dynamiques »). Il existe différentes notions liées à la polysémie, notamment la distinction entre polysémie régulière et polysémie irrégulière. De manière générale, elle désigne la capacité d’un mot à prendre plusieurs sens selon ses contextes d’emploi [CITATION]. Par exemple, un mot comme « voix » peut désigner le son produit par la parole, mais aussi une opinion ou une forme d’influence. Les modèles de langage basés sur l'architecture Transformers, comme BERT (*Bidirectional Encoder Representations from Transformers*), sont particulièrement adaptés à l’étude de ce phénomène, car, comme nous le verrons, ils ne produisent pas une représentation unique et fixe pour un mot donné. Au contraire, la représentation vectorielle d’un mot dépend du contexte dans lequel chaque occurrence apparaît. Ainsi, deux occurrences d’un même mot peuvent recevoir des embeddings différents si elles sont employées dans des sens ou des environnements sémantiques distincts.

L’objectif de ce projet a été d’évaluer dans quelle mesure cette variation vectorielle pouvait être interprétée comme un indice de polysémie. Pour cela, nous avons travaillé à partir d’un corpus de 29 romans français au format `.txt` et d’une liste de mots cible, comprenant des noms et des formes verbales dont les différents sens respectifs étaient suffisamment attestés au sein du corpus. Pour chaque mot, nous avons extrait plusieurs occurrences en contexte, puis nous les avons encodées avec des modèles BERT pour le français. Nous avons ensuite défini un score de polysémie fondé sur l’écart-type des similarités cosinus deux à deux entre les embeddings des occurrences d’un même mot. Un score élevé indique une forte dispersion des représentations, tandis qu’un score faible indique des usages plus homogènes. Afin de déterminer si ce score correspondait effectivement à la notion linguistique de polysémie, nous l’avons confronté à une mesure externe fondée sur des macro-sens. Nous avons également utilisé des visualisations 2D par réduction de dimensionnalité afin d’observer qualitativement la distribution des occurrences dans l’espace vectoriel.


## Hypothèses

Nous faisons l’hypothèse que les mots fortement polysémiques ou employés dans des contextes sémantiquement variés auront des embeddings contextuels plus dispersés. Cette dispersion devrait se traduire par un score de polysémie plus élevé, calculé à partir de l’écart-type des similarités cosinus entre occurrences d’un même mot. À l’inverse, les mots dont les emplois sont plus homogènes devraient obtenir un score plus faible.

## Structure du pipeline
> L'intégralité du pipeline est consultable à l'adresse : https://github.com/crispyfunicular/semantique-distributionnelle/tree/main/mini_projet

- `1.normalisation_corpus.py` : homogénéise le corpus (apostrophes, ligature `œ`, etc.) pour réduire le bruit typographique et éviter les doublons de tokens avant l’extraction.
- `2.extraire_occurrences.py` : extrait des occurrences exactes des mots cibles avec une fenêtre de contexte \(`k=10` mots à gauche/droite\) et en conserve au plus `n=100` par cible (échantillonnage reproductible via `seed=42`).
- `3.encoder_embeddings.py` : encode chaque occurrence avec CamemBERT et/ou FlauBERT (dernière couche, sans fine-tuning) et associe chaque occurrence à sa ligne dans les matrices d’embeddings via `embeddings_meta.jsonl`.
- `4.score_polysemie.py` : calcule, pour chaque mot et modèle, la dispersion des similarités cosinus 2-à-2 (score principal : `cosine_std`) et produit `polysemy_scores.json` (stats) et `polysemy_ranking.json` (classement).
- `5.visualiser_2d.py` (optionnel, pour l’oral) : visualise en 2D les occurrences d’un mot cible (PCA par défaut, UMAP si installé) et exporte un PNG.


## Choix méthodologiques effectués
### Choix du corpus
Notre corpus rassemble 29 œuvres littéraires françaises, couvrant des thèmes et des époques variés, ce qui devrait favoriser des contextes d’emploi divers pour les mots cibles (concrets, abstraits, figurés, etc.). Toutefois, notre mesure ne porte que sur les sens effectivement attestés dans ce corpus : un mot peut être très polysémique en dictionnaire mais apparaître ici dans des usages plus restreints. Enfin, nous avons travaillé sur des formes graphiques exactes afin de conserver les formes fléchies telles qu’elles apparaissent dans le corpus (par ex. `porte`), plutôt que de les ramener au lemme (`porter`) et de préserver l’ambiguïté nom/verbe susceptible d’influencer la dispersion des embeddings.
En outre, le paramètre `k` correspond au nombre de mots conservés autour du mot cible. Dans notre run final, nous avons retenu `k = 10`, soit dix mots à gauche et à droite de chaque occurrence. Ce choix s’appuie sur les réflexions du TP2, consacré à l’influence de la taille du contexte dans les représentations distributionnelles. Ce TP montrait que la taille de la fenêtre pouvait modifier les voisins obtenus par similarité cosinus et donc les propriétés linguistiques capturées. Même si notre projet utilise des embeddings contextuels BERT plutôt que des embeddings statiques par cooccurrences, la taille du contexte reste importante : une fenêtre trop courte peut manquer d’indices sémantiques, tandis qu’une fenêtre trop large peut introduire du bruit. La fenêtre de dix mots constitue donc un compromis.

### Choix des mots
Les noms `porte`, `feu`, `pied`, `cour`, `voix` et `campagne` présentent des emplois concrets, abstraits, institutionnels ou figurés. Les verbes `passer` et `entendre` sont également susceptibles de varier selon leur construction et leur contexte. Enfin, `baron` est utilisé comme contrôle à faible polysémie, car il devrait renvoyer majoritairement, dans ce corpus littéraire, à une personne portant ce titre nobiliaire.

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

### Choix des modèles : CamemBERT et FlauBERT
Nous avons utilisé deux modèles BERT adaptés au français : CamemBERT et FlauBERT. Ces modèles sont tous deux des encodeurs contextuels : ils produisent, pour un même mot, des représentations vectorielles différentes selon le contexte d’occurrence. C’est précisément cette propriété que nous exploitons pour mesurer la variation sémantique.

| | **CamemBERT** | **FlauBERT** |
|---|---|---|
| Référence | Martin et al. (2019) | Le et al. (2020) |
| Architecture de base | RoBERTa (encodeur Transformer) | Transformer encodeur (XLM-like) |
| Données d'entraînement | OSCAR + Wikipedia FR (~138 Go) | CCNet FR (~71 Go, filtré par perplexité) |
| Tokenisation | SentencePiece BPE (~32k tokens) | BPE (~68k tokens) |
| Dimension des embeddings | 768 | 768 |
| Couches / têtes d'attention | 12 / 12 | 12 / 12 |

Nous utilisons ces modèles sans fine-tuning : les embeddings sont extraits directement à partir de la dernière couche cachée. Pour chaque occurrence, nous récupérons la représentation du mot cible. Lorsque le mot est segmenté en plusieurs sous-tokens, les vecteurs correspondants sont moyennés afin d’obtenir un seul embedding par occurrence.

Nous avons testé CamemBERT et FlauBERT sans fine-tuning. Pour l’analyse finale, nous retenons CamemBERT comme modèle principal ; la comparaison chiffrée des deux modèles est présentée ci-dessous.



### Comportement comparé des deux modèles

Sur notre run final, **CamemBERT** produit des embeddings relativement plus « concentrés » : les cosinus moyens sont élevés (≈ 0.69–0.92) et les dispersions `cosine_std` s’étendent de 0.040 à 0.141. Il discrimine donc nettement les cibles : `baron` apparaît comme le plus homogène (cosine_mean ≈ 0.920 ; `cosine_std` = 0.040), tandis que des mots comme `voix` (`cosine_std` = 0.141), `pied` (0.125) ou `cour` (0.124) présentent une plus forte variation contextuelle.

**FlauBERT**, à l’inverse, donne des cosinus moyens plus faibles (≈ 0.48–0.63) et des dispersions beaucoup plus resserrées (≈ 0.216–0.250), ce qui rend le score moins discriminant : `baron` (`cosine_std` = 0.239) est proche de `passer` (0.239) et `porte` (0.250). Dans notre protocole, **nous retenons donc CamemBERT comme modèle principal**, car l'écart entre les valeurs extrêmes de cosine_std est nettement plus large, ce qui permet de hiérarchiser les mots de façon plus lisible. Enfin, rappelons que ce score ne « compte » pas les sens lexicographiques mais reflète surtout la diversité des contextes dans le corpus et peut par conséquent être affecté par des ambiguïtés morphosyntaxiques (par ex. `porte`, nom ou forme verbale).

## Discussion des résultats

### Scores de polysémie

Le classement obtenu avec CamemBERT montre que certains mots, comme `voix` (0.141), `pied` (0.125), `cour` (0.124), ou encore `feu` (0.114), présentent des scores de dispersion (écart-type des similarités cosinus 2-à-2) relativement élevés. Ces valeurs indiquent une plus grande variation contextuelle des embeddings, que l’on peut rapprocher d’une plus grande diversité sémantique.

D’un point de vue linguistique, cette variation peut être mise en relation avec l’idée que le sens d’un mot ne dépend pas uniquement de son contenu lexical pris en isolation, mais aussi de son environnement linguistique. Dans sa thèse, Évelyne Saunier (1996) montre notamment que l’interprétation d’un mot se construit en interaction avec le contexte dans lequel il apparaît : le mot joue un rôle précis dans l’interprétation de l’énoncé où il figure. Cette perspective permet de mieux comprendre pourquoi un même terme peut recevoir des valeurs différentes selon ses emplois.

Par exemple, `voix` peut renvoyer, selon le contexte, au son produit par la parole, à une opinion ou à une forme d’influence. De même, `pied` peut désigner une partie du corps, une base ou apparaître dans des expressions figées. `Cour` peut renvoyer à un espace extérieur, à une cour royale ou à l’expression « faire la cour » [IDEALEMENT, CITER LES DICTIONNAIRES D'OU SONT TIREES CES DEFINITIONS]. Ces variations d’usage expliquent pourquoi ces mots obtiennent des scores de dispersion plus élevés avec CamemBERT.

Cependant, certains cas intéressants, comme `passer`, `entendre`, `porte` et `campagne` montrent aussi les limites du score. Ces mots ne se laissent pas interpréter uniquement à partir de leur rang dans le classement, car leur dispersion dépend à la fois de leur polysémie, des constructions syntaxiques et des usages effectivement présents dans le corpus.

Le cas de `passer` est révélateur. D’un point de vue linguistique, ce verbe peut décrire des déplacements physiques, à des successions temporelles ou encore à des transmissions d’objets. Pourtant, dans nos résultats, `passer` n’obtient pas un score aussi élevé que certains noms comme `voix`, `pied` ou `cour`. Cela peut s’expliquer par le fait que notre extraction porte sur la forme exacte `passer` (la forme fléchie à l'infinitif), plutôt que sur l’ensemble des formes conjuguées du verbe. Le score mesure donc la dispersion des occurrences réellement extraites, et non toute la richesse sémantique du lemme.

Le mot `entendre` présente une autre limite. Il est principalement associé à deux grands emplois, percevoir par l’ouïe et comprendre, mais il obtient malgré tout un score relativement élevé. Cela montre que le score peut aussi être sensible à la diversité des contextes syntaxiques ou discursifs, et pas seulement au nombre de sens distingués linguistiquement. `Porte` est également un cas problématique, car la forme peut correspondre au nom `porte`, mais aussi à une forme conjuguée du verbe `porter`. Son score élevé peut donc refléter une véritable variation sémantique, mais aussi une ambiguïté morphosyntaxique. Sans lemmatisation ni étiquetage grammatical, le score mélange ces différents emplois.

Enfin, `campagne` obtient un score plus faible, alors que le mot possède au moins deux grands sens : l’espace rural et la campagne militaire ou politique. Cela suggère que certains sens sont peut-être moins représentés dans le corpus, ou que les occurrences extraites restent proches dans leurs contextes d’emploi. Ce cas rappelle que **notre score ne mesure pas directement le nombre de sens disponibles dans une ressource lexicale, mais la variation des usages observés dans le corpus**.

### Mesure externe par macro-sens

Afin d’évaluer si le score `cosine_std` reflète la polysémie, nous l’avons comparé à une mesure externe fondée sur des **macro-sens**. Chaque mot cible reçoit un score égal au nombre de grands emplois distingués manuellement (p. ex. `baron` a un score faible, tandis que `feu` ou `passer` ont un score plus élevé).

Nous utilisons des macro-sens plutôt qu’un comptage détaillé d’acceptions de dictionnaire, car les dictionnaires distinguent souvent des sous-sens très fins, difficiles à retrouver comme groupes séparés dans l’espace des embeddings. Cette mesure sert donc surtout de **repère** (et non de description exhaustive) pour tester si les mots jugés plus polysémiques tendent aussi à présenter une plus grande dispersion contextuelle.

La corrélation obtenue est positive mais modérée. Le coefficient de Spearman (ρ = 0.422), qui compare les rangs (c’est-à-dire l’ordre des mots dans les deux classements), et le coefficient de Pearson (r = 0.603), qui compare les valeurs numériques, vont dans le même sens : les mots associés à davantage de macro-sens ont tendance à présenter des embeddings plus dispersés. Cependant, les p-values obtenues ne permettent pas de conclure à une corrélation statistiquement significative. Cette absence de significativité peut s’expliquer par la taille réduite de notre échantillon, limité à neuf mots.

Ces résultats suggèrent donc que **le score fondé sur les embeddings contextuels est lié à la polysémie**, mais qu’il reflète plus largement la dispersion des usages attestés dans le corpus (fréquence des emplois, diversité des contextes, etc.).


### Limites de l’étude

- Cette étude présente plusieurs limites. La première concerne la taille de l’échantillon : l’analyse finale porte sur neuf mots cible, ce qui permet d’observer des tendances, mais limite la portée statistique des résultats.

- Une deuxième limite tient au choix d’une extraction par formes lexicales exactes, sans lemmatisation ni étiquetage morphosyntaxique. Les différentes formes fléchies d’un même verbe ne sont donc pas regroupées, et certaines formes ambiguës peuvent mélanger plusieurs catégories grammaticales. C’est notamment le cas de `porte`, qui peut correspondre au nom ou à une forme du verbe `porter`.

- Les résultats dépendent également du corpus utilisé. Notre corpus littéraire et argumentatif offre une diversité d’emplois, mais il ne couvre pas nécessairement tous les sens possibles des mots. Le score mesure donc les usages attestés dans ce corpus, et non la polysémie complète d’un mot dans la langue.

- Enfin, le score `cosine_std` doit être interprété avec prudence. Il mesure une dispersion des embeddings contextuels, qui peut refléter la polysémie, mais aussi des différences syntaxiques, stylistiques ou thématiques. Les différences observées entre CamemBERT et FlauBERT montrent également que cette mesure dépend de la géométrie propre au modèle utilisé.


## Bibliographie

## Annexes

### Citations : un exemple par macro-sens

Les citations ci-dessous sont reprises de `liste_termes_polysemiques.md` et illustrent, pour chaque mot du run 9, des emplois correspondant à des macro-sens distincts.

#### `porte`
- **nom (objet / ouverture)** : « la raie de jour qui était sous sa porte a disparu »
- **verbe (porter physiquement)** : « le héron les guette.... les saisit.... les porte à son nid.... »
- **tour “porter à” (inciter / pousser à)** : « aucun besoin d'expansion qui me porte à parler de mon présent ou de mon passé »

#### `pied`
- **membre inférieur** : « marchant sur la pointe des pieds »
- **unité de mesure** : « un mur de vingt pieds de hauteur et de trente ou quarante toises de long »

#### `entendre`
- **percevoir par l’ouïe** : « nous n'entendîmes plus que ses sanglots »
- **comprendre** : « Je n'entends pas ce que Monsieur veut dire »

#### `cour`
- **espace extérieur d’une demeure** : « Nous traversâmes une cour intérieure. »
- **entourage royal / courtisans** : « toute la Cour se trouva à Paris »
- **séduction (“faire la cour”)** : « Julien lui fit la cour en lui demandant des explications sur la généalogie des meilleures familles de la Bourgogne »

#### `voix`
- **son produit par la parole** : « Sa voix était si douce, que j'osai lever les yeux et la regarder: la sérénité de son visage, son sourire, me rendirent le calme et l'assurance. »
- **opinion / influence (“avoir voix…”, “voix publique”)** : « à tous ces titres, je dois avoir voix au chapitre, et surtout dans l'affaire d'aujourd'hui. »

#### `passer`
- **traverser un lieu** : « A peine avions-nous ouvert la porte des orchestres que nous fûmes forcés de nous arrêter pour laisser passer Marguerite et le duc qui s'en allaient. »
- **temps qui s’écoule** : « Je passai le reste du jour, la nuit entière, à y penser. »
- **laisser passer / pardonner / autoriser** : « je crois devoir laisser passer ces premiers jours sans chercher à la voir. »

#### `campagne`
- **espace rural** : « Je ne suis arrivé ici qu'avant-hier, mon cher Henri; et déjà notre ambassadeur veut me mener passer quelques jours à la campagne, »
- **expédition militaire / politique** : « Il avait fait toutes les campagnes de Buonaparté en Italie; »

#### `feu`
- **combustion / foyer (chauffage, cuisine)** : « Mme Demaille le faisant asseoir près du feu, déficelait devant lui deux paquets noués de faveurs bleues ou roses »
- **incendie (mettre le feu)** : « On raconte que mon arrière-grand-père, en 1789, mit le feu au théâtre de Rouen »

#### `baron`
- **titre nobiliaire (personne)** : « M. le baron Haussmann nous aère—mais on ne s'y retrouve plus, dans son Paris. »
- **nom propre (titre dans un nom figé)** : « comme avait coutume de dire le Baron Louis. »
