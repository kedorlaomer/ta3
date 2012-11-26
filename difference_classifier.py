# encoding: utf-8
# vim: encoding=utf-8

from helpers import substrings


class DifferenceClassifier:
    _difference = None

    def __init__(self, difference):
        if not hasattr(difference, '__getitem__'):
            raise ValueError(
                "Init object must to implement '__getitem__' method.")
        self._difference = difference

    # summiert die per difference bestimmten Signifikanzen für alle
    # Substrings von token
    def classify_token(self, token):
        classified = sum(
            (self._difference[x] for x in substrings(token))
        )
        return classified
