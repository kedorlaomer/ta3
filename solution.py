#!/usr/bin/env python
# encoding: utf-8
# vim: encoding=utf-8

import sys
from collections import defaultdict

from nltk.probability import FreqDist
# from pylab import array, dtype, zeros_like

from helpers import extremely_normalize, substrings
from classifiers import (
    DifferenceClassifier, DictionaryClassifier, OrClassifier, RegExpClassifier,
    NeighborClassifier, NormFormClassifier, WordRatioClassifier, NaiveClassifier,
)


def get_unique_tokens(filename):
    with open(filename) as f:
        return set([
            line.lower().strip() for line in f.xreadlines()
        ])


def mini_evaluation(goldstandard_words, classifier, epsilon=0.01):
    true_positives = false_positives = false_negatives = 0
    precision = recall = f_measure = 0

    for (token, is_gene) in goldstandard_words:
        classification = classifier.classify_token(token) >= epsilon
        if classification:
            if is_gene:
                true_positives += 1
            else:
                false_positives += 1
        elif is_gene:
            false_negatives += 1

    if true_positives:
        precision = true_positives / float(true_positives + false_positives)
        recall = true_positives / float(true_positives + false_negatives)
        f_measure = 2 * precision * recall / (precision + recall)

    print true_positives, false_positives, false_negatives
    return precision, recall, f_measure


def solution(input_file, output_file, stopwords_file, genes_file):
    stopwords = get_unique_tokens(stopwords_file)
    given_genes = get_unique_tokens(genes_file)

    # lies goldstandard.iob ein

    # Format von goldstandard_words: Liste von Paaren (token,
    # is_gene), wobei token ein String (ein Token) und is_gene ein
    # Boole'scher Wert ist, welcher angibt, ob token laut
    # goldstandard.iob ein Gen ist.

    goldstandard_words = []
    goldgens = []
    regexClassi = RegExpClassifier()

    with open("goldstandard.iob") as f:
        for line in f.xreadlines():

            content = line.split("\t")
            if len(content) != 2:
                continue

            left, right = content
            right = right.strip() != "O"
            # if regexClassi.classify_token(left) > 0:
            #     print "%s\t%s" % (left, right)
            # elif str(right) == "B-protein":
            #     print '\t \t forgot this: %s' % left
                #guardar en una lista las que cumplen el patron pero no son B-prot
            # goldstandard_words.append((extremely_normalize(left), right))
            goldstandard_words.append((left, right))
            if right:
                goldgens.append(left)

    # classifier = NormFormClassifier(goldgens, stopwords)
    # with open("my.predict", "w") as f:
    #     for token, is_gene in goldstandard_words:
    #         predict = classifier.classify_token(token)
    #         f.write("%s\t%s\n" % (token, "B-protein" if predict else "O"))

    # classifier = NaiveClassifier(stopwords=stopwords)
    # print mini_evaluation(goldstandard_words, classifier, 1.0)
    classifier = NormFormClassifier(goldgens=goldgens, stopwords=stopwords)
    print mini_evaluation(goldstandard_words, classifier, 0.5)
    return

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

    # r = xrange(1, 11)
    # A = array([array(r), zeros_like(r)])
    # A.dtype = dtype('float32')

    # for (i, e) in enumerate(xrange(1, 11)):
    #    epsilon = 0.1 * e
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
    if len(sys.argv) == 5:
        solution(sys.argv)
    else:
        print """
            Give this files:
            1. input.iob
            2. output.iob
            3. stop.txt
            4. genes.txt
        """
