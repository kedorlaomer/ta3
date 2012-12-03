# encoding: utf-8
# vim: encoding=utf-8

from helpers import substrings, substringsByLength
import re
import nltk

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
                return 0.5
            else:
                return 10
        else:
            if token in self._stopwords:
                return -10
            else:
                return 0.5

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
    
    def classify_token(self,token):
        p1 = re.compile('([\w]+|[\W]+)[A-Z]') # großbuchstabe nicht am anfang
        p2 = re.compile('([\w]*[a-zA-Z]+[\w]*[\W]+)|(([\w]*[\W]+[\w]*)+[a-zA-Z]+)') # Zeichen im Wort
        p3 = re.compile('([\D]*[a-zA-Z]+[\D]*[\d]+)|(([\D]*[\d]+[\D]*)+[a-zA-Z]+)') # Zahl im Wort
        tokenScore = 0
        if (p1.match(token)!=None):
            tokenScore = 3
        if (p2.match(token)!=None):
            tokenScore = 3
        if (p3.match(token)!=None):
            tokenScore = 3
        return tokenScore


class RegExpGenClassifier(BaseClassifier):
    _notGenes = None

    def __init__(self, notGenes):
        self._notGenes = notGenes

    def classify_token(self,token):
        if token in self._notGenes:
            print "tokenclassifier: "+token+" out because in bad dictionary"
            return 0;

        #TODO: doesn't match '3rd' but should
        p1 = re.compile('([\w+]|[\W*])+[A-Z]')
        p2 = re.compile('([\w]+([\W]+[\w]*)+)|([\w]*([\W]+[\w]+)+)')
        p3 = re.compile('([\D]+([\d]+[\D]*)+)|([\D]*([\d]+[\D]+)+)')
        tokenScore = 0
        if (p1.match(token)!=None):
            tokenScore = 3
        if (p2.match(token)!=None):
            tokenScore = 3
        if (p3.match(token)!=None):
            tokenScore = 3
        return tokenScore

#TODO: neighbors are not correctly implemented
class NeighborClassifier(BaseClassifier):
    _relevantNeighbors = None

    def __init__(self,relevantNeighbors):
        self._relevantNeighbors = relevantNeighbors

    def classify_token(self,token,tokenNeighborhood):
        tokenScore = 0
        for neighbor in tokenNeighborhood:
            if (neighbor != token) and (neighbor in self._relevantNeighbors):
                tokenScore += 1
        return tokenScore

#TODO: class that matches the token with a given dictionary of suffixes

class substringClassifier(BaseClassifier):
    _commonSubstrings = set()

    def __init__(self,commonSubstrings):
        self._commonSubstrings = commonSubstrings

    def classify_token(self, token):
        tokenScore = 0
        if token > 3:
            substrings = substringsByLength(token,3)
            for sbstr in substrings:
                if sbstr not in self._commonSubstrings:
                    tokenScore = 3
        return tokenScore



