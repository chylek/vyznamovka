import time
import sys

infilePath = sys.argv[1]
outfilePath = sys.argv[2]

count_sent = 0

start_time = time.time()
current_sent = []
with open(infilePath, 'r', encoding="utf8") as fr, open(outfilePath, "w") as fw:
    for line in fr:
        if line.startswith("<s"):
            if current_sent and len(current_sent)>20:
                count_sent+=1

                if count_sent % 2000 == 0:
                    elapsed_time = time.time() - start_time
                    print('Processed sentence number:', count_sent, 'Elapsed time:', elapsed_time, 's')
                fw.write(" ".join(current_sent)+"\n")
            del current_sent[:]
        elif line.startswith("<g"):
            continue
        elif line.startswith("\""):
            continue
        elif line.startswith("<"):
            continue
        else:
            splt = line.strip().split("\t")
            tok = splt[3]
            if "|" in tok:
                tok = tok.split("|")[0]
            if tok in ",.:?!-­֊᐀᠆‐‑‧⁃⸗⸚⹀゠﹣－󠀭‒–—⁓⊝⑈┄┅┆┇┈┉┊┋╌╍╎╏⤌⤍⤎⤏⤐⥪⥫⥬⥭⩜⩝⫘⫦⬷⸺⸻⹃〜〰︱︲﹘\"«»‘’‚‛“”„‟‹›❛❜❝❞❟❠❮❯⹂〝〞〟＂🙶🙷🙸!#$%&\'()*+/:;<=>?@[\\]^_`{|}~":
                continue
            current_sent.append(tok)
        