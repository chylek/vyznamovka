"""Guessable vocabulary = top-N lemmas that have a fastText cc.cs.300 vector,
minus inflected forms simplemma missed (stem+case ending whose base form is
more frequent and close in vector space; they go to the forms map instead).
Writes data/words.txt, data/ft.npy (float16, L2-normalised, same order),
and adds the dropped forms to data/forms.json."""
import sys, json, numpy as np
N = int(sys.argv[1]) if len(sys.argv) > 1 else 40000
lemmas = [l.split("\t")[0] for l in open("data/vocab.tsv")]
want = set(lemmas)
ft = {}
for line in open("data/cc.cs.300.head.vec"):
    w, _, rest = line.partition(" ")
    if w in want and w not in ft:
        v = np.array(rest.split(), dtype=np.float32)
        ft[w] = v / np.linalg.norm(v)
ok = json.load(open("data/lemma_ok.json"))  # from clean.py
cand = [w for w in lemmas if w in ft and ok.get(w, 0) >= 0.45][: int(N * 1.25)]
rank = {w: i for i, w in enumerate(cand)}
END = sorted("a e i o u y á é í ý ě ů ou ám ách ami ům em ím ích ými ého ému ém ým ova ovi ové ových ovým ovou ení ením eními eních".split(), key=len, reverse=True)
BASE = ["", "a", "o", "e", "í", "ý", "é", "á", "ě", "ost", "ení"]
forms = json.load(open("data/forms.json"))
words = []
for i, x in enumerate(cand):
    base = None
    if not x.endswith("ý"):  # masculine adjective is the lemma
        for en in END:
            if x.endswith(en) and len(x) - len(en) >= 3:
                st = x[: -len(en)]
                for b in BASE:
                    h = st + b
                    if h != x and rank.get(h, i) < i and ft[h] @ ft[x] > 0.55:
                        if h.endswith("ý") and x[-1] in "ěeyí":  # adverb from adjective, or -í noun (zdraví), keep
                            continue
                        base = h
                        break
                break
    if base:
        forms[x] = base
    else:
        words.append(x)
words = words[:N]
keep = set(words)
forms = {f: (l if l in keep else forms.get(l, l)) for f, l in forms.items()}
forms = {f: l for f, l in forms.items() if l in keep and f not in keep}
np.save("data/ft.npy", np.stack([ft[w] for w in words]).astype(np.float16))
open("data/words.txt", "w").write("\n".join(words) + "\n")
json.dump(forms, open("data/forms.json", "w"), ensure_ascii=False, separators=(",", ":"))
print(len(words), "words,", len(forms), "forms; last:", words[-8:])
