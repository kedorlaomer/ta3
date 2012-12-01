# encoding: utf-8
# vim: encoding=utf-8

from collections import OrderedDict

from helpers import substrings, extremely_normalize


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


class GoldBasedClassifier(BaseClassifier):
    stopwords = []
    goldgens = []

    normform_goldgens = []
    baseform_goldgens = {}

    normform_search = False
    baseform_search = False

    def __init__(
        self, goldgens, stopwords=None,
        normform_search=False, baseform_search=False
    ):
        self.stopwords = stopwords
        self.goldgens = goldgens
        self.set_normform_search(normform_search)
        self.set_baseform_search(baseform_search)

    def set_normform_search(self, value):
        self.normform_search = value
        if value:
            self.normform_goldgens = map(extremely_normalize, self.goldgens)
        else:
            self.normform_goldgens = []

    def set_baseform_search(self, value):
        self.baseform_search = value
        if value:
            self.baseform_goldgens = OrderedDict()
            for goldgen in sorted(
                self.goldgens,
                lambda x, y: cmp(len(x), len(y)),
                reverse=1
            ):
                self.baseform_goldgens[goldgen] = substrings(goldgen)
        else:
            self.baseform_goldgens = {}

    def is_stopword(self, token):
        return token in self.stopwords

    def is_goldgen(self, token):
        return token in self.goldgens

    def has_equal_normform(self, token):
        return extremely_normalize(token) in self.normform_goldgens

    def get_baseform_coeff(self, token, min_coeff=0):
        token_baseforms = substrings(token)

        coeff = 0
        curr_coeff = 0
        f1 = ""
        w1 = ""
        for word, forms in self.baseform_goldgens.iteritems():
            if len(word) < min_coeff * len(token):
                break
            if len(word) < len(f1):
                break

            for form in forms:
                if form in token_baseforms:
                    curr_coeff = (len(form) ** 2) / float(len(token) * len(word))
                    coeff = max(curr_coeff, coeff)
                    f1 = form
                    w1 = word
        return coeff

    def classify_token(self, token):
        if self.is_stopword(token):
            return 0
        if self.is_goldgen(token):
            return 1

        coeff = 0
        if self.normform_search and self.has_equal_normform(token):
            coeff = 0.5
        if self.baseform_search:
            coeff = max([
                coeff,
                self.get_baseform_coeff(token, min_coeff=coeff)
            ])
        return coeff
