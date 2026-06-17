import pytest
from typing_trainer.core.sentence_generator import SentenceGenerator


@pytest.fixture
def generator():
    gen = SentenceGenerator()
    gen.set_seed(42)
    return gen


class TestSentenceGenerator:
    def test_generate_easy(self, generator):
        sentence = generator.generate("easy")
        assert isinstance(sentence, str)
        assert len(sentence) > 0
        assert sentence[0].isupper()
        assert sentence.endswith(".")

    def test_generate_medium(self, generator):
        sentence = generator.generate("medium")
        assert isinstance(sentence, str)
        assert len(sentence) > 0
        assert sentence[0].isupper()

    def test_generate_hard(self, generator):
        sentence = generator.generate("hard")
        assert isinstance(sentence, str)
        assert len(sentence) > 0
        assert sentence[0].isupper()

    def test_invalid_difficulty(self, generator):
        with pytest.raises(ValueError):
            generator.generate("invalid")

    def test_uniqueness(self, generator):
        sentences = {generator.generate("easy") for _ in range(5)}
        assert len(sentences) >= 4  # at least 4 unique out of 5

    def test_seed_reproducibility(self):
        gen1 = SentenceGenerator()
        gen1.set_seed(42)
        result = gen1.generate("easy")

        gen2 = SentenceGenerator()
        gen2.set_seed(42)
        assert gen2.generate("easy") == result

    def test_different_seeds(self):
        gen1 = SentenceGenerator()
        gen2 = SentenceGenerator()
        gen1.set_seed(1)
        gen2.set_seed(2)
        results = {gen1.generate("easy"), gen2.generate("easy")}
        assert len(results) == 2

    def test_generate_paragraph(self, generator):
        paragraph = generator.generate_paragraph("easy", 3)
        assert isinstance(paragraph, str)
        assert len(paragraph) > 0
        sentences = [s.strip() for s in paragraph.split(".") if s.strip()]
        assert len(sentences) == 3

    def test_difficulty_levels_differ(self, generator):
        easy = generator.generate("easy")
        medium = generator.generate("medium")
        hard = generator.generate("hard")
        difficulties = {easy, medium, hard}
        assert len(difficulties) == 3

    def test_easy_sentence_format(self, generator):
        for _ in range(10):
            s = generator.generate("easy")
            assert s[0].isupper()
            assert s.endswith(".")

    def test_medium_sentence_ends_with_period(self, generator):
        for _ in range(10):
            s = generator.generate("medium")
            assert s[0].isupper()
            assert s.endswith(".")

    def test_hard_sentence_complexity(self, generator):
        hard_words = generator.generate("hard").rstrip(".").split()
        assert len(hard_words) >= 8

    def test_history_exhaustion_fallback(self):
        gen = SentenceGenerator(history_size=2)
        gen.set_seed(42)
        for _ in range(5):
            s = gen.generate("easy")
            assert isinstance(s, str)
