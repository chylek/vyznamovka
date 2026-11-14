"""Per-day puzzle files for the static site.
Ranking = cosine of POS-debiased fastText vectors (pos.py: without it an adjective secret
only finds adjectives) for everything. The pool of the 1000 debiased-nearest plus the 300
raw-nearest words is re-ranked by a blend of Jev's 'closely related in meaning?'
probability and the debiased rank, so the warm end follows human association.

docs/d/<n>.bin  (n = 1-based day number since START):
  uint16[1001]  word indices: secret, then ranks 1..1000
  uint8[V]      cosine of every core word to the secret in the int8 PCA-128 space of
                longtail.py, mapped (-0.2..1) -> 0..255 (ranks 1001+ and long-tail words)
  int8[128]     the secret's PCA vector, so the browser can score long-tail guesses
Jev answers are cached in data/jev/<secret>.json, so re-runs only ask about new words."""
import json, os, sys, numpy as np
sys.path.insert(0, "build"); from jev import noul; from pos import pos, debias

POOL, RAW, TOP, W_JEV = 1000, 300, 1000, 0.6
words = open("data/words.txt").read().split()
ix = {w: i for i, w in enumerate(words)}
e = np.load("data/ft.npy").astype(np.float32)
pca = np.load("data/pca.npz")  # from longtail.py
known = set(words)
ed = debias(e, np.array([pos(w, known) for w in words]), pca["cent"])
z = (ed - pca["mu"]) @ pca["P"].T
zq = np.clip(np.round(z / np.abs(z).max(1, keepdims=True) * 127), -127, 127)  # same int8 as the shards
zn = zq / np.linalg.norm(zq, axis=1, keepdims=True)
secrets = open("data/secrets.txt").read().split()
only = sys.argv[1:]  # optional: just these secrets, print the result
os.makedirs("docs/d", exist_ok=True); os.makedirs("data/jev", exist_ok=True)


def rank(sec):
    s, raw = ed @ ed[ix[sec]], e @ e[ix[sec]]
    s[ix[sec]] = raw[ix[sec]] = -9
    order = np.argsort(-s)
    dr = np.empty(len(words), int); dr[order] = np.arange(len(words))  # debiased rank of every word
    pool = np.array(list(dict.fromkeys([*order[:POOL], *np.argsort(-raw)[:RAW]])))
    cache = f"data/jev/{sec}.json"
    p = json.load(open(cache)) if os.path.exists(cache) else {}
    todo = [words[i] for i in pool if words[i] not in p]  # only words not asked before (vocab changes)
    if todo:
        p.update(zip(todo, noul({"language": "Czech", "secret_word": sec},
                                [f"Is „{w}“ closely related in meaning to the secret word?" for w in todo])))
        json.dump(p, open(cache, "w"), ensure_ascii=False)
    blend = [W_JEV * p[words[i]] + (1 - W_JEV) * max(0, 1 - dr[i] / POOL) for i in pool]
    top = pool[np.argsort(blend, kind="stable")[::-1]][:TOP]
    return s, top


for n, sec in enumerate(secrets, 1):
    if only and sec not in only:
        continue
    s, top = rank(sec)
    if only:
        print(sec, ":", ", ".join(words[i] for i in top[:40]))
        continue
    c = zn @ zn[ix[sec]]
    q = np.clip((c + 0.2) / 1.2 * 255, 0, 255).round().astype(np.uint8)
    with open(f"docs/d/{n}.bin", "wb") as f:
        f.write(np.array([ix[sec], *top], dtype="<u2").tobytes() + q.tobytes() + zq[ix[sec]].astype(np.int8).tobytes())
    print(n, sec, flush=True)
