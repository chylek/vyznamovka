# Semantle clone 

This is the code + guide that should enable you to create a Semantle clone in Czech language - [Významovka](https://vyznamovka.chylek.eu).

See the `word2vec-syn` directory to learn how to create the word2vec vector binaries from the [SYN v9 dataset](https://korpus.cz). The dataset (and derived work like word2vec vectors) is available only for non-commercial use, see [LINDAT/CLARIN](https://lindat.cz/repository/xmlui/handle/11234/1-4635). Alternatively you can use Wikipedia dump approach in `word2vec-wiki`, but I find the game more difficult with its non-lemmatized word forms. Additional step to lemmatize the words may be needed in that case.

Edit the `server.py` script so the `w2v_path` variable points to the word2vec vector binary. The Tornado server will listen on port 8888. This  also has to be changed in code. I am too lazy to change it to CLI arguments, sorry. 

Use pip to install the dependencies from `requirements.txt`. I'm using Python 3.10, but it should run with any reasonably young Python 3.

The worst thing is that the server has hardcoded list of the "secret" solutions to the daily riddle. It was created by hand using the [SYN2015-based  word frequency corpus](https://wiki.korpus.cz/doku.php/seznamy:srovnavaci_seznamy) and filtering out obviously useless parts of speech.

The server also serves the static/index.html page that also contains the CSS and JavaScript. This is not a pretty sight, I know. Maybe if it starts making me money I will think about doing it the proper way. Or create PR.

Enjoy your [Semantle](https://semantle.com) clone.