"""Rough part of speech from Czech word endings, used to debias fastText vectors.
fastText neighbours cluster by part of speech (technický -> other adjectives; technika
sits at #3487). Subtracting each POS's mean vector before comparing removes most of that
(technika -> ~#100) without changing noun-noun neighbours much.
ponytail: ending heuristic, not a tagger - nouns in -ě/-í are guessed via the adjective
test below; a real tagger (MorphoDiTa) would be the upgrade if misreads matter."""
import re, numpy as np

ADJ = re.compile(r"(ý|ejší|ší|cí|[^eáí]ní)$")       # nový, lepší, pracující, letní (not zdraví, vedení)
VERB = re.compile(r"(at|át|et|ět|it|ít|ýt|out|ovat|nout|ci)$")
ADV_E = re.compile(r"(ně|ě|e|y)$")


def pos(w, known):
    """known: set of words, used to accept -ě/-e/-y adverbs only when the adjective exists."""
    if ADJ.search(w):
        return 0
    if VERB.search(w):
        return 1
    m = ADV_E.search(w)
    if m and (w[: m.start()] + "ý" in known or w[: m.start() + 1 if w.endswith("ně") else m.start()] + "ý" in known):
        return 2
    return 3  # noun / other


def centroids(words, e):
    known = set(words)
    p = np.array([pos(w, known) for w in words])
    return p, np.stack([e[p == k].mean(0) for k in range(4)])


def debias(v, p, cent):
    """v: (n, d) unit vectors, p: (n,) POS ids -> unit vectors with POS mean removed."""
    d = v - cent[p]
    return d / np.linalg.norm(d, axis=1, keepdims=True)


if __name__ == "__main__":  # self-check on obvious cases
    known = {"hodný", "pravý", "rychlý", "krásný"}
    cases = {"nový": 0, "letní": 0, "lepší": 0, "zdraví": 3, "vedení": 3, "nádraží": 3, "náměstí": 3,
             "zpívat": 1, "moci": 1, "jít": 1, "hodně": 2, "rychle": 2, "krásně": 2, "dítě": 3, "země": 3,
             "pes": 3, "technika": 3, "stát": 1, "hrát": 1, "život": 3, "radost": 3}
    bad = {w: (pos(w, known), want) for w, want in cases.items() if pos(w, known) != want}
    assert not bad, bad
    print("pos.py ok")
