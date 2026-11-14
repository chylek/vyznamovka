"""Second clean-up pass over data/words.txt (run after vectors.py, before days.py):
1. diacritics twins: a word whose de-accented spelling matches a more frequent word
   and that Jev calls a misspelling of it (plus fastText agreement) -> forms map;
2. inflected / conjugated / ne- forms Jev flags (vyzní, nezazní, krásnější) -> forms map,
   pointing at the closest remaining word sharing their stem (dropped if none).
Rewrites data/words.txt, data/ft.npy, data/forms.json. Jev answers cached in data/dedupe.json."""
import json, os, sys, unicodedata, numpy as np
sys.path.insert(0, "build"); from jev import noul

words = open("data/words.txt").read().split()
e = np.load("data/ft.npy").astype(np.float32)
ix = {w: i for i, w in enumerate(words)}
forms = json.load(open("data/forms.json"))
cache = json.load(open("data/dedupe.json")) if os.path.exists("data/dedupe.json") else {}


def ask(keys, texts):
    todo = [(k, t) for k, t in zip(keys, texts) if k not in cache]
    if todo:
        cache.update(zip([k for k, _ in todo], noul({"language": "Czech"}, [t for _, t in todo])))
        json.dump(cache, open("data/dedupe.json", "w"), ensure_ascii=False)
    return [cache[k] for k in keys]


freq = {l.split("\t")[0]: float(l.split("\t")[1]) for l in open("data/vocab.tsv")}
# real words with an accented twin that the rules above would merge
# ponytail: hand-checked list from the 2026-11-14 build; re-check if the vocab changes
REAL = set("byt tykat zprava směsný dosazený dosazení vypravení zamyslet pocestný svatost splacení nesplacení "
           "panský rvát utracení horkost směrovat narůst odklizení plakat".split())
marks = lambda s: len(unicodedata.normalize("NFD", s)) - len(de(s))
cos = lambda a, b: float(e[ix[a]] @ e[ix[b]])
de = lambda s: "".join(c for c in unicodedata.normalize("NFD", s) if not unicodedata.combining(c))
drop = {}

# 1. diacritics twins (words are frequency-ordered, so the first spelling wins)
first, pairs = {}, []
for w in words:
    first.setdefault(de(w), w)
    if first[de(w)] != w:
        pairs.append((w, first[de(w)]))
p = ask([f"typo:{a}:{b}" for a, b in pairs],
        [f"Is „{a}“ just a misspelling of „{b}“ (diacritics missing or wrong), rather than a separate, "
         "correctly spelled Czech word?" for a, b in pairs])
for (a, b), x in zip(pairs, p):
    if (((x + cos(a, b) > 1.15 and marks(a) < marks(b))  # typo twins sit close in vector space; plakat/plakát don't
             or (freq[b] > 40 * freq[a]  # rare mis-accented spelling of a common word: vedet, muz, běhěm ...
                 and (marks(a) < marks(b) or cos(a, b) > 0.47)))  # ... but not hřát/hrát, vědění/vedení
            and a not in REAL  # missing accents (byť/být, vymýšlet/vymyslet are real words)
            and not (a.endswith("ky") and b.endswith("ký") and freq[b] < 200 * freq[a])):  # hezky/hezký adverb; velky (1500x rarer) typo
        drop[a] = b
print(len(drop), "typo twins, e.g.", list(drop.items())[:12])

# 2. inflected / ne- forms
rest = [w for w in words if w not in drop]
p = ask([f"infl:{w}" for w in rest],
        [f"Is „{w}“ an inflected or conjugated form (e.g. 3rd person, past tense, case, plural, comparative) "
         "or a ne- negation of some other Czech verb or adjective, rather than a dictionary headword "
         "(infinitive, nominative singular noun, masculine adjective, adverb)?" for w in rest])
infl = {w for w, x in zip(rest, p) if x > 0.8 and not w.endswith(("ý", "ost"))}  # nezávislý, nezaměstnanost are headwords
heads = [w for w in rest if w not in infl]
by_prefix = {}
for w in heads:
    by_prefix.setdefault(w[:3], []).append(w)
n_mapped = 0
for w in infl:
    stem = w[2:] if w.startswith("ne") and len(w) > 5 else w
    k = max(3, len(stem) - 3)
    cands = [h for h in by_prefix.get(stem[:3], []) if h[:k] == stem[:k]]
    if not cands and stem != w:  # nezazní -> zaznít: retry without the ne- stem trim
        cands = [h for h in by_prefix.get(w[:3], []) if h[:max(3, len(w) - 3)] == w[:max(3, len(w) - 3)]]
    best = max(cands, key=lambda h: cos(w, h), default=None)
    drop[w] = best if best and cos(w, best) > 0.4 else None
    n_mapped += drop[w] is not None
print(len(infl), "inflected,", n_mapped, "mapped, e.g.", [(w, drop[w]) for w in list(infl)[:15]])

keep = [w for w in words if w not in drop]
forms.update({w: b for w, b in drop.items() if b})
kept = set(keep)
forms = {f: (l if l in kept else drop.get(l) or forms.get(l)) for f, l in forms.items()}
forms = {f: l for f, l in forms.items() if l in kept and f not in kept}
np.save("data/ft.npy", e[[ix[w] for w in keep]].astype(np.float16))
open("data/words.txt", "w").write("\n".join(keep) + "\n")
json.dump(forms, open("data/forms.json", "w"), ensure_ascii=False, separators=(",", ":"))
print(len(keep), "words,", len(forms), "forms")
