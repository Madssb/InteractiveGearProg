import random


def araxxor_uniques_no_pet():
    n_nally_pieces = 0
    n_fangs = 0
    kc = 0
    while (
        n_nally_pieces < 3 or n_fangs < 1
    ):  # keeps going until there are three or more nally pieces, and n_fangs > 0.
        kc += 1
        if random.random() < 1 / 150:
            if random.random() < 1 / 4:
                n_fangs += 1
            else:
                n_nally_pieces += 1
    return kc


N = 100000
cum_kcs = 0
for i in range(N):
    cum_kcs += araxxor_uniques_no_pet()


print(print(cum_kcs / N))
# 853.86084
