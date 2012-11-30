#!/usr/bin/env python
# encoding: utf-8
# vim: encoding=utf-8

from collections import defaultdict

from nltk.probability import FreqDist
from pylab import array, dtype, zeros_like

from helpers import extremely_normalize, substrings
from classifiers import (
    DifferenceClassifier, DictionaryClassifier, OrClassifier, RegExpClassifier, NeighborClassifier
)


def get_unique_tokens(filename):
    with open(filename) as f:
        return set([
            line.lower().strip() for line in f.xreadlines()
        ])


def mini_evaluation(goldstandard_words, classifier, epsilon=0.01):
    true_positives = 0
    false_negatives = 0
    total = len(goldstandard_words)

    for (token, is_gene) in goldstandard_words:
        classification = classifier.classify_token(token) > epsilon
        if classification and is_gene:
            true_positives += 1
        if not classification and not is_gene:
            false_negatives += 1

    precision = true_positives / float(total)
    recall = true_positives / float(true_positives + false_negatives)
    f_measure = 2 * precision * recall / (precision + recall)
    return precision, recall, f_measure


def solution():
    stopwords = get_unique_tokens("english_stop_words.txt")
    given_genes = get_unique_tokens("human-genenames.txt")

    # lies goldstandard.iob ein

    # Format von goldstandard_words: Liste von Paaren (token,
    # is_gene), wobei token ein String (ein Token) und is_gene ein
    # Boole'scher Wert ist, welcher angibt, ob token laut
    # goldstandard.iob ein Gen ist.

    goldstandard_words = []
    regexClassi = RegExpClassifier()
    with open("goldstandard.iob") as f:
        for line in f.xreadlines():

            content = line.split("\t")
            if len(content) != 2:
                continue

            left, right = content
            # if False:  # left in stopwords:
            #     continue

            right = right.strip() != "O"
            if regexClassi.classify_token(left) > 0:
                print left + '\t' +str(right)
            elif str(right) == "B-protein":
                print '\t \t forgot this: '+left
                #guardar en una lista las que cumplen el patron pero no son B-prot
            goldstandard_words.append((extremely_normalize(left), right))
    print '#################### end of RegExpClassifier ################'
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

    r = xrange(-10, 10 + 1)
    A = array([array(r), zeros_like(r)])
    A.dtype = dtype('float32')

    # for (i, e) in enumerate(xrange(-10, 10 + 1)):
    #     if e != 0:
    #         epsilon = 0.2 / e
    #         print "epsilon = ", epsilon
    #         klassi = OrClassifier([
    #             DictionaryClassifier(given_genes, stopwords),
    #             DifferenceClassifier(difference),
    #         ])

    #         precision, recall, f_measure = mini_evaluation(
    #             goldstandard_words, klassi, epsilon
    #         )
    #         A[0, i] = epsilon
    #         A[1, i] = f_measure


if __name__ == '__main__':
    solution()
