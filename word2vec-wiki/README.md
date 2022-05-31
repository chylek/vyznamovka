# word2vec-on-wikipedia
A pipeline for training word embeddings using word2vec on wikipedia corpus. Originally by [Di Jin](https://github.com/jind11/word2vec-on-wikipedia).
Modifications that allow you to change the language and have better dependencies done by Adam Chýlek.

## How to use
Download the original word2vec. You can find it [here](https://github.com/dav/word2vec). Compile it and copy the binaries to the word2vec folder.
Just run `sudo sh run.sh`, which will:

* Download the latest English wikipedia dump. If you want to change the language, change the LANG variable in the script.
* Extract and clean texts from the downloaded wikipedia dump
* Pre-process the wikipedia corpus
* Train word2vec model on the processed corpus to produce word embedding results

Details for each step will be discussed as below:

### Wikipedia dump

All the latest English wikipedia can be downloaded from a [Wikipedia database dump](https://dumps.wikimedia.org/enwiki/latest). Here I downloaded all the article pages:

```
curl -L -O "https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.bz2"
```

### Wikipedia dump extraction

The original wikipedia dump that can be downloaded is in xml format and the structure is quite complex. Thus we need to use a extractor tool to parse it. The one I used is from the [wikiextractor](https://github.com/attardi/wikiextractor) repository. Only the file *WikiExtractor.py* is needed and the descriptions of parameters can be found the in the repository readme file. The output would be each article id and its name followed by the content in text format.

```
python WikiExtractor.py enwiki-latest-pages-articles.xml.bz2 -b 1G -o extracted --no-template --processes 24
```

### Text pre-processing

Before the word2vec training, the corpus needs to be pre-processed, which bascially includes: sentence spltting, sentence tokenization, removing sentences that contain less than 20 characters or 5 tokens, and converting all numerals to 0. For example, "1993" would be converted into "0000". 

```
python wiki-corpus-prepare.py extracted/wiki processed/wiki
```

### Word2vec training

Once we get the processed wikipedia corpus ready, we can start the word2vec training. Here I used the [Google word2vec tool](https://code.google.com/archive/p/word2vec/), which is pretty standard and efficient. You can find it [here](https://github.com/dav/word2vec).

```
./word2vec -train ../processed/wiki -output ../results/enwiki.skip.size300.win10.neg15.sample1e-5.min10.bin -cbow 0 -size 300 -window 10 -negative 15 -hs 0 -sample 1e-5 -threads 24 -binary 1 -min-count 10
```

## Evaluation of word embeddings

After we well-train the word embeddings, we always want to evaluate the performance for quality check. Here I used the word relation test set described in [**Efficient Estimation of Word Representations in Vector Space**](https://arxiv.org/pdf/1301.3781.pdf) for performance test. 

```
./compute-accuracy ../results/enwiki.skip.size300.win10.neg15.sample1e-5.min15.bin < questions-words.txt
```

In my experiments, the vocabulary of word embeddings I obtained is 833,976 and the token number of the corpus is 2,333,367,969. I generated several word embedding files for different vector sizes: 50, 100, 200, 300 and 400. For each file, I provide the downloadable link and its word relation test performance in the following table:

| vector size  | Word relation test performance (%)    |
| :-----------:|:-------------------------------------:|
| [50](https://drive.google.com/open?id=1OeJNyl1SUoH8XUhKsJYKkSixeEVwCe-h)   | 47.33 |
| [100](https://drive.google.com/open?id=16CaxHtytsw-kfsQd0CVxukSe1oTnj7B_) | 54.94 |
| [200](https://drive.google.com/open?id=1tjCPsisG9mLCyRPDVFa4W9boBDXALOGL) | 69.41 |
| [300](https://drive.google.com/open?id=1NEHKLFQ2z4cYsdbFxEeU0UCjlDDx_tal) | 71.29 |
| [400](https://drive.google.com/open?id=1mJG-28ay__bTKHGIxeShM2wGKOdzI2M3) | 71.80 |

As you can see, the vector size can influence the word relation test performance, and within a certain range, the larger vector size, the better performance.
