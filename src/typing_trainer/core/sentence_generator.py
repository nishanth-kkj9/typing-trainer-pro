"""
SentenceGenerator
-----------------
Generates grammatically correct English sentences at runtime using
pre-defined word pools and templates.  No external files, APIs, or
heavy libraries required.
"""

import random
from collections import deque
from typing import List, Optional


class SentenceGenerator:
    """
    Lightweight sentence generator with three difficulty levels.
    Sentences are built from curated word lists and fill-in templates.
    """

    # ── Word Pools ────────────────────────────────────────────────────────

    EASY_NOUNS = [
        "cat", "dog", "bird", "car", "book", "house", "tree", "ball",
        "girl", "boy", "mom", "dad", "sun", "moon", "fish", "frog",
    ]
    EASY_VERBS = [
        "run", "jump", "play", "read", "eat", "sleep", "swim", "sing",
        "dance", "draw", "walk", "talk", "see", "like", "make", "help",
    ]
    EASY_ADJECTIVES = [
        "big", "small", "red", "blue", "happy", "sad", "fast", "slow",
        "hot", "cold", "new", "old", "good", "bad", "tall", "short",
    ]
    EASY_ADVERBS = [
        "quickly", "slowly", "happily", "loudly", "softly", "well", "badly", "fast",
    ]

    MEDIUM_NOUNS = [
        "student", "teacher", "computer", "garden", "library", "market",
        "window", "bottle", "picture", "journey", "village", "problem",
        "message", "concert", "restaurant", "mountain",
    ]
    MEDIUM_VERBS = [
        "discover", "imagine", "prepare", "explore", "describe", "consider",
        "arrange", "collect", "connect", "develop", "explain", "improve",
        "observe", "perform", "receive", "suggest",
    ]
    MEDIUM_ADJECTIVES = [
        "beautiful", "interesting", "important", "different", "difficult",
        "comfortable", "expensive", "friendly", "helpful", "popular",
        "serious", "strange", "terrible", "wonderful", "ancient", "modern",
    ]
    MEDIUM_ADVERBS = [
        "carefully", "easily", "finally", "generally", "immediately",
        "perfectly", "probably", "suddenly", "usually", "actually",
        "certainly", "completely", "exactly", "naturally", "recently",
    ]

    HARD_NOUNS = [
        "hypothesis", "phenomenon", "methodology", "implementation",
        "configuration", "infrastructure", "collaboration", "algorithm",
        "equilibrium", "biodiversity", "consciousness", "civilization",
        "jurisdiction", "philosophy", "sustainability", "entrepreneur",
    ]
    HARD_VERBS = [
        "synchronize", "extrapolate", "disseminate", "corroborate",
        "differentiate", "encapsulate", "facilitate", "incorporate",
        "orchestrate", "perpetuate", "reconcile", "scrutinize",
        "substantiate", "transcend", "validate", "calibrate",
    ]
    HARD_ADJECTIVES = [
        "unprecedented", "paradoxical", "multifaceted", "heterogeneous",
        "indispensable", "ephemeral", "ubiquitous", "meticulous",
        "ambivalent", "cognizant", "dichotomous", "exponential",
        "intrinsic", "juxtaposed", "quintessential", "reciprocal",
    ]
    HARD_ADVERBS = [
        "unequivocally", "paradoxically", "simultaneously", "consequently",
        "nevertheless", "furthermore", "notwithstanding", "subsequently",
        "invariably", "predominantly", "exponentially", "intrinsically",
        "ostensibly", "concurrently", "allegedly", "inadvertently",
    ]

    # ── Templates ─────────────────────────────────────────────────────────

    EASY_TEMPLATES = [
        "The {adj} {noun} {verb}s.",
        "A {noun} can {verb}.",
        "I {verb} the {adj} {noun}.",
        "{noun}s {verb} {adv}.",
        "This {noun} is {adj}.",
        "My {noun} likes to {verb}.",
        "The {noun} is very {adj}.",
        "We {verb} the {noun}.",
        "She has a {adj} {noun}.",
        "He {verb}s every day.",
    ]

    MEDIUM_TEMPLATES = [
        "The {adj} {noun} {adv} {verb}s the {noun}.",
        "A {adj} {noun} can {adv} {verb} the {noun}.",
        "I {adv} {verb} the {adj} {noun} in the {noun}.",
        "The {noun} {verb}s {adv} because it is {adj}.",
        "After the {noun}, we {adv} {verb} the {adj} {noun}.",
        "The {adj} {noun} and the {adj} {noun} {verb} together.",
        "She {adv} {verb}s the {adj} {noun} for her {noun}.",
        "It is {adj} to {verb} the {noun} {adv}.",
        "The {noun} has a {adj} {noun} that {verb}s {adv}.",
        "Many {noun}s {adv} {verb} the {adj} {noun}.",
    ]

    HARD_TEMPLATES = [
        "The {adj} {noun}, which was {adv} {adj}, {verb}ed the {adj} {noun}.",
        "Although the {adj} {noun} {adv} {verb}ed, the {adj} {noun} remained {adj}.",
        "The {adj} {noun} {adv} {verb}ed the {adj} {noun}; consequently, the {noun} became {adj}.",
        "If the {adj} {noun} {verb}s {adv}, then the {adj} {noun} will {adv} {verb}.",
        "The {noun}'s {adj} {noun} was {adv} {adj} — a fact that could not be ignored.",
        "Having {adv} {verb}ed the {adj} {noun}, the {noun} felt {adj} and {adj}.",
        "The {adj} {noun}, together with its {adj} {noun}, {adv} {verb}ed the {adj} {noun}.",
        "Not only did the {adj} {noun} {verb} {adv}, but it also {adv} {verb}ed the {noun}.",
        "The {adj} {noun} {adv} {verb}ed; furthermore, it {adv} {verb}ed the {adj} {noun}.",
        "Because the {adj} {noun} was {adv} {adj}, the {noun} {adv} {verb}ed the {adj} {noun}.",
    ]

    # ── Public API ─────────────────────────────────────────────────────────

    def __init__(self, history_size: int = 10) -> None:
        self.history: deque = deque(maxlen=history_size)
        self._seed: Optional[int] = None

    def set_seed(self, seed: Optional[int] = None) -> None:
        self._seed = seed
        random.seed(seed)

    def generate(self, difficulty: str) -> str:
        """Return a unique sentence for the given difficulty level."""
        difficulty = difficulty.lower()
        if difficulty not in ("easy", "medium", "hard"):
            raise ValueError("Difficulty must be 'easy', 'medium', or 'hard'.")

        for _ in range(20):
            sentence = self._generate_one(difficulty)
            if sentence not in self.history:
                self.history.append(sentence)
                return sentence
        return sentence  # fallback after exhausted attempts

    def generate_paragraph(self, difficulty: str, sentences: int = 3) -> str:
        """Join *sentences* generated sentences into a paragraph."""
        return " ".join(self.generate(difficulty) for _ in range(sentences))

    # ── Internals ──────────────────────────────────────────────────────────

    def _generate_one(self, difficulty: str) -> str:
        dispatch = {"easy": self._generate_easy, "medium": self._generate_medium, "hard": self._generate_hard}
        return dispatch[difficulty]()

    def _generate_easy(self) -> str:
        return self._fill(random.choice(self.EASY_TEMPLATES),
                          self.EASY_NOUNS, self.EASY_VERBS,
                          self.EASY_ADJECTIVES, self.EASY_ADVERBS)

    def _generate_medium(self) -> str:
        return self._fill(random.choice(self.MEDIUM_TEMPLATES),
                          self.MEDIUM_NOUNS, self.MEDIUM_VERBS,
                          self.MEDIUM_ADJECTIVES, self.MEDIUM_ADVERBS)

    def _generate_hard(self) -> str:
        sentence = self._fill(random.choice(self.HARD_TEMPLATES),
                              self.HARD_NOUNS, self.HARD_VERBS,
                              self.HARD_ADJECTIVES, self.HARD_ADVERBS)
        if random.random() < 0.3:
            sentence = sentence.replace(";", random.choice([";", "—", ","]))
        return sentence

    def _fill(self, template: str, nouns: List[str], verbs: List[str],
              adjs: List[str], advs: List[str]) -> str:
        r = template
        while "{noun}"    in r: r = r.replace("{noun}",   random.choice(nouns), 1)
        while "{noun}s"   in r:
            n = random.choice(nouns)
            plural = n + ("es" if n.endswith(("s","x","ch","sh")) else "s")
            r = r.replace("{noun}s", plural, 1)
        while "{verb}"    in r: r = r.replace("{verb}",   random.choice(verbs), 1)
        while "{verb}s"   in r:
            v = random.choice(verbs)
            if   v.endswith(("s","x","ch","sh","o")): c = v + "es"
            elif v.endswith("y") and v[-2] not in "aeiou": c = v[:-1] + "ies"
            else: c = v + "s"
            r = r.replace("{verb}s", c, 1)
        while "{verb}ed"  in r:
            v = random.choice(verbs)
            past = v + "d" if v.endswith("e") else (v[:-1] + "ied" if v.endswith("y") and v[-2] not in "aeiou" else v + "ed")
            r = r.replace("{verb}ed", past, 1)
        while "{adj}"     in r: r = r.replace("{adj}",    random.choice(adjs),  1)
        while "{adv}"     in r: r = r.replace("{adv}",    random.choice(advs),  1)

        # Capitalise first character
        r = r[0].upper() + r[1:]

        # Fix "a" → "an" before vowel sounds
        words = r.split()
        for i, w in enumerate(words):
            if w.lower() == "a" and i + 1 < len(words):
                nw = words[i + 1].lower().lstrip("\"'")
                if nw and nw[0] in "aeiou":
                    words[i] = "An" if w[0].isupper() else "an"
        return " ".join(words)


if __name__ == "__main__":
    gen = SentenceGenerator()
    gen.set_seed(42)
    for diff in ("easy", "medium", "hard"):
        print(f"\n=== {diff.upper()} ===")
        for _ in range(5):
            print(gen.generate(diff))
