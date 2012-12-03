#!/usr/bin/env python
# encoding: utf-8
# vim: encoding=utf-8

from collections import defaultdict

from helpers import sort_dict_by_value

from classifiers import (
    DifferenceClassifier, DictionaryClassifier, OrClassifier,
    RegExpClassifier, RegExpGenClassifier, NeighborClassifier,
    substringClassifier
)


def get_unique_tokens(filename):
    with open(filename) as f:
        return set([
            line.lower().strip() for line in f.xreadlines()
        ])


def solution():
    stopwords = get_unique_tokens("english_stop_words.txt")
    given_genes = get_unique_tokens("human-genenames.txt")

    # neighbors: Dictionary mit token, die länger als ein Zeichen sind als key und Anzahl von Erscheiningen als value.
    # Es werden die nicht stopwords gespeichert die in der Nähe von einem Protein vorkommen
    sentence = set()
    sentenceFlag = False
    neighbors = defaultdict(int)

    regexClassi = RegExpClassifier()
    dictClassi = DictionaryClassifier(given_genes, stopwords)

    with open("goldstandard.iob") as f:
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
                left = content[0]
                dictValue = dictClassi.classify_token(left.lower())
                if dictValue > 1:
                    sentenceFlag = True

                if (regexClassi.classify_token(left)):
                    sentence.add(left)
                elif (dictValue > 0) and (len(left) > 1) and (not left.isdigit()):
                    sentence.add(left.lower())
    # we only want the 100 most seen neighbors as a list
    if len(neighbors) > 100:
        neighbors = sort_dict_by_value(neighbors)[-1:-100:-1]
    # for word in neighbors:
    #     print word

    sentenceScores = defaultdict(int)
    sentence.clear()
    sentenceNr = 0
    with open("goldstandard.iob") as f:
        for line in f.xreadlines():
            content = line.split("\t")

            # der Satz ist zu Ende
            if len(content) != 2:
                score = len([x for x in sentence if x in neighbors])
                sentenceScores[sentenceNr] = score
                sentence.clear()

            else:
                left = content[0]
                if (regexClassi.classify_token(left)):
                    sentence.add(left)
                elif (dictValue > 0) and (len(left) > 1) and (not left.isdigit()):
                    sentence.add(left.lower())
            sentenceNr += 1

    sentenceNr = 0
    print len(sentenceScores)
    with open("goldstandard.iob") as f:
        with open("goldstandard.predict", "w") as w:
            for line in f.xreadlines():
                content = line.split("\t")

                if len(content) == 2:
                    left = content[0]

                    dictValue = dictClassi.classify_token(left.lower())

                    if dictValue > 1 or (
                        regexClassi.classify_token(left)
                        and sentenceScores[sentenceNr] > 5
                    ):
                        w.write("%s\tB-protein\n" % content[0])
                    else:
                        w.write("%s\t%s" % content)
                else:
                    w.write("\n")

                sentenceNr += 1


if __name__ == '__main__':
    solution()
