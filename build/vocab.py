"""Czech lemma vocabulary from wordfreq forms, lemmatized with simplemma.
Writes data/vocab.tsv (lemma, zipf-ish freq) and data/forms.json (form -> lemma)."""
import json, re, sys
from collections import defaultdict
from wordfreq import top_n_list, word_frequency
import simplemma

N = int(sys.argv[1]) if len(sys.argv) > 1 else 200000
ok = re.compile(r"^[a-záčďéěíňóřšťúůýž]{2,}$")
freq = defaultdict(float)
forms = {}
for f in top_n_list("cs", N):
    if not ok.match(f):
        continue
    lem = simplemma.lemmatize(f, lang="cs").lower()
    if not ok.match(lem):
        continue
    freq[lem] += word_frequency(f, "cs")
    if f != lem:
        forms[f] = lem
vocab = sorted(freq, key=freq.get, reverse=True)
# a lemma must also exist as an attested form, otherwise simplemma likely invented it
attested = set(top_n_list("cs", N))
vocab = [w for w in vocab if w in attested]
keep = set(vocab)
forms = {f: l for f, l in forms.items() if l in keep and f not in keep}
import os; os.makedirs("data", exist_ok=True)
with open("data/vocab.tsv", "w") as fh:
    for w in vocab:
        fh.write(f"{w}\t{freq[w]:.3e}\n")
json.dump(forms, open("data/forms.json", "w"), ensure_ascii=False, separators=(",", ":"))
print(len(vocab), "lemmas,", len(forms), "forms")
