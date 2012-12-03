# encoding: utf-8
# vim: encoding=utf-8


# normalisiere sehr brutal: bis auf Buchstaben ist alles gleich;
# Ziffern sind alle gleich; Groß- und Kleinschreibung wird
# entfernt
def extremely_normalize_char(char, digit_char="0", else_char="@"):
    char = char.lower()

    if char.isalpha():
        return char

    if char.isdigit():
        return digit_char

    return else_char


# wie extremely_normalize_char, nur dass alle Zeichen eines
# Wortes derartig behandelt werden
def extremely_normalize(token):
    return ''.join(map(extremely_normalize_char, token))


# Findet alle Substrings eines Wortes. Dabei wird „x“ auf „^x$“
# abgebildet, um Wortanfang und -ende zu berücksichtigen
def substrings(token):
    return list(xsubstrings(token))


def xsubstrings(token):
    token = "^" + token + "$"
    for i in xrange(0, len(token)):
        for j in xrange(i + 1, len(token) + 1):
            yield token[i:j]


def substringsByLength(token, length):
    substrings = []
    if len(token) >= length:
        for i in xrange(0, len(token) - length + 1):
            substrings.append(token[i: i + length])
    return substrings


def sort_by_value(dictionary, sgn=None):
    sgn = sgn if callable(sgn) else cmp
    return sorted(dictionary, lambda x, y: sgn(dictionary[x], dictionary[y]))


def sort_dict_by_value(dictionary):
    return sorted(dictionary, key=dictionary.get)


def keysWithHighestValues(dictionary, ranking):
    listOfKeys = sort_dict_by_value(dictionary)
    return listOfKeys[-1:-(ranking + 1):-1]
