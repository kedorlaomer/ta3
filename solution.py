#!/usr/bin/env python
# vim: encoding=utf-8

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
#
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

def sgn(x):
    if sgn > 0:
        return 1
    elif sgn < 0:
        return -1
    else:
        return 0

def sort_by_value(dictionary):
    return sorted(dictionary, lambda x, y: sgn(dictionary[x] - dictionary[y]))

def mini_evaluation(klassi, epsilon):
    true_positives = 0
    false_negatives = 0
    total = 0

    for (token, is_gene) in goldstandard_words:
        total += 1
        classification = klassi.classify_token(token) > epsilon
        if classification and is_gene:
            true_positives += 1
        if not classification and not is_gene:
            false_negatives += 1

    precision = true_positives/float(total)
    recall = true_positives/float(true_positives + false_negatives)
    f_measure = 2*precision*recall / (precision+recall)
    return precision, recall, f_measure

################################################################
######################## Klassifizierer ########################
################################################################

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

class OrClassifier:
    _classifiers = None

    def __init__(self, classifiers):
        self._classifiers = classifiers

    def classify_token(self, token):
        return sum([classifier.classify_token(token) for classifier in self._classifiers])


################################################################
########################### Programm ###########################
################################################################

from nltk.probability import FreqDist
from collections import defaultdict
from pylab import *

# lies english_stop_words.txt ein
stopwords = set()

for token in open("english_stop_words.txt"):
    stopwords.add(token.strip().lower())

# lies human-genenames.txt ein
given_genes = set()

for token in open("human-genenames.txt"):
    given_genes.add(token.strip().lower())

# lies goldstandard.iob ein

# Format von goldstandard_words: Liste von Paaren (token,
# is_gene), wobei token ein String (ein Token) und is_gene ein
# Boole'scher Wert ist, welcher angibt, ob token laut
# goldstandard.iob ein Gen ist.

goldstandard_words = []
for line in open("goldstandard.iob"):
    content = line.split("\t")
    if len(content) == 2:
        left, right = content
        if True: #left not in stopwords:
            right = right.strip() != "O"
            goldstandard_words.append((extremely_normalize(left), right))

# diese FreqDists enthalten die von Gene bzw. nicht-Gene
# typischen Substrings
gene_substrings = FreqDist()
notgene_substrings = FreqDist()

for (token, is_gene) in goldstandard_words:
    dist = gene_substrings if is_gene else notgene_substrings
    dist.update(substrings(token))

difference = defaultdict(float)
size1 = float(gene_substrings.N())
size2 = float(notgene_substrings.N())

# difference ist eine Hashtabelle, wobei die Schlüssel von
# Substrings und die Werte Differenzen in ihrer Häufigkeit sind.
# Positiv bedeutet: häufig in Gennamen; negativ bedeutet: selten
# in Gennamen.

for substr in (gene_substrings + notgene_substrings).keys():
    v1 = gene_substrings.get(substr) or 0
    v2 = notgene_substrings.get(substr) or 0

    difference[substr] = v1/size1 - v2/size2

r = xrange(-10, 10+1)
A = array([array(r), zeros_like(r)])
A.dtype = dtype('float64')

for (i, e) in enumerate(xrange(-10, 10+1)):
    if e != 0:
        epsilon = 0.2/e
        print "epsilon = ", epsilon
        klassi = OrClassifier([DictionaryClassifier(given_genes, stopwords),
                              DifferenceClassifier(difference)])
        precision, recall, f_measure = mini_evaluation(klassi, epsilon)
        A[0, i] = epsilon
        A[1, i] = f_measure
