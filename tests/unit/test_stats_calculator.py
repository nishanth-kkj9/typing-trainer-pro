from typing_trainer.core.stats_calculator import StatsCalculator
from typing_trainer.core.typing_engine import CharStatus

calculator = StatsCalculator()


class TestStatsCalculatorWPM:
    def test_zero_elapsed(self):
        assert calculator.calculate_wpm(50, 0) == 0.0

    def test_negative_elapsed(self):
        assert calculator.calculate_wpm(50, -1) == 0.0

    def test_typical_wpm(self):
        wpm = calculator.calculate_wpm(50, 30)
        assert round(wpm, 1) == 20.0

    def test_high_wpm(self):
        wpm = calculator.calculate_wpm(250, 60)
        assert round(wpm, 1) == 50.0

    def test_zero_correct_chars(self):
        wpm = calculator.calculate_wpm(0, 60)
        assert wpm == 0.0

    def test_precision(self):
        wpm = calculator.calculate_wpm(37, 29)
        assert isinstance(wpm, float)
        assert wpm > 0


class TestStatsCalculatorAccuracy:
    def test_nothing_typed(self):
        assert calculator.calculate_accuracy(0, 0) == 100.0

    def test_perfect_accuracy(self):
        assert calculator.calculate_accuracy(100, 100) == 100.0

    def test_half_accuracy(self):
        assert calculator.calculate_accuracy(50, 100) == 50.0

    def test_no_accuracy(self):
        assert calculator.calculate_accuracy(0, 100) == 0.0

    def test_precision(self):
        acc = calculator.calculate_accuracy(1, 3)
        assert round(acc, 1) == 33.3


class TestStatsCalculatorCountErrors:
    def test_no_errors(self):
        statuses = [CharStatus.CORRECT] * 5
        assert calculator.count_errors(statuses) == 0

    def test_all_errors(self):
        statuses = [CharStatus.INCORRECT] * 5
        assert calculator.count_errors(statuses) == 5

    def test_mixed(self):
        statuses = [
            CharStatus.CORRECT,
            CharStatus.INCORRECT,
            CharStatus.UNTYPED,
            CharStatus.INCORRECT,
            CharStatus.CORRECT,
        ]
        assert calculator.count_errors(statuses) == 2

    def test_empty_list(self):
        assert calculator.count_errors([]) == 0

    def test_only_untyped(self):
        statuses = [CharStatus.UNTYPED] * 3
        assert calculator.count_errors(statuses) == 0
