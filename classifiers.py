# encoding: utf-8
# vim: encoding=utf-8

from helpers import substrings


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
