# download the latest English wikipedia dump
# LANG=en
LANG=cs
DUMP=${LANG}wiki-latest-pages-articles.xml.bz2
curl -L -O "https://dumps.wikimedia.org/${LANG}wiki/latest/$DUMP"

# extract and clean texts from downloaded wikipedia dump
mkdir -p extracted
python WikiExtractor.py $DUMP -b 1G -o extracted --no-template --processes 24

# process the extracted wiki text corpus including: splitting the sentence, sentence tokenization,
# removing sentences that contain less than 20 characters or less then 5 tokens,
# converting all numerals into 0, say, 1993 converted to 0000
mkdir -p processed
for i in {00..14};
do
	python wiki-corpus-prepare.py extracted/${LANG}/wiki_$i processed/wiki_${LANG}_$i &
done

# merge all the wikipedia text file
cat processed/wiki_${LANG}* > processed/${LANG}wiki

# train the word embeddings using skipgram model
mkdir -p results
cd word2vec
./word2vec -train ../processed/${LANG}wiki -output ../results/${LANG}wiki.skip.size300.win10.neg15.sample1e-5.min15.bin -cbow 0 -size 300 -window 10 -negative 15 -hs 0 -sample 1e-5 -threads 24 -binary 1 -min-count 15

# test the performace of word embeddings on word relation test set
./compute-accuracy ../results/${LANG}wiki.skip.size300.win10.neg15.sample1e-5.min15.bin < questions-words.txt