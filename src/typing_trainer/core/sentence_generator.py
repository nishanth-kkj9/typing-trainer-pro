import random
from collections import deque


class SentenceGenerator:
    EASY_NOUNS = [
        "cat", "dog", "bird", "car", "book", "house", "tree", "ball",
        "girl", "boy", "mom", "dad", "sun", "moon", "fish", "frog",
        "star", "door", "bell", "cake", "duck", "hand", "foot", "rain",
    ]
    EASY_VERBS = [
        "run", "jump", "play", "read", "eat", "sleep", "swim", "sing",
        "dance", "draw", "walk", "talk", "see", "like", "make", "help",
        "find", "give", "take", "hold", "pull", "push", "sit", "stand",
    ]
    EASY_ADJECTIVES = [
        "big", "small", "red", "blue", "happy", "sad", "fast", "slow",
        "hot", "cold", "new", "old", "good", "bad", "tall", "short",
        "soft", "hard", "wet", "dry", "clean", "dark", "bright", "empty",
    ]
    EASY_ADVERBS = [
        "quickly", "slowly", "happily", "loudly", "softly", "well", "badly", "fast",
        "gently", "neatly", "eagerly", "bravely", "cheerfully", "silently",
    ]

    MEDIUM_NOUNS = [
        "student", "teacher", "computer", "garden", "library", "market",
        "window", "bottle", "picture", "journey", "village", "problem",
        "message", "concert", "restaurant", "mountain", "captain", "doctor",
        "bridge", "castle", "dinner", "engine", "forest", "guitar",
    ]
    MEDIUM_VERBS = [
        "discover", "imagine", "prepare", "explore", "describe", "consider",
        "arrange", "collect", "connect", "develop", "explain", "improve",
        "observe", "perform", "receive", "suggest", "complete", "deliver",
        "encourage", "establish", "generate", "identify", "negotiate", "purchase",
    ]
    MEDIUM_ADJECTIVES = [
        "beautiful", "interesting", "important", "different", "difficult",
        "comfortable", "expensive", "friendly", "helpful", "popular",
        "serious", "strange", "terrible", "wonderful", "ancient", "modern",
        "brilliant", "curious", "elegant", "famous", "generous", "humble",
    ]
    MEDIUM_ADVERBS = [
        "carefully", "easily", "finally", "generally", "immediately",
        "perfectly", "probably", "suddenly", "usually", "actually",
        "certainly", "completely", "exactly", "naturally", "recently",
        "positively", "regularly", "similarly",
    ]

    HARD_NOUNS = [
        "hypothesis", "phenomenon", "methodology", "implementation",
        "configuration", "infrastructure", "collaboration", "algorithm",
        "equilibrium", "biodiversity", "consciousness", "civilization",
        "jurisdiction", "philosophy", "sustainability", "entrepreneur",
        "accountability", "authentication", "cryptography", "determinism",
    ]
    HARD_VERBS = [
        "synchronize", "extrapolate", "disseminate", "corroborate",
        "differentiate", "encapsulate", "facilitate", "incorporate",
        "orchestrate", "perpetuate", "reconcile", "scrutinize",
        "substantiate", "transcend", "validate", "calibrate",
        "conceptualize", "decentralize", "operationalize", "revolutionize",
    ]
    HARD_ADJECTIVES = [
        "unprecedented", "paradoxical", "multifaceted", "heterogeneous",
        "indispensable", "ephemeral", "ubiquitous", "meticulous",
        "ambivalent", "cognizant", "dichotomous", "exponential",
        "intrinsic", "juxtaposed", "quintessential", "reciprocal",
        "authoritative", "comprehensive", "deterministic", "interdisciplinary",
    ]
    HARD_ADVERBS = [
        "unequivocally", "paradoxically", "simultaneously", "consequently",
        "nevertheless", "furthermore", "notwithstanding", "subsequently",
        "invariably", "predominantly", "exponentially", "intrinsically",
        "ostensibly", "concurrently", "allegedly", "inadvertently",
        "categorically", "indisputably", "preferentially", "unambiguously",
    ]

    SYMBOLS_POOL = [";", ":", ",", ".", "!", "?"]
    PARENTHETICALS = ["(however)", "(therefore)", "(indeed)", "(for example)"]

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
        "The {adj} {noun} {verb}s {adv}.",
        "Look at the {adj} {noun}!",
        "Can you {verb} the {noun}?",
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
        "Why does the {adj} {noun} {verb} {adv}?",
        "The {adj} {noun}, however, {verb}s {adv}.",
        "I think the {noun} is {adj} and {adj}.",
    ]

    HARD_TEMPLATES = [
        "The {adj} {noun}, which was {adv} {adj}, {verb}ed the {adj} {noun}.",
        "Although the {adj} {noun} {adv} {verb}ed, the {adj} {noun} remained {adj}.",
        "The {adj} {noun} {adv} {verb}ed the {adj} {noun}; consequently, the {noun} became {adj}.",
        "If the {adj} {noun} {verb}s {adv}, then the {adj} {noun} will {adv} {verb}.",
        "The {noun}'s {adj} {noun} was {adv} {adj} \u2014 a fact that could not be ignored.",
        "Having {adv} {verb}ed the {adj} {noun}, the {noun} felt {adj} and {adj}.",
        "The {adj} {noun}, together with its {adj} {noun}, {adv} {verb}ed the {adj} {noun}.",
        "Not only did the {adj} {noun} {verb} {adv}, but it also {adv} {verb}ed the {noun}.",
        "The {adj} {noun} {adv} {verb}ed; furthermore, it {adv} {verb}ed the {adj} {noun}.",
        "Because the {adj} {noun} was {adv} {adj}, the {noun} {adv} {verb}ed the {adj} {noun}.",
        "The {adj} {noun} \u2014 a {adj} example of {noun} \u2014 {adv} {verb}ed.",
        "What if the {adj} {noun} had {adv} {verb}ed the {adj} {noun}?",
        "The {noun}: a {adj} {noun} that {verb}s {adv} and {adv}.",
        "Either the {adj} {noun} {verb}s {adv}, or the {adj} {noun} will {verb} {adv}.",
        "The {adj} {noun}, {adv}, {verb}ed; however, the {adj} {noun} {verb}ed {adv}.",
    ]

    TOPICS = {
        "science": {
            "nouns": ["hypothesis", "experiment", "laboratory", "phenomenon", "equation", "theory"],
            "verbs": ["analyze", "measure", "calculate", "observe", "verify", "demonstrate"],
            "adjs": ["scientific", "empirical", "quantifiable", "systematic", "theoretical", "rigorous"],
        },
        "technology": {
            "nouns": ["algorithm", "database", "server", "interface", "protocol", "pipeline"],
            "verbs": ["compile", "deploy", "encrypt", "synchronize", "optimize", "refactor"],
            "adjs": ["scalable", "modular", "asynchronous", "distributed", "redundant", "robust"],
        },
    }

    def __init__(self, history_size: int = 10) -> None:
        self.history: deque = deque(maxlen=history_size)
        self._seed: int | None = None

    def set_seed(self, seed: int | None = None) -> None:
        self._seed = seed
        random.seed(seed)

    def generate(self, difficulty: str, topic: str | None = None,
                 include_symbols: bool = False) -> str:
        difficulty = difficulty.lower()
        if difficulty not in ("easy", "medium", "hard"):
            raise ValueError("Difficulty must be 'easy', 'medium', or 'hard'.")

        sentence = ""
        for _ in range(20):
            sentence = self._generate_one(difficulty, topic, include_symbols)
            if sentence not in self.history:
                self.history.append(sentence)
                return sentence
        return sentence

    def generate_paragraph(self, difficulty: str, sentences: int = 3,
                           topic: str | None = None) -> str:
        return " ".join(self.generate(difficulty, topic) for _ in range(sentences))

    def _generate_one(self, difficulty: str, topic: str | None = None,
                      include_symbols: bool = False) -> str:
        if difficulty == "easy":
            sentence = self._generate_easy()
        elif difficulty == "medium":
            sentence = self._generate_medium()
        else:
            sentence = self._generate_hard()
        if include_symbols and difficulty in ("medium", "hard"):
            sentence = self._maybe_add_symbol(sentence)
        return sentence

    def _maybe_add_symbol(self, sentence: str) -> str:
        if random.random() < 0.3:
            sym = random.choice(self.SYMBOLS_POOL)
            if sym in ("!", "?"):
                sentence = sentence.rstrip(".") + sym
            elif sym in (":", ";"):
                words = sentence.split()
                if len(words) > 3:
                    idx = random.randint(1, len(words) - 2)
                    words.insert(idx, sym)
                    sentence = " ".join(words)
        return sentence

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
            sentence = sentence.replace(";", random.choice([";", "\u2014", ","]))
        return sentence

    def _fill(self, template: str, nouns: list[str], verbs: list[str],
              adjs: list[str], advs: list[str]) -> str:
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

        r = r[0].upper() + r[1:]

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
            print(gen.generate(diff, include_symbols=True))
