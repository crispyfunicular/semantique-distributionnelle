from nltk.corpus import wordnet as wn
from random import sample, seed

"""
get;put;1.98
forget;know;0.92
multiply;divide;1.75
modest;flexible;0.98
container;mouse;0.3
inform;notify;9.25
vanish;disappear;9.8
quick;rapid;9.7
cow;cattle;9.52
student;pupil;9.35
"""

class WordPair:
    def __init__(self, word1, word2, pos, simlex):
        self.word1 = word1
        self.word2 = word2
        self.pos = pos
        self.simlex = simlex

        # Listes d'objets Synset
        synsets1 = wn.synsets(word1, pos=pos.lower())
        synsets2 = wn.synsets(word2, pos=pos.lower())
        
        # Pour la pertinence de nos calculs, on retient pour chaque paire de mots les sens qui rendent ces mots les plus proches possible.
        # On cherche donc la paire qui maximise le path_similarity et qui servira de référence pour tous les scores
        self.path_score = 0
        best_pair = None
        for synset1 in synsets1:
            for synset2 in synsets2:
                if not synset1.pos() == synset2.pos():
                    continue
                path_score = synset1.path_similarity(synset2)
                if path_score > self.path_score:
                    best_pair = (synset1, synset2)
                    self.path_score = path_score
        
        if not best_pair:
            raise Exception(f"Aucune paire de sens de même POS n'a été trouvée pour la paire {word1}-{word2}.")

        self.lch_score = best_pair[0].lch_similarity(best_pair[1])
        self.wup_score = best_pair[0].wup_similarity(best_pair[1])
    
    def __str__(self):
        return f"""La paire {self.word1}-{self.word2} a :
        - une simlex de {self.simlex},
        - une similarité de {self.path_score},
        - un coefficient de similarité de Leacock et Chodorow de {self.lch_score}, et
        - un coefficient de similarité Wu-Palmer de {self.wup_score}.
        """


def get_random_words(input_file) -> list[WordPair]:
    # Liste "greater than 9"
    gt_9 = []

    # Liste "less than 2"
    lt_2 = []
    
    i = 0
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            i += 1
            line_lst = line.split(";")
            
            # On saute la première ligne correspondant au titre des colonnes
            if i == 1:
                continue

            if len(line_lst) < 3:
                raise Exception(f"Liste trop courte : {len(line_lst)} {line}")
            word1 = line_lst[0]
            word2 = line_lst[1]
            pos = line_lst[2]
            simlex = float(line_lst[3])

            # Evite les paires dont le POS n'est pas le même (ex : new.a.01 et ancient.s.01)
            # car le score LCH nécessite que les deux mots aient le même POS
            try:
                pair = WordPair(word1, word2, pos, simlex)
            except Exception as e:
                print(e)
                continue

            if pair.simlex > 9:
                gt_9.append(pair)
            if pair.simlex < 2:
                lt_2.append(pair)
    
    if len(gt_9) < 5 or len(lt_2) < 5:
        raise Exception("Nombre insuffisant de paires de mots pertinents.")
    
    return sample(lt_2, 5) + sample(gt_9, 5)



def main():
    # On "fige" la fonctionne random pour pouvoir toujours travailler avec les mêmes mots
    seed(0)
    input_file = "input_file.csv"
    output_file = "table.csv"
    words = get_random_words(input_file)

    with open(output_file, "w", encoding="utf-8") as f:
        # Le programme renvoie deux tableaux : l'un dans un fichier .csv (avec f.write (sep=";")), l'autre directement dans le terminal (avec print (sep="\t"))
        f.write("mot 1;mot 2;simlex;path;LCH;WUP\n")
        print("mot 1", "mot 2", "SimLex", "path", "LCH", "WUP", sep="\t")
        for pair in words:
            f.write(f"{pair.word1}; {pair.word2}; {pair.simlex}; {pair.path_score:.2f}; {pair.lch_score:.2f}; {pair.wup_score:.2f}\n")
            print(pair.word1, pair.word2, pair.simlex, f"{pair.path_score:.2f}", f"{pair.lch_score:.2f}", f"{pair.wup_score:.2f}", sep="\t")


if __name__ == "__main__":
    main()