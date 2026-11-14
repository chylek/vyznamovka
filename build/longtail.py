"""Long tail: make every Czech word fastText knows guessable, not just the ~32k core.
Streams the full cc.cs.300 (data/cc.cs.300.vec.gz), lemmatises each lowercase Czech token
(simplemma; core forms.json wins), adds hunspell lemmas from subword.py,, and writes lazily-loaded shards docs/w/<first 3 letters>.json:
  {"m": {form: lemma}, "v": {lemma: base64 int8[128]}}
"m" holds every form whose lemma differs from itself (core or not); "v" holds a PCA-128
int8 vector for each non-core lemma (fastText row < MAX_ROW). Also writes data/pca.npz
(mean + basis fitted on the core vectors), which days.py uses for the per-day cosines,
so core and long-tail words are compared in the same space."""
import base64, gzip, json, os, re, shutil, collections, numpy as np, simplemma

MAX_ROW, DIM = 1_000_000, 128
ok = re.compile(r"^[a-záčďéěíňóřšťúůýž]{2,}$")
core = open("data/words.txt").read().split()
core_set = set(core)
forms = json.load(open("data/forms.json"))

ft = np.load("data/ft.npy").astype(np.float32)
mu = ft.mean(0)
P = np.linalg.svd(ft - mu, full_matrices=False)[2][:DIM]
np.savez("data/pca.npz", mu=mu, P=P)

vec, row = {}, {}
with gzip.open("data/cc.cs.300.vec.gz", "rt", encoding="utf8", errors="ignore") as f:
    next(f)
    for n, line in enumerate(f):
        w = line[: line.find(" ")]
        if not ok.match(w) or w in row:
            continue
        row[w] = n
        if n < MAX_ROW and w not in core_set:
            vec[w] = np.array(line.split(" ")[1:301], dtype=np.float32)
print(len(row), "czech tokens,", len(vec), "with vectors")
# dictionary words Common Crawl lacks (or has only past MAX_ROW): subword vectors from subword.py
hv = np.load("data/hunspell.npy").astype(np.float32)
for w, v in zip(open("data/hunspell.txt").read().split(), hv):
    if w not in core_set and w not in vec and np.linalg.norm(v) > 0:
        vec[w] = v
        row.setdefault(w, MAX_ROW)
print(len(vec), "with hunspell lemmas")


def lemma(w):
    if w in core_set:
        return w
    if w in forms:
        return forms[w]
    l = simplemma.lemmatize(w, lang="cs").lower()
    return l if l in core_set or l in vec else w


shards = collections.defaultdict(lambda: {"m": {}, "v": {}})
need = set()
for w in row:
    l = lemma(w)
    if l != w and (l in core_set or l in vec):
        shards[w[:3]]["m"][w] = l
    if l not in core_set and l in vec:
        need.add(l)
for f_, l in forms.items():  # core forms not in fastText (wordfreq-only) too
    shards[f_[:3]]["m"].setdefault(f_, l)
for l in need:
    z = (vec[l] / np.linalg.norm(vec[l]) - mu) @ P.T
    q = np.clip(np.round(z / np.abs(z).max() * 127), -127, 127).astype(np.int8)
    shards[l[:3]]["v"][l] = base64.b64encode(q.tobytes()).decode()
shutil.rmtree("docs/w", ignore_errors=True); os.makedirs("docs/w")
for k, s in shards.items():
    json.dump(s, open(f"docs/w/{k}.json", "w"), ensure_ascii=False, separators=(",", ":"))
print(len(shards), "shards,", len(need), "long-tail lemmas,", sum(len(s["m"]) for s in shards.values()), "forms")
