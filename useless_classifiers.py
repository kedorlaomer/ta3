#!/usr/bin/env python
# encoding=utf-8

################################################################
########################## Funktionen ##########################
################################################################

# normalisiere sehr brutal: bis auf Buchstaben ist alles gleich;
# Ziffern sind alle gleich; Groß- und Kleinschreibung wird
# entfernt
 
def extremely_normalize_char(char):
    char = char.lower()
    if char in "abcdefghijklmnopqrstuvwxyz":
        return char
    elif char in "0123456789":
        return "0"
    else:
        return "@"

# wie extremely_normalize_char, nur dass alle Zeichen eines
# Wortes derartig behandelt werden
 
def extremely_normalize(token):
    return ''.join(map(extremely_normalize_char, token))

# Findet alle Substrings eines Wortes. Dabei wird „x“ auf „^x$“
# abgebildet, um Wortanfang und -ende zu berücksichtigen

def substrings(token):
    token = "^" + token + "$"
    rv = []
    for i in xrange(0, len(token)):
        for j in xrange(i+1, len(token)+1):
            rv.append(token[i:j])

    return rv

def sort_by_value(dictionary):
    return sorted(dictionary, lambda x, y: cmp(dictionary[x], dictionary[y]))

# gegeben goldstandard_words (Liste von von Paaren (token,
# isGene)), wird ein eine „Verteilung“ prob berechnet, welche
# dem Konstruktor von SomehowClassifier übergeben werden kann
def data_to_prob(goldstandard_words, stopwords, genes):

# Hashtabelle, welche Substrings (wie in der Funktion
# substrings()) auf Paare (x, y) abbildet. x ist die Anzahl der
# Vorkommen des Substrings in Gennamen, y die Anzahl in
# nicht-Gennamen.
    evaluation = defaultdict(lambda: (0, 0))

#   for (name, isGene) in goldstandard_words:
#       for subs in substrings(name):
#           (x, y) = evaluation[subs]

#           if isGene:
#               x += 50
#           else:
#               y += 50

#           evaluation[subs] = (x, y)

    for token in stopwords:
        for w in substrings(token):
            t = evaluation[w]
            t = (t[0], t[1]+1)
            evaluation[w] = t

    for token in genes:
        for w in substrings(token):
            t = evaluation[w]
            t = (t[0]+100, t[1])
            evaluation[w] = t

    EPSILON = 0.0001
# bildet jeden Substring auf die Wahrscheinlichkeit ab, in einem
# Gennamen vorzukommen bzw. nicht in einem Gennamen
# vorzukommen); EPSILON wird genommen, falls keine
# Wahrscheinlichkeit bestimmt werden kann
    yesProbability = defaultdict(lambda: EPSILON)
    noProbability = defaultdict(lambda: EPSILON)

# über wieviele Substrings (nicht notwendigerweise verschieden)
# läuft die Statistik?
    total = float(sum([x+y for (x, y) in evaluation.values()]))

# prob bildet Substrings auf irgendwas ab, was mit deren
# Vorkommen in Gennamen zu tun hat
    prob = defaultdict(lambda: EPSILON)

    for substring in evaluation.keys():
        (yes, no) = evaluation[substring]
        yesProbability[substring] = yes
        noProbability[substring] = no
        yes = float(max(EPSILON, yes))
        no = float(max(EPSILON, no))
        prob[substring] = (yes/(yes+no))

    return prob

################################################################
######################## Klassifizierer ########################
################################################################

# unsinniger Classifier
class DifferenceClassifier:
    _difference = None

    def __init__(self, difference):
        self._difference = difference

# summiert die per difference bestimmten Signifikanzen für alle
# Substrings von token
    def classify_token(self, token):
        return sum([self._difference[x] for x in substrings(token)])

# akzeptiert alle Tokens im dictionary
class DictionaryClassifier:
    _dictionary = None
    _stopwords = None

    def __init__(self, dictionary, stopwords):
        self._dictionary = dictionary
        self._stopwords = stopwords

    def classify_token(self, token):
        if token in self._dictionary:
            if token in self._stopwords:
                return 0.1
            else:
                return 1
        else:
            if token in self._stopwords:
                return 0
            else:
                return 0.01

# berechnet die Summe verschiedener Classifier
class OrClassifier:
    _classifiers = None

    def __init__(self, classifiers):
        self._classifiers = classifiers

    def classify_token(self, token):
        return sum([classifier.classify_token(token) for classifier in self._classifiers])

# berechnet die Summe der Gewichte aller Substrings, die in prob
# vorkommen
class SomehowClassifier:
    _prob = None

    def __init__(self, prob):
        self._prob = prob

    def classify_token(self, token):
        # Faktor 2.18 durch Experimente gefunden
        l = max(len(token)-2, 1)**2*2.18
        return sum([self._prob[w] for w in substrings(token)])/l

################################################################
########################### Programm ###########################
################################################################

from nltk.probability import FreqDist
from collections import defaultdict
from pylab import *

# lies english_stop_words.txt ein
stopwords = set()

for token in open("english_stop_words.txt"):
    stopwords.add(extremely_normalize(token.strip().lower()))

# lies human-genenames.txt ein
given_genes = set()

for token in open("human-genenames.txt"):
    given_genes.add(extremely_normalize(token.strip()))

# lies goldstandard.iob ein

# Format von goldstandard_words: Liste von Paaren (token,
# isGene), wobei token ein String (ein Token) und isGene ein
# Boole'scher Wert ist, welcher angibt, ob token laut
# goldstandard.iob ein Gen ist.

goldstandard_words = []
for line in open("goldstandard.iob"):
    content = line.split("\t")
    if len(content) == 2:
        left, right = content
        if rand() < 0.5: # nur 50% betrachten
            right = right.strip() != "O"
            goldstandard_words.append((extremely_normalize(left), right))

# konstruiere daraus Klassifizierer
klassi = SomehowClassifier(data_to_prob(goldstandard_words, stopwords, given_genes))

# erzeuge goldstandard.predict
with open("goldstandard.iob") as inp:
    with open("goldstandard.predict", "w") as out:
        for line in inp.xreadlines():
            content = line.strip().split("\t")
            if len(content) == 2:
                (token, _) = content
                token = extremely_normalize(token)
                result = klassi.classify_token(token) > 0.5
                result = "B-protein" if result else "O"
                out.write("%s\t%s\n" % (token, result))
