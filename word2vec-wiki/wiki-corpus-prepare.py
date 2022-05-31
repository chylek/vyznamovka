## split texts to sentences
# from pycorenlp import StanfordCoreNLP
import re
from string import punctuation
import time
import sys
from nltk.tokenize import sent_tokenize, word_tokenize

# stdout = sys.stdout
# reload(sys)
# sys.setdefaultencoding('utf-8')
# sys.stdout = stdout
# nlp = StanfordCoreNLP('http://localhost:9000')

infilePath = sys.argv[1]
outfilePath = sys.argv[2]

splitted_texts = ''
count_articles = 0
count_tokens = 0
start_time = time.time()
outfile = open(outfilePath, 'w')
trans = str.maketrans('-­֊᐀᠆‐‑‧⁃⸗⸚⹀゠﹣－󠀭‒–—⁓⊝⑈┄┅┆┇┈┉┊┋╌╍╎╏⤌⤍⤎⤏⤐⥪⥫⥬⥭⩜⩝⫘⫦⬷⸺⸻⹃〜〰︱︲﹘', '--------------------------------------------------------', '"«»‘’‚‛“”„‟‹›❛❜❝❞❟❠❮❯⹂〝〞〟＂🙶🙷🙸!"#$%&\'()*+/:;<=>?@[\\]^_`{|}~')

with open(infilePath, 'r') as f:
    for text in f:
        text = text.strip()
        if len(text) > 20:
            if not text.startswith('<doc id='):
                text = re.sub('\d', '0', text)
                text = text.translate(punctuation)
                try:
                    sents = []
                    for sent in sent_tokenize(text):
                        wt = word_tokenize(sent)
                        wt[0]=wt[0].lower()
                        if len(wt)>5:
                            sents.append(list(t for t in wt if t not in "().,"))
                except Exception as e:
                    print(e.message, text)
                else:
                    for sent in sents:
                        outfile.write(' '.join(sent)+'\n')
                        count_tokens += len(sent)

            else:
                count_articles += 1
                if count_articles % 2000 == 0:
                    elapsed_time = time.time() - start_time
                    print (infilePath.split('/')[-1], 'Processed article number:', count_articles, 'Elapsed time:', elapsed_time, 's')