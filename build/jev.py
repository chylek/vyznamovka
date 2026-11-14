"""Tiny Jev (TypeSafe System One) client: batched yes/no probabilities."""
import json, os, subprocess, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

KEY = os.environ.get("JEV_API_KEY") or subprocess.run(
    [os.path.expanduser("~/claudecode/scripts/secrets.sh"), "JEV_API_KEY"],
    capture_output=True, text=True).stdout.strip()


def _call(state, questions):
    body = json.dumps({"model": "jev-latest", "state": state, "questions": questions}).encode()
    for attempt in range(5):
        try:
            req = urllib.request.Request("https://api.typesafe.ai/v1/systemone", body,
                                         {"Content-Type": "application/json", "Authorization": "Bearer " + KEY})
            a = json.load(urllib.request.urlopen(req, timeout=120))["answers"]
            return [a[k]["noul"] for k in questions]
        except Exception:
            if attempt == 4:
                raise
            time.sleep(2 ** attempt)


def noul(state, texts, batch=64, threads=6):
    """Probability that each instruction in `texts` is true about `state`."""
    chunks = [texts[i:i + batch] for i in range(0, len(texts), batch)]
    qs = [{f"q{j}": {"type": "noul", "instructions": t} for j, t in enumerate(c)} for c in chunks]
    with ThreadPoolExecutor(threads) as ex:
        return [p for r in ex.map(lambda q: _call(state, q), qs) for p in r]
