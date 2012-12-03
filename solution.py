#!/usr/bin/env python
# encoding: utf-8
# vim: encoding=utf-8

import sys
from collections import defaultdict

from nltk.probability import FreqDist
# from pylab import array, dtype, zeros_like

from helpers import extremely_normalize, substrings
from classifiers import (
    DifferenceClassifier, DictionaryClassifier, AndClassifier, OrClassifier,
    RegExpClassifier, NeighborClassifier, NormFormClassifier, NGramClassifier,
    NaiveClassifier, BadStructureClassifier,
)
from StringComparator import StringComparator


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


def save_results(classifier, tokens, output_file):
    with open(output_file, "w") as f:
        i = 0
        for token in tokens:
            predict = classifier.classify_token(token)
            f.write("%s\t%s\n" % (token, "B-protein" if predict else "O"))
            i += 1
            if i % 10000 == 0:
                print i, len(tokens)


def solution(input_file, output_file, stopwords_file, genes_file):
    stopwords = get_unique_tokens(stopwords_file)
    given_genes = get_unique_tokens(genes_file)
    tokens = []

    with open(input_file) as f:
        for line in f.xreadlines():
            content = line.split("\t")

            if len(content) != 2:
                continue

            left, right = content
            # if right.strip() != "O":
            #     print right.strip()
            tokens.append(left)
    print "Read"

    classifier = AndClassifier([
        BadStructureClassifier(),
        OrClassifier([
            NormFormClassifier(given_genes, stopwords, 1),
            NaiveClassifier(stopwords),
        ])
    ])
    save_results(classifier, tokens, output_file)
    return


if __name__ == '__main__':
    if len(sys.argv) == 5:
        solution(*sys.argv[1:])
    else:
        print """
            Give this files:
            1. input.iob
            2. output.predict
            3. stop.txt
            4. genes.txt
        """
