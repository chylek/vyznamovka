"""Pick secret words: the hand-curated 2022 list plus Jev-vetted common words,
shuffled with a fixed seed. Writes data/secrets.txt (one per line, day order)."""
import random, sys
sys.path.insert(0, "build"); from jev import noul
DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 365
words = open("data/words.txt").read().split()
have = set(words)
old = open("build/secrets-2022.txt").read().split()  # hand-picked for the 2022 server version
old = [w for w in old if w in have]
cand = [w for w in words[300:5000] if w not in set(old)]
p = noul({"language": "Czech"}, [
    f"Would „{w}“ make a good secret word for a daily Czech word-guessing game like Semantle? Good = a common, "
    "everyday Czech word in its dictionary form (noun, verb, adjective or adverb). Bad = proper name, place, brand, "
    "abbreviation, English word, inflected form or vulgarism." for w in cand])
good = [w for w, x in zip(cand, p) if x > 0.8]
print(len(old), "old,", len(good), "vetted new")
rng = random.Random(2026)
rng.shuffle(good)
sec = old + good[: max(0, DAYS - len(old))]
rng.shuffle(sec)
open("data/secrets.txt", "w").write("\n".join(sec) + "\n")
print(len(sec), "secrets:", sec[:20])
