# TP3 - Correction des biais
**Morgane Bona-Pellissier**, Master 1 pluriTAL  
morgane@bona-pellissier.net  

L’ensemble de ce projet est disponible sur le dépôt suivant : `https://github.com/crispyfunicular/semantique-distributionnelle/tp3`

## Choix du corpus
Après quelques essais infructueux pour mettre en évidence le *male gaze* dans un corpus d’auteurs français (les résultats s’étant révélés peu parlants), nous nous sommes tournée vers deux auteurs anglophones ayant dépeint dans leurs œuvres la vie dans l’Empire britanniques, à savoir **Rudyard Kipling** (1865-1936) et **Joseph Conrad** (1857-1924). Afin de maximiser nos résultats et de ne pas bruiter inutilement le corpus, nous avons délibérément restreint notre sélection aux seules les œuvres de ces auteurs portant sur les colonies. Les romans sélectionnés pour le corpus sont donc les suivants :

**Joseph Conrad** : *Heart of Darkness* (1899), *Victory: An Island Tale* (1915), *Lord Jim* (1900), *The Nigger of the "Narcissus"* (1897), *An Outcast of the Islands* (1896), *Typhoon* (1902).

- Nombre de tokens (corpus brut) : TBD
- Nombre de tokens (corpus lemmatisé) : 462 434

**Rudyard Kipling** : *In Black and White* (1888), *Under the Deodars* (1888), *The Story of the Gadsbys* (1888), *Plain Tales from the Hills* (1888), *The Jungle Book* (1894), *The Second Jungle Book* (1895), *Kim* (1901), *The Man Who Would Be King* (1888), *Life’s Handicap: Being Stories of Mine Own People* (1891), *The Light That Failed* (1891), *From Sea to Sea: Letters of Travel* (1899), *Soldiers Three* (1888).

- Nombre de tokens (corpus brut) : 939 527
- Nombre de tokens (corpus lemmatisé) : TBD

L'ensemble de ces textes ont été récupérés manuellement sur le site du Projet Guthenberg (https://www.gutenberg.org/).

### Hypothèse
Nous espérons que ce corpus de littérature impériale nous permettra de mettre en évidence les stéréotypes coloniaux et racistes de l’époque victorienne. Pour ce faire, nous avons cherché spécifiquement des analogies pouvant capturer ces biais, telles que :
- **`man` - `english` + `native` = ?**
- **`human` - `white` + `black` = ?**
- **`master` - `english` + `native` = ?**
- **`wisdom` - `english` + `native` = ?**
- **`light` - `white` + `black` = ?**

## Structure de la pipeline

Le pipeline est composé d'une succession de trois scripts :
1. `nettoyage.py` : pour préparer le corpus brut en supprimant les métadonnées et licences du Projet Gutenberg, en normalisant la typographie (apostrophes) et en fusionnant les sauts de ligne.
2. `lemmatisation.py` : pour lemmatiser le corpus avec le modèle `en_core_web_lg` de spaCy (anglais - large)
3. `tp3.py` : pour entraîner le modèle GloVe sur le corpus lemmatisé, tester la présence de biais coloniaux à travers de la résolution d'analogies et appliquer deux méthodes de débiaisage. Nous avons utilisé la librairie `Mittens` pour générer nos plongements lexicaux avec GloVe.
La structure de ce pipeline a été créée par nos soins et les scripts en eux-mêmes ont été codés à l'aide de `Claude Opus 4.6 (Thinking)`.

## Discussion des résultats
> Voir `resultats.md`


## Conclusion


## Bibliographie


## Annexe