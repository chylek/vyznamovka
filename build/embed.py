"""Embed vocab lemmas with an Ollama embedding model -> data/emb-<model>.npy (float16, L2-normalised).
usage: embed.py MODEL N [TEMPLATE]   TEMPLATE uses {w}, default '{w}'"""
import sys, time, numpy as np, requests
model, n = sys.argv[1], int(sys.argv[2])
tpl = sys.argv[3] if len(sys.argv) > 3 else "{w}"
words = [l.split("\t")[0] for l in open("data/vocab.tsv")][:n]
out, t0 = [], time.time()
for i in range(0, n, 64):
    r = requests.post("http://localhost:11434/api/embed",
                      json={"model": model, "input": [tpl.format(w=w) for w in words[i:i+64]]}, timeout=600)
    r.raise_for_status()
    out += r.json()["embeddings"]
    if i % 2048 == 0:
        print(i, f"{time.time()-t0:.0f}s", flush=True)
e = np.array(out, dtype=np.float32)
e /= np.linalg.norm(e, axis=1, keepdims=True)
np.save(f"data/emb-{model.replace(':','_').replace('/','_')}.npy", e.astype(np.float16))
print("done", e.shape, f"{time.time()-t0:.0f}s")
