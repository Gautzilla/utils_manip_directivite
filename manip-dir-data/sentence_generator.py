from enum import Enum
import random

Direction = Enum('Direction', ["Up","Down","Left","Right"])

objects = ["un lit", "une armoire", "une commode", "un miroir", "une table", "une étagère", "un bureau", "un évier"]
objects = {
    Direction.Left: objects,
    Direction.Right: objects,
    Direction.Up: ["un luminaire", "un ventilateur", "des poutres", "des néons", "des moulures"],
    Direction.Down: ["du parquet", "un tapis", "du carrelage", "de la moquette", "du lino"]
}

names = {
    Direction.Left: "à gauche",
    Direction.Right: "à droite",
    Direction.Down: "au sol",
    Direction.Up: "au plafond",
}

smallAngleSentenceParts = ["oui, j'ai déjà vu", "non, je n'ai jamais vu"]
movies = ["Les Affranchis", "Fargo", "Le Parrain", "Duel", "Les Infiltrés", "L'Impasse", "Le Prestige", "Un Prophète", "Porco Rosso", "Incendies", "Juno", "Magnolia", "Le Péril Jeune", "La Vie Aquatique"]

def two_distinct_items(liste):
    item1 = random.choice(liste)
    item2 = random.choice(list(filter(lambda x: x!=item1, liste)))
    return (item1, item2)

def gen_sentence_small():
    (part1, part2) = two_distinct_items(smallAngleSentenceParts)
    (movie1, movie2) = two_distinct_items(movies)
    return f"{part1.capitalize()} {movie1}, mais {part2} {movie2}."

def gen_sentence_large():
    sentence = "Dans cette pièce, il y a :"
    (object1, object2) = two_distinct_items(objects[Direction.Right])
    parts = []
    for direction in Direction:
        object = ""
        match direction:
            case Direction.Left:
                object = object1
            case Direction.Right:
                object = object2
            case _:
                object = random.choice(objects[direction])
        parts.append(f"{names[direction]} : {object}")
    random.shuffle(parts)
    sentence += ' ' + ' ; '.join(parts[0:-1]) + ' et ' + parts[-1] + '.'
    return sentence

if (__name__ == '__main__'):  
    while(True):
        print("a: mouvement faible \nb: mouvement large \n_: retour")
        c = input()
        if (c=="a"):
            print(gen_sentence_small())
        elif(c == "b"):
            print(gen_sentence_large())
        else:
            break