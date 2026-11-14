"""Vectors for dictionary words Common Crawl never saw: every lowercase lemma of the
LibreOffice hunspell cs_CZ dictionary (data/cs_CZ.dic, GPL), embedded with fastText's
subword model (data/cc.cs.300.bin). Writes data/hunspell.txt + data/hunspell.npy.
Needs the `fasttext` package, which has no wheel for new Pythons:
  uv venv -p 3.11 .venv-ft && uv pip install -p .venv-ft/bin/python fasttext-wheel numpy
  .venv-ft/bin/python build/subword.py"""
import re, numpy as np, fasttext
ok = re.compile(r"^[a-záčďéěíňóřšťúůýž]{2,}$")
words = sorted({l.split("/")[0].strip() for l in open("data/cs_CZ.dic").read().splitlines()[1:]} )
words = [w for w in words if ok.match(w)]
m = fasttext.load_model("data/cc.cs.300.bin")
np.save("data/hunspell.npy", np.stack([m.get_word_vector(w) for w in words]).astype(np.float16))
open("data/hunspell.txt", "w").write("\n".join(words) + "\n")
print(len(words), "dictionary lemmas embedded")
