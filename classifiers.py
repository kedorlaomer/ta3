# encoding: utf-8
# vim: encoding=utf-8

import re
from collections import OrderedDict, Counter

from helpers import StringComparator, substrings, extremely_normalize


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


class MetaClassifier(BaseClassifier):
    _classifiers = None

    def __init__(self, classifiers):
        if not all(map(
            lambda x: isinstance(x, BaseClassifier), classifiers
        )):
            raise TypeError("Only '%s' type are allowed." % BaseClassifier)

        self._classifiers = classifiers


class OrClassifier(MetaClassifier):
    def classify_token(self, token):
        return sum([
            classifier.classify_token(token) for classifier in self._classifiers
        ])


class AndClassifier(MetaClassifier):
    def classify_token(self, token):
        res = 1
        for classifier in self._classifiers:
            res *= classifier.classify_token(token)
            if res == 0:
                return 0
        return res


class BadStructureClassifier(BaseClassifier):
    def classify_token(self, token):
        return not (
            len(token) in [1, 3]
            and token in [token.upper(), token.lower()]
        )


class NaiveClassifier(BaseClassifier):
    stopwords = []

    def __init__(self, stopwords=[]):
        self.stopwords = stopwords

    def is_stopword(self, token):
        return token in self.stopwords

    def _contains_digit(self, token):
        return bool(re.search(r"\d", token))

    def _contains_upper(self, token, min_count=1):
        match = re.findall(r"[A-Z]", token)
        if match:
            return len(match) >= min_count
        return False

    def classify_token(self, token):
        return int(
            not self.is_stopword(token)
            and not token.isdigit()
            and len(token) > 2
            and token.isalnum()
            and self._contains_digit(token)
            and self._contains_upper(token, min_count=1)
        )


class NormFormClassifier(BaseClassifier):
    gens = []
    stopwords = []
    normform_gens = []
    min_normform_count = 1
    _results = {}
    _normform_counter = None
    _gene_similarity = {}

    def __init__(self, gens, stopwords=None, min_normform_count=1):
        self.gens = gens or []
        self.stopwords = stopwords or []
        self.min_normform_count = min_normform_count

        self._init_normform_gens()

    def _init_normform_gens(self):
        self.normform_gens = map(extremely_normalize, list(set(self.gens)))
        self._normform_counter = Counter(self.normform_gens)
        # self._normform_counter = Counter(map(extremely_normalize, self.gens))
        self.normform_gens = list(set(self.normform_gens))

    def has_equal_normform(self, token):
        return extremely_normalize(token) in self._normform_counter

    def has_equal_normform_with_min_frequency(self, norm_token):
        return (
            norm_token in self._normform_counter
            and self._normform_counter[norm_token] >= self.min_normform_count
        )

    def get_best_gene_similarity(self, normalized_token, min_v):
        if normalized_token not in self._gene_similarity:
            max_v = 0
            for norm_gen in self.normform_gens:
                max_v = max(max_v, StringComparator.compare(normalized_token, norm_gen))
                if max_v >= min_v:
                    break
            self._gene_similarity[normalized_token] = max_v
        return self._gene_similarity[normalized_token]

    def classify_token(self, token):
        coeff = 0
        normalized_token = extremely_normalize(token)

        if normalized_token in self._results:
            coeff = self._results[normalized_token]
        elif normalized_token in self.stopwords:
            coeff = 0
        elif normalized_token in self.normform_gens:
            coeff = 1
        elif self.has_equal_normform_with_min_frequency(normalized_token):
            coeff = 0.5
        # elif self.get_best_gene_similarity(token, 0.5) >= 0.5:
        #     coeff = self.get_best_gene_similarity(normalized_token, 0.5)
        self._results[normalized_token] = coeff
        return coeff


class NGramClassifier(BaseClassifier):
    stopwords = []
    gens = []
    baseform_gens = {}

    def __init__(self, gens, stopwords=None):
        raise NotImplementedError
        self.gens = gens
        self.stopwords = stopwords

    def set_baseform_search(self, value):
        self.baseform_search = value
        if value:
            self.baseform_gens = OrderedDict()
            for goldgen in sorted(
                self.gens,
                lambda x, y: cmp(len(x), len(y)),
                reverse=1
            ):
                self.baseform_gens[goldgen] = substrings(goldgen, False)
        else:
            self.baseform_gens = {}

    def get_baseform_coeff(self, token, min_coeff=0):
        token_baseforms = substrings(token, False)

        coeff = 0
        curr_coeff = 0
        last_found_form = ""
        # w1 = ""
        for word, forms in self.baseform_gens.iteritems():
            if len(word) < min_coeff * len(token):
                break
            if len(word) < len(last_found_form):
                break

            for form in forms:
                if form in token_baseforms:
                    curr_coeff = (len(form) ** 2) / float(len(token) * len(word))
                    coeff = max(curr_coeff, coeff)
                    # last_found_form = form
                    # w1 = word
        # return coeff

        coeff = max([
            coeff,
            self.get_baseform_coeff(token, min_coeff=coeff)
        ])
        return coeff

    def classify_token(self, token):
        raise NotImplementedError
        if self.is_stopword(token):
            return 0
        if self.is_goldgen(token):
            return 1
        return self.get_baseform_coeff(token)


class RegExpClassifier(BaseClassifier):
    
    #def __init__(self)

    def classify_token(self, token):
        p1 = re.compile('([?\w]+|[?\W])[A-Z]')
        p2 = re.compile('([\w]+([\W]+[\w]*)+)|([\w]*([\W]+[\w]+)+)')
        p3 = re.compile('([\D]+([\d]+[\D]*)+)|([\D]*([\d]+[\D]+)+)')
        tokenScore = 0
        if (p1.match(token) != None):
            tokenScore += 1
        if (p2.match(token) != None):
            tokenScore += 1
        if (p3.match(token) != None):
            tokenScore += 1
        return tokenScore


class NeighborClassifier(BaseClassifier):
    _relevantNeighbors = None

    def __init__(self, relevantNeighbors):
        self._relevantNeighbors = relevantNeighbors

    def classify_token(self, tokenNeighborhood):
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
