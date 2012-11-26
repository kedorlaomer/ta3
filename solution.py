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
        s = sum([self._difference[x] for x in substrings(token)])
        return s

################################################################
########################### Programm ###########################
################################################################

from nltk.probability import FreqDist
from collections import defaultdict

# lies english_stop_words.txt ein
stopwords = {}

for token in open("english_stop_words.txt"):
    stopwords[token.strip().lower()] = 1

# lies human-genenames.txt ein
given_genes = {}

for token in open("human-genenames.txt"):
    given_genes[token.strip().lower()] = 1

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
        if left not in stopwords:
            right = right.strip() != "O"
            goldstandard_words.append((extremely_normalize(left), right))

# diese FreqDists enthalten die von Gene bzw. nicht-Gene
# typischen Substrings
gene_substrings = FreqDist()
notgene_substrings = FreqDist()

for (token, is_gene) in goldstandard_words:
    dist = gene_substrings if is_gene else notgene_substrings
    dist.update(substrings(token)

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

klassi = DifferenceClassifier(difference)

# vergleiche klassi gegen goldstandard_words
for (token, is_gene) in goldstandard_words:
    result = klassi.classify_token(token)
    if is_gene != result:
        print token
