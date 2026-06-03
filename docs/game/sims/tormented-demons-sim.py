import random


def tormented_demons_completion():
    n_burning_claws = 0
    n_tormented_synapses = 0
    kc = 0
    while (
        n_burning_claws < 2 or n_tormented_synapses < 2
    ):  # keeps going until there are three or more nally pieces, and n_tormented_synapses > 0.
        kc += 1
        if random.random() < 1 / 500:
            n_tormented_synapses += 1
        elif random.random() < 1 / 500:
            n_burning_claws += 1
    return kc


N = 100000
cum_kcs = 0
for i in range(N):
    cum_kcs += tormented_demons_completion()

print(cum_kcs / N)
# 1374.76 kc
