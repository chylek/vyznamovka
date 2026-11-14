"""Jev pass over the guessable vocab: is each word standard Czech in its dictionary form?
Caches probabilities in data/lemma_ok.json (used by vectors.py to drop English words,
typos, colloquial and inflected forms)."""
import json, os, sys
sys.path.insert(0, "build"); from jev import noul
words = [l.split("\t")[0] for l in open("data/vocab.tsv")][:int(sys.argv[1]) if len(sys.argv) > 1 else 60000]
path = "data/lemma_ok.json"
ok = json.load(open(path)) if os.path.exists(path) else {}
todo = [w for w in words if w not in ok]
for i in range(0, len(todo), 2048):
    c = todo[i:i + 2048]
    ok.update(zip(c, noul({"language": "Czech"}, [
        f"Is „{w}“ a standard Czech word written in its dictionary (base) form — nominative singular for nouns, "
        "masculine nominative for adjectives, infinitive for verbs — and not an English word, typo, slang spelling "
        "or abbreviation?" for w in c])))
    json.dump(ok, open(path, "w"), ensure_ascii=False)
    print(i + len(c), "/", len(todo), flush=True)
