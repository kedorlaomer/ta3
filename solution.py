#!/usr/bin/env python
# encoding: utf-8
# vim: encoding=utf-8


from collections import defaultdict
from nltk.probability import FreqDist

from helpers import extremely_normalize, substrings
from difference_classifier import DifferenceClassifier


def get_unique_tokens(filename):
    with open(filename) as f:
        return set([
            line.lower().strip() for line in f.xreadlines()
        ])


def solution():
    stopwords = get_unique_tokens("english_stop_words.txt")
    given_genes = get_unique_tokens("human-genenames.txt")

    # lies goldstandard.iob ein

    # Format von goldstandard_words: Liste von Paaren (token,
    # is_gene), wobei token ein String (ein Token) und is_gene ein
    # Boole'scher Wert ist, welcher angibt, ob token laut
    # goldstandard.iob ein Gen ist.

    goldstandard_words = []
    with open("goldstandard.iob") as f:
        for line in f.xreadlines():

            content = line.split("\t")
            if len(content) != 2:
                continue

            left, right = content
            if left in stopwords:
                continue

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

    for substr in (gene_substrings + notgene_substrings).iterkeys():
        v1 = gene_substrings.get(substr) or 0
        v2 = notgene_substrings.get(substr) or 0

        difference[substr] = v1 / size1 - v2 / size2

    classifier = DifferenceClassifier(difference)

    # vergleiche classifier gegen goldstandard_words
    for (token, is_gene) in goldstandard_words:
        result = classifier.classify_token(token)
        if is_gene != result:
            print token


if __name__ == '__main__':
    solution()
