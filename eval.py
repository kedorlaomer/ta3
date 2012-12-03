# encode:utf-8
import sys


def get_tokens_value(filename):
    with open(filename) as f:
        rt = []
        for line in f.xreadlines():
            line_args = line.strip().split("\t")
            line_args = [x for x in line_args if x.strip()]

            if len(line_args) != 2:
                continue
            token, value = [x.strip() for x in line_args]
            rt.append((token, value))
        return rt


def get_unique_tokens(tokens):
    return dict([
        (x[0], x[1]) for x in tokens
    ])


def main(fileA, fileB):
    tokensA = get_tokens_value(fileA)
    tokensB = get_tokens_value(fileB)
    unique_tokensA = get_unique_tokens(tokensA)
    unique_tokensB = get_unique_tokens(tokensB)

    true_positives = 0
    true_negatives = 0
    false_positives = 0
    false_negatives = 0
    not_in_a = 0
    not_in_b = 0

    false_positives_list = []
    for token, value in tokensB:
        if token in unique_tokensA:
            if value == "O":
                if value == unique_tokensA[token]:
                    true_negatives += 1
                else:
                    false_negatives += 1
            else:
                if value == unique_tokensA[token]:
                    true_positives += 1
                else:
                    false_positives += 1
                    false_positives_list.append(token)
        else:
            not_in_a += 1
    for token, value in tokensA:
        if token not in unique_tokensB:
            not_in_b += 1
    with open('./data/false_positives.txt', 'w') as f:
        f.writelines(sorted(["%s, " % x for x in false_positives_list]))

    print not_in_a, not_in_b
    print true_positives, true_negatives, false_positives, false_negatives
    if true_positives:
        precision = true_positives / float(true_positives + false_positives)
        recall = true_positives / float(true_positives + false_negatives)
        f_measure = 2 * precision * recall / (precision + recall)
        print precision, recall, f_measure

if __name__ == '__main__':
    if len(sys.argv) == 3:
        main(*sys.argv[1:])
