# TP3 - Correction des biais
**Morgane Bona-Pellissier**, Master 1 pluriTAL  
morgane@bona-pellissier.net  

L’ensemble de ce projet est disponible sur le dépôt suivant : `https://github.com/crispyfunicular/semantique-distributionnelle/tp3`

## Choix du corpus
Après quelques essais infructueux pour mettre en évidence le *male gaze* dans un corpus d’auteurs français (les résultats s’étant révélés peu parlants), nous nous sommes tournée vers deux auteurs anglophones ayant dépeint dans leurs œuvres la vie dans l’Empire britannique, à savoir **Rudyard Kipling** (1865-1936) et **Joseph Conrad** (1857-1924). Afin de maximiser nos résultats et de ne pas bruiter inutilement le corpus, nous avons délibérément restreint notre sélection aux seules œuvres de ces auteurs portant sur les colonies. Les romans sélectionnés pour le corpus sont donc les suivants :

**Joseph Conrad** : *Heart of Darkness* (1899), *Victory: An Island Tale* (1915), *Lord Jim* (1900), *The Nigger of the “Narcissus”* (1897), *An Outcast of the Islands* (1896), *Typhoon* (1902).

- Nombre de tokens (corpus brut) : 476 872
- Nombre de tokens (corpus lemmatisé) : 462 434

**Rudyard Kipling** : *In Black and White* (1888), *Under the Deodars* (1888), *The Story of the Gadsbys* (1888), *Plain Tales from the Hills* (1888), *The Jungle Book* (1894), *The Second Jungle Book* (1895), *Kim* (1901), *The Man Who Would Be King* (1888), *Life’s Handicap: Being Stories of Mine Own People* (1891), *The Light That Failed* (1891), *From Sea to Sea: Letters of Travel* (1899), *Soldiers Three* (1888).

- Nombre de tokens (corpus brut) : 939 527
- Nombre de tokens (corpus lemmatisé) : 923 778

L’ensemble de ces textes ont été récupérés manuellement sur le site du Projet Guthenberg (https://www.gutenberg.org/).

### Hypothèse
Nous espérons que ce corpus de littérature impériale nous permettra de mettre en évidence les stéréotypes coloniaux et racistes de l’époque victorienne. Pour ce faire, nous avons cherché spécifiquement des analogies pouvant capturer ces biais, telles que :
- `man - english + native = ?`
- `human - white + black = ?`
- `master - english + native = ?`
- `wisdom - english + native = ?`
- `light - white + black = ?`

## Structure de la pipeline

Le pipeline est composé d’une succession de trois scripts :
1. **`nettoyage.py`** : pour préparer le corpus brut en supprimant les métadonnées et licences du Projet Gutenberg, en normalisant la typographie (apostrophes) et en fusionnant les sauts de ligne.
2. **`lemmatisation.py`** : pour lemmatiser le corpus avec le modèle `en_core_web_lg` de spaCy (anglais - large)
3. **`tp3.py`** : pour entraîner le modèle GloVe sur le corpus lemmatisé, tester la présence de biais coloniaux à travers de la résolution d’analogies et appliquer deux méthodes de débiaisage. Nous avons utilisé la librairie `Mittens` pour générer nos plongements lexicaux avec GloVe.

La structure de ce pipeline a été créée par nos soins et les scripts en eux-mêmes ont été codés à l’aide de `Claude Opus 4.6 (Thinking)`.

### Matrice
Nous avons rassemblé 17 concepts coloniaux sous forme de liste. Pour chacun de ces concepts, nous appliquons l’équation vectorielle `concept − mot_moins + mot_plus = ?`, en mettant en regard des termes associés à la Couronne britannique, “english” et “white” (`MOT_MOINS = [“english”, “white”]`), et des termes associés aux colonies, “native” et “brown” (`MOT_PLUS  = [“native”, “brown”]`), générant ainsi une matrice de 17 x 2 x 2 = 68 analogies.

```python
CONCEPTS_COLONIAUX = [
    # Humanité
    "man", "master", "human", "soul",
    # Raison / intelligence
    "mind", "wisdom", "think", "understand",
    # Ordre / civilisation
    "law", "order", "rule",
    # Espaces
    "home", "empire", "city",
    # Force / courage
    "brave", "soldier",
]

MOT_MOINS = ["english", "white"]
MOT_PLUS  = ["native", "brown"]
```

## Discussion des résultats

> Les résultats complets sont disponibles dans `resultats/corpus_lemmes_comparatif_triple.md`.

### Biais coloniaux mis en évidence par GloVe dans le corpus de départ

Les associations sémantiques de GloVe à partir du corpus de départ (non modifié) mettent en évidence deux dichotomies entre colons et colonisés : d’une part, l’opposition entre **l’esprit et le corps**, d’autre part celle entre **l’ordre et le chaos**.

#### Déshumanisation des populations dominées
Tout d’abord, le résultat le plus frappant est sans doute **`soul − english + native = body`** (similarité cosinus de 0,625), que l’on observe également avec `soul − white + brown = body` (0,682) ou encore `mind − white + brown` = `body` (0,594). Que l’on oppose *english* à *native* ou *white* à *brown*, l’autochtone est dans tous les cas réduit à son enveloppe corporelle dépourvue de psyché. Le groupe dominant *pense*, le groupe colonisé *ressent*.

Ces résultats résonnent pleinement avec la pensée coloniale victorienne, dont l’un des rouages fondamentaux était précisément la déshumanisation des populations dominées pour justifier l’impérialisme. Ainsi, dans ses travaux, Edward **Said** (1978) explique que l’Occident a façonné une image fictive de l’Orient afin de s’ériger en unique garant de la raison et de la civilisation. De son côté, Homi **Bhabha** (1994) démontre que l’usage systématique de stéréotypes visait à réduire l’individu colonisé à sa seule dimension biologique et corporelle. En niant la complexité intellectuelle et spirituelle de l’Autre, le discours colonial légitime de fait son asservissement.

#### Loi de la jungle
Ensuite, **`law − english + native = jungle`** (0,559) est l’illustration parfaite du vers “Now is the **law of the jungle**”, issu du *Livre de la jungle* de Kipling. Dans cette analogie, l’ordre colonial civilisé s’oppose à un espace indigène présenté comme naturellement chaotique. Dans cette même imaginaire colonial, l’analogie **`city − english + native = dreadful`** (0,618) présente la ville colonisée comme effroyable (au premier sens du terme), quand la ville britannique est un lieu d’ordre et de régulation.
> « Now is the law of the jungle, as old and as true as the sky, / And the wolf that shall keep it may prosper, but the wolf that shall break it must die ».

Ces biais font écho au *les Damnés de la terre*, essai dans lequel Frantz Fanon explique comment le monde colonial est divisé en deux :
> « Le secteur du colonisé, ou du moins la “ville” indigène, le village nègre, la médina, la réserve, est un lieu mal famé, peuplé d’hommes mal famés ».

#### Exemples
| Équation d’analogie | Première association | Score cosinus |
| :--- | :--- | :--- |
| `soul − english + native` | **body** | 0,625 |
| `mind − english + native` | **nothing** | 0,633 |
| `law − english + native` | **jungle** | 0,559 |
| `city − english + native` | **dreadful** | 0,618 |

### Échec du CDA : quand l’inversion renforce le stéréotype
Afin d’atténuer les biais coloniaux mis en évidence dans le corpus initial, nous avons eu recours à la méthode d’augmentation de données par contrefactuels (CDA). Dans ce cadre, nous avons créé un corpus alternatif en inversant symétriquement les termes polarisés. À l’aide d’un dictionnaire Python, nous avons par exemple remplacé chaque occurrence de english par native, et inversement. Ce corpus miroir, une fois combiné au texte d’origine, a pour but de neutraliser ces dichotomies et de forcer le modèle à apprendre une géométrie vectorielle plus équilibrée.

```python
PAIRES_BIAIS = [
    # Kipling : hiérarchie coloniale (Inde)
    ("english",   "native"),
    ("white",     "brown"),
    ("sahib",     "servant"),
    ("england",   "india"),
    # Conrad : biais racial et moral (Afrique)
    ("white",     "black"),
    ("light",     "darkness"),
    ("civilized", "savage"),
]
```

```python
def generer_dico_cda(paires_biais: list = None) -> dict:
    if paires_biais is None:
        paires_biais = PAIRES_BIAIS
    dico = {}
    for a, b in paires_biais:
        if a not in dico:
            dico[a] = b
        if b not in dico:
            dico[b] = a
    return dico
```

```python
def inverser_corpus(corpus_lemmatise: list, dico_cda: dict) -> list:
    """Génère un nouveau corpus en inversant les termes coloniaux polarisés."""
    corpus_inverse = []
    for phrase in corpus_lemmatise:
        phrase_inverse = [dico_cda.get(mot, mot) for mot in phrase]
        corpus_inverse.append(phrase_inverse)
    return corpus_inverse
```

```python
# Concaténation et entraînement
corpus_augmente = corpus_propre + corpus_inverse
modele_cda = entrainer_glove(corpus_augmente, taille_fenetre=10, dimensions=100)
```

Toutefois, les résultats obtenus n’ont guère été encourageants. En effet, paradoxalement, la plupart des biais sont restés inchangés et certains scores cosinus ont même augmenté : `soul − english + native = body` passe de 0,625 à 0,829, `law − english + native = jungle` de 0,559 à 0,788 et `city − english + native = dreadful` de 0,618 à 0,805.

En dupliquant le texte pour inverser les dichotomies, nous avons doublé la fréquence des termes connotés (*jungle*, *dreadful*, *body*) dans l’environnement immédiat des mots polarisés. Ainsi, puisque les termes *english* et *native* apparaissent désormais dans des contextes strictement identiques, leurs vecteurs respectifs fusionnent. L’analogie `soul − english + native = body` se réduit alors à `soul − english + english = body` ou `soul − native + native = body`, soit `soul = body`, les vecteurs s’annulant. Ce faisant, loin de neutraliser les biais coloniaux visés, la méthode CDA les a tout bonnement renforcés et se révèle totalement contre-productif. Ces biais ne semblent donc pas ici relever d’un simple problème d’asymétrie ou de déséquilibre des fréquences mais imprègnent l’intégralité du corpus.

#### Exemples
| Analogie | Standard (score) | CDA (score) |
| :--- | :--- | :--- |
| `soul − english + native` | body (0,625) | body (0,829) |
| `law − english + native` | jungle (0,559) | jungle (0,788) |
| `city − english + native` | dreadful (0,618) | dreadful (0,805) |
| `mind − english + native` | nothing (0,633) | never (0,908) |

### Efficacité du hard debiasing
La méthode dite de *hard debiasing* consiste à repérer « l’axe du biais colonial » (la ligne invisible qui sépare le vocabulaire dominant du vocabulaire dominé) dans l’espace vectoriel. Une fois cette ligne identifiée, l’algorithme « aplatit » tous les mots du dictionnaire pour effacer leurs différences sur cet axe, neutralisant ainsi le stéréotype.

```python
def calculer_direction_biais(modele, paires_biais: list) -> np.ndarray:
    # [...]
    matrice = np.array(differences)  # forme (n_paires, d)
    _, _, Vt = np.linalg.svd(matrice, full_matrices=False)
    direction = Vt[0]  # première ligne = première composante principale
    return direction / np.linalg.norm(direction)  # normalisation unitaire
```

```python
def neutraliser_vecteurs(modele, paires_biais: list):
    # [...]
    direction = calculer_direction_biais(modele, paires_biais)
    # [...]
    for mot, idx in modele.dictionary.items():
        if mot not in mots_definitionnels:
            v = nouveaux_vecteurs[idx]
            # Soustraction de la projection sur la direction du biais
            nouveaux_vecteurs[idx] = v - np.dot(v, direction) * direction
    # [...]
```

Cette méthode produit des résultats en demi-teinte. Si les scores cosinus diminuent légèrement pour la majorité des analogies (`soul − english + native` passe ainsi de 0,625 à **0,592**, `law − english + native` de 0,559 à **0,544**), l’analogie `city − english + native` voit quant à elle son score augmenter (de 0,618 à **0,640**). Surtout, les analogies problématiques ne sont pas gommées de l’espace vectoriel : **les mots retournés en tête de classement restent largement inchangés**. La correction s’avère superficielle puisque des termes comme *body*, *jungle* ou *dreadful* demeurent les premières associations pour ces concepts déshumanisants.

Ces limites empiriques corroborent les conclusions de Gonen et Goldberg (2019) dans leur célèbre article "Lipstick on a Pig". Les auteurs y démontrent que le Hard Debiasing n’offre en réalité qu’une correction de façade.
- Tout d’abord, l’axe calculé par l’ACP se contente de capturer la direction de plus grande variance entre nos paires de biais (*english*/*native*, *white*/*brown*, etc.) Or, le biais colonial est un phénomène multidimensionnel qu’une simple ligne droite ne peut résumer intégralement.
- Ensuite, le choix de nos paires de biais est restreint. Si le stéréotype s’exprime à travers des associations lexicales qui ne passent pas par ces sept paires spécifiques (par exemple *jungle*, *darkness* ou *dreadful*), la correction mathématique ne les atteint pas.

Par conséquent, bien que la méthode masque l’asymétrie en surface, la géométrie globale de l’espace vectoriel demeure intacte. Ainsi, Gonen et Goldberg ont pu, en utilisant un simple classificateur d’apprentissage automatique sur des vecteurs « neutralisés », prédire le biais d’origine des mots avec une précision extrêmement élevée (entre 88,88 % et 96,53 %), montrant ainsi qu’il est possible de retrouver le biais, même enfoui après application d’une méthode de *hard debiasing*.

#### Exemples
| Analogie | Standard (score) | Débiaisé (score) |
| :--- | :--- | :--- |
| `soul − english + native` | body (0,625) | body (0,592) |
| `law − english + native` | jungle (0,559) | jungle (0,544) |
| `city − english + native` | dreadful (0,618) | dreadful (0,640) |


## Conclusion
En définitive, les limites empiriques du *hard debiasing* et de l’augmentation contrefactuelle (CDA) invitent à une réflexion méthodologique plus large. Le biais colonial, tel qu’il apparaît dans les œuvres de Kipling et Conrad, ne relève pas d’un simple déséquilibre lexical que l’on pourrait lisser par l’algèbre mais d’une structure sémantique profonde, inscrite dans la manière même dont les mots cooccurrent pour décrire le monde. Les méthodes de correction testées ici s’attaquent à des symptômes superficiels, comme les fréquences d’occurrence ou la géométrie locale de l’espace vectoriel, sans pour autant déconstruire les réseaux de sens qui organisent le corpus.

C’est en effet une vérité fondamentale du traitement du langage : le modèle n’est que le miroir des données qu’il ingère. Le biais colonial n’est pas une anomalie mathématique que l’on pourrait résoudre par une simple équation mais reflète une vision du monde (ici, coloniale). Si l’on souhaite construire des modèles sémantiques véritablement équitables, le défi n’est pas purement algorithmique, il est avant tout culturel. Ce ne sont pas nos calculs qu’il faut corriger, mais les données en entrée : c’est notre vision du monde et les textes que nous choisissons pour entraîner nos machines qu’il convient de déconstruire.


## Bibliographie
> BHABHA, H. (1994). *Les lieux de la culture*

> FANON, F. (1961). *Les Damnés de la terre*

> GONEN, H. et Y. Goldberg (2019). “Lipstick on a Pig: Debiasing Methods Cover up Systematic Gender Biases in Word Embeddings But do not Remove Them”

> SAID, E. (1978). *L’Orientalisme : L’Orient créé par l’Occident*.
