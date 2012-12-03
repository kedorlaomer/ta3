# encode:utf-8

import sys


class StringComparator():
    DEF_GRAM_LEN = 3

    @staticmethod
    def tokenize(s, gram_len):
        tokens = set()
        for i in xrange(len(s) - (gram_len - 1)):
            tokens.add(s[i:i + gram_len])
        return tokens

    @staticmethod
    def dice_grams(t1, t2):
        return 2 * len(t1 & t2) / float(len(t1) + len(t2))

    @staticmethod
    def compare(s1, s2, gram_len=0):
        gram_len = gram_len or StringComparator.DEF_GRAM_LEN
        if gram_len > min(len(s1), len(s2)):
            return 0.0

        return StringComparator.dice_grams(
            StringComparator.tokenize(s1, gram_len),
            StringComparator.tokenize(s2, gram_len),
        )

if __name__ == '__main__':
    if len(sys.argv) == 4:
        s1, s2, gram_len = sys.argv[1:]
    print StringComparator.compare(s1, s2, int(gram_len))
