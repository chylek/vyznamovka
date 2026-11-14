# Významovka

Czech [Semantle](https://semantle.com)-style daily word game. Fully static: the
`docs/` folder is the whole site (GitHub Pages ready), no backend.

## How the ranking works

Each guess gets a **rank** (1 = closest to the secret), Contexto-style, instead of
a raw cosine score.

- **Vocabulary** – Czech word forms from [wordfreq](https://github.com/rspeer/wordfreq),
  lemmatised with [simplemma](https://github.com/adbar/simplemma). An LLM pass (Jev)
  drops English words and slang spellings; `build/dedupe.py` then folds accent typos
  (`svuj`, `vedet`, `běhěm` – Jev + fastText + frequency ratio, with a short keep-list
  of real look-alikes like `byt/být`, `hřát/hrát`) and inflected / `ne-` forms Jev
  flags (`vyzní`, `nezazní`) into their headword. ~32k guessable words; ~83k other
  forms map to them, so typing `psa`, `clovek` or `nezazní` still works.
- **Base similarity** – [fastText cc.cs.300](https://fasttext.cc/docs/en/crawl-vectors.html)
  (Common Crawl + Wikipedia, CC BY-SA 3.0) cosine. Ranks every word.
- **Top 1000** – the 1000 nearest fastText words are re-ranked by a blend of
  60 % *“is this closely related in meaning to the secret?”* probability from
  [Jev](https://typesafe.ai) and 40 % fastText rank. That fixes the classic word2vec
  oddities (antonyms and co-occurring words ranked as “similar”).
- **Per-day file** `docs/d/<n>.bin` (~34 kB): `uint16[1001]` secret + top-1000 word
  indices, then `uint8` fastText cosine for every word (ranks 1001+ are sorted in
  the browser). Day 1 = 2026-11-14, 365 days generated.

Transformer embedding models (bge-m3, EmbeddingGemma, Qwen3-Embedding-0.6B) were tried for single words
and rank by spelling, not meaning (`pes` → pe, pec, ps), so they aren't used.

## Build

```sh
python -m venv .venv && .venv/bin/pip install -r requirements.txt
curl -sL https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.cs.300.vec.gz | gunzip -c | head -400001 > data/cc.cs.300.head.vec
.venv/bin/python build/vocab.py          # data/vocab.tsv, data/forms.json
.venv/bin/python build/clean.py 110000   # Jev: which lemmas are clean Czech (cached)
.venv/bin/python build/vectors.py        # data/words.txt, data/ft.npy
.venv/bin/python build/dedupe.py         # fold typos + inflected forms into forms.json (Jev, cached)
# build/pick_secrets.py only once: data/secrets.txt is committed and is the schedule
.venv/bin/python build/days.py           # docs/d/*.bin (Jev answers cached in data/jev/)
cp data/words.txt data/forms.json docs/
```

Jev needs `JEV_API_KEY` in the environment. Changing `data/words.txt` changes word
indices, so regenerate all of `docs/d/` together with it.

**Spoilers:** with no backend the answers are public by design – each day file
contains its secret and `data/secrets.txt` is the whole schedule. Fine for a
friends-and-family game; hiding them would need a server.

Play locally: `python -m http.server -d docs`, `?d=N` opens day N.
