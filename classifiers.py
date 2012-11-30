# encoding: utf-8
# vim: encoding=utf-8

from helpers import substrings
import re

class BaseClassifier:
    def classify_token(self, token):
        raise NotImplementedError


class DifferenceClassifier(BaseClassifier):
    _difference = None

    def __init__(self, difference):
        if not hasattr(difference, '__getitem__'):
            raise ValueError(
                "Init object must to implement '__getitem__' method.")
        self._difference = difference

    # summiert die per difference bestimmten Signifikanzen für alle
    # Substrings von token
    def classify_token(self, token):
        return sum((
            self._difference[x] for x in substrings(token)
        ))


# akzeptiert alle Tokens im dictionary
class DictionaryClassifier(BaseClassifier):
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


class OrClassifier(BaseClassifier):
    _classifiers = None

    def __init__(self, classifiers):
        if not all(map(
            lambda x: isinstance(x, BaseClassifier), classifiers
        )):
            raise TypeError("Only '%s' type are allowed." % BaseClassifier)

        self._classifiers = classifiers

    def classify_token(self, token):
        return sum([
            classifier.classify_token(token) for classifier in self._classifiers
        ])


class RegExpClassifier(BaseClassifier):
    
    #def __init__(self)

    def classify_token(self,token):
        p1 = re.compile('([?\w]+|[?\W])[A-Z]')
        p2 = re.compile('([\w]+([\W]+[\w]*)+)|([\w]*([\W]+[\w]+)+)')
        p3 = re.compile('([\D]+([\d]+[\D]*)+)|([\D]*([\d]+[\D]+)+)')
        tokenScore = 0
        if (p1.match(token)!=None):
            tokenScore +=1
        if (p2.match(token)!=None):
            tokenScore +=1
        if (p3.match(token)!=None):
            tokenScore +=1
        return tokenScore


class NeighborClassifier(BaseClassifier):
    _relevantNeighbors = None

    def __init__(self,relevantNeighbors):
        self._relevantNeighbors = relevantNeighbors


    def classify_token(self,tokenNeighborhood):
        tokenScore = 0
        for neighbor in tokenNeighborhood:
            if neighbor in self._relevantNeighbors:
                tokenScore += 1
        return tokenScore

# class TopologyClassifier(BaseClassifier):
#     _neighborhoodTopology = None

#     def __init__(self,neighborhoodTopology)
#         self._neighborhoodTopology = neighborhoodTopology


#     def classify_token(self,tokenNeighborhood):
#         tokenScore = 0
#         for neighbor in tokenNeighborhood:
#             if neighbor in self._relevantNeighbors:
#                 tokenScore += 1
#         return tokenScore

