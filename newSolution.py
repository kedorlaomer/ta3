#!/usr/bin/env python
# encoding: utf-8
# vim: encoding=utf-8

import sys
from collections import defaultdict

from helpers import sort_dict_by_value

from classifiers import (
    DifferenceClassifier, DictionaryClassifier, OrClassifier,
    RegExpClassifier, RegExpGenClassifier, NeighborClassifier,
    SubstringClassifier, BadStructureClassifier,
)


def get_unique_tokens(filename):
    with open(filename) as f:
        return set([
            line.lower().strip() for line in f.xreadlines()
        ])


def solution(input_file, output_file, stopwords_file, genes_file):
    stopwords = get_unique_tokens(stopwords_file)
    given_genes = get_unique_tokens(genes_file)

    # neighbors: Dictionary mit token, die länger als ein Zeichen sind als key und Anzahl von Erscheiningen als value.
    # Es werden die nicht stopwords gespeichert die in der Nähe von einem Protein vorkommen
    sentence = set()
    sentenceFlag = False
    neighbors = defaultdict(int)

    regexClassi = RegExpClassifier()
    badStructureClassi = BadStructureClassifier()
    dictClassi = DictionaryClassifier(given_genes, stopwords)

    with open(input_file) as f:
        for line in f.xreadlines():
            content = line.split("\t")

            # der Satz ist zu Ende
            if len(content) != 2:
                if sentenceFlag:
                    for word in sentence:
                        neighbors[word] += 1
                sentence.clear()
                sentenceFlag = False
            else:
                token = content[0]
                dictValue = dictClassi.classify_token(token.lower())
                if dictValue > 1:
                    sentenceFlag = True

                if regexClassi.classify_token(token):
                    sentence.add(token)
                elif dictValue > 0 and len(token) > 1 and not token.isdigit():
                    sentence.add(token.lower())

    # we only want the 100 most seen neighbors as a list
    if len(neighbors) > 100:
        neighbors = sort_dict_by_value(neighbors, reverse=True)[:100]

    sentenceScores = defaultdict(int)
    sentence.clear()
    sentenceNr = 0
    with open(input_file) as f:
        for line in f.xreadlines():
            content = line.split("\t")

            # der Satz ist zu Ende
            if len(content) != 2:
                score = len([x for x in sentence if x in neighbors])
                sentenceScores[sentenceNr] = score
                sentence.clear()
            else:
                token = content[0]
                if regexClassi.classify_token(token):
                    sentence.add(token)
                elif dictValue > 0 and len(token) > 1 and not token.isdigit():
                    sentence.add(token.lower())
            sentenceNr += 1

    sentenceNr = 0
    # print len(sentenceScores)
    with open(input_file) as f:
        with open(output_file, "w") as w:
            for line in f.xreadlines():
                content = line.split("\t")

                if len(content) == 2:
                    token = content[0]

                    dictValue = dictClassi.classify_token(token.lower())

                    if badStructureClassi.classify_token(token) and (
                        dictValue > 1
                        or (
                            regexClassi.classify_token(token)
                            and sentenceScores[sentenceNr] > 5
                        )
                    ):
                        w.write("%s\tB-protein\n" % token)
                    else:
                        w.write("%s\tO\n" % token)
                else:
                    w.write("\n")

                sentenceNr += 1


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
