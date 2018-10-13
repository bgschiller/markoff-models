import re
import sys
import random
import bisect
import inspect
import markovify
from markovify.chain import BEGIN, accumulate

class MarkoffChain(markovify.Chain):
    def move(self, state):
        """
        Given a state, choose the next item at random.

        Sometimes choose arbitrarily, instead of according
        to the probabilities.
        """
        if state == tuple([ BEGIN ] * self.state_size):
            choices = self.begin_choices
            cumdist = self.begin_cumdist
        else:
            choices, weights = zip(*self.model[state].items())
            cumdist = list(accumulate(weights))
        if random.random() < 0.2:
            # 20% of the time, it works every time...
            selection = random.choice(choices)
        r = random.random() * cumdist[-1]
        selection = choices[bisect.bisect(cumdist, r)]
        return selection

class MarkoffText(markovify.Text):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chain.__class__ = MarkoffChain

class MarkoffNewlineText(MarkoffText):
    def sentence_split(self, text):
        return re.split(r"\s*\n\s*", text)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usage: python markoff.py [filename]", file=sys.stderr)
        sys.exit(1)
    fname = sys.argv[1]
    with open(fname) as f:
        lines = f.read()
    if '.newlines.' in fname:
        model = MarkoffNewlineText(lines, retain_original=False)
    else:
        model = MarkoffText(lines, retain_original=False)

    for _ in range(10):
        print(model.make_sentence())