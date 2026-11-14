"""Per-day puzzle files for the static site.
Ranking = fastText cosine for everything, but the 1000 nearest words get re-ranked
by a blend of Jev's 'closely related in meaning?' probability and their fastText rank,
so the warm end of the list follows human association, not just co-occurrence.

docs/d/<n>.bin  (n = 1-based day number since START):
  uint16[1001]  word indices: secret, then ranks 1..1000
  uint8[V]      fastText cosine of every word to the secret, mapped (-0.2..1) -> 0..255
Jev answers are cached in data/jev/<secret>.json, so re-runs only ask about new words."""
import json, os, sys, numpy as np
sys.path.insert(0, "build"); from jev import noul

POOL, TOP, W_JEV = 1000, 1000, 0.6
words = open("data/words.txt").read().split()
ix = {w: i for i, w in enumerate(words)}
e = np.load("data/ft.npy").astype(np.float32)
secrets = open("data/secrets.txt").read().split()
only = sys.argv[1:]  # optional: just these secrets, print the result
os.makedirs("docs/d", exist_ok=True); os.makedirs("data/jev", exist_ok=True)


def rank(sec):
    s = e @ e[ix[sec]]
    s[ix[sec]] = -9
    pool = np.argsort(-s)[:POOL]
    cache = f"data/jev/{sec}.json"
    p = json.load(open(cache)) if os.path.exists(cache) else {}
    todo = [words[i] for i in pool if words[i] not in p]  # only words not asked before (vocab changes)
    if todo:
        p.update(zip(todo, noul({"language": "Czech", "secret_word": sec},
                                [f"Is „{w}“ closely related in meaning to the secret word?" for w in todo])))
        json.dump(p, open(cache, "w"), ensure_ascii=False)
    blend = [W_JEV * p[words[i]] + (1 - W_JEV) * (1 - r / POOL) for r, i in enumerate(pool)]
    top = pool[np.argsort(blend, kind="stable")[::-1]][:TOP]
    return s, top


for n, sec in enumerate(secrets, 1):
    if only and sec not in only:
        continue
    s, top = rank(sec)
    if only:
        print(sec, ":", ", ".join(words[i] for i in top[:40]))
        continue
    s[ix[sec]] = 1
    q = np.clip((s + 0.2) / 1.2 * 255, 0, 255).round().astype(np.uint8)
    with open(f"docs/d/{n}.bin", "wb") as f:
        f.write(np.array([ix[sec], *top], dtype="<u2").tobytes() + q.tobytes())
    print(n, sec, flush=True)
