Download the [SYN V9](https://wiki.korpus.cz/doku.php/cnk:syn:verze9) dataset from https://korpus.cz and use the prepare.py script to convert the dataset format to 1 sentence per line for word2vec.
The sentences are created from lemmatized forms, some tokens are omitted. See the code.

```
python prepare.py syn_v9 syn_v9_lines.txt

```

Grab word2vec source code from https://github.com/dav/word2vec, compile it and train it on the data:

```
word2vec -train syn_v9_lines.txt -output cs_syn_vectors.bin -cbow 1 -size 500 -window 10 -negative 10 -hs 0 -sample 1e-5 -threads 10 -binary 1 -iter 3 -min-count 50
```

You can use the cs_syn_vectors.bin with the other word2vec binaries or load it in gensim.