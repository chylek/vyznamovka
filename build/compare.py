"""Print top neighbours of probe words for each embedding in data/emb-*.npy (+ fastText head)."""
import sys, glob, numpy as np
n = 15000
words = [l.split("\t")[0] for l in open("data/vocab.tsv")][:n]
idx = {w: i for i, w in enumerate(words)}
probes = sys.argv[1].split(",")
embs = {}
for p in sorted(glob.glob("data/emb-*.npy")):
    e = np.load(p).astype(np.float32)
    if len(e) >= n: embs[p[9:-4]] = e[:n]
# fastText: map vocab lemmas to their vector
ft = {}
for line in open("data/cc.cs.300.head.vec"):
    w, _, rest = line.partition(" ")
    if w in idx and w not in ft:
        ft[w] = np.array(rest.split(), dtype=np.float32)
e = np.zeros((n, 300), np.float32)
for w, v in ft.items(): e[idx[w]] = v / np.linalg.norm(v)
embs["fasttext"] = e
for w in probes:
    print(f"\n=== {w}")
    for name, e in embs.items():
        s = e @ e[idx[w]]
        top = np.argsort(-s)[1:16]
        print(f"{name:28s}", ", ".join(words[i] for i in top))
