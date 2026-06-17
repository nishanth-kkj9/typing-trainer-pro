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


class TestStatsCalculatorCPM:
    def test_zero_elapsed(self):
        assert calculator.calculate_cpm(50, 0) == 0.0

    def test_typical_cpm(self):
        cpm = calculator.calculate_cpm(100, 60)
        assert cpm == 100.0

    def test_cpm_relationship_to_wpm(self):
        cpm = calculator.calculate_cpm(50, 60)
        wpm = calculator.calculate_wpm(50, 60)
        assert cpm == wpm * 5


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


class TestStatsCalculatorCountCorrect:
    def test_all_correct(self):
        statuses = [CharStatus.CORRECT] * 5
        assert calculator.count_correct(statuses) == 5

    def test_mixed(self):
        statuses = [CharStatus.CORRECT, CharStatus.INCORRECT, CharStatus.UNTYPED]
        assert calculator.count_correct(statuses) == 1

    def test_empty(self):
        assert calculator.count_correct([]) == 0


class TestStatsCalculatorConsistency:
    def test_empty_statuses(self):
        assert calculator.calculate_consistency([]) == 100.0

    def test_perfect_consistency(self):
        statuses = [CharStatus.CORRECT] * 10
        assert calculator.calculate_consistency(statuses) == 100.0

    def test_some_errors(self):
        statuses = [
            CharStatus.CORRECT, CharStatus.CORRECT, CharStatus.CORRECT,
            CharStatus.INCORRECT,
            CharStatus.CORRECT, CharStatus.CORRECT,
        ]
        score = calculator.calculate_consistency(statuses)
        assert 0.0 < score < 100.0

    def test_all_errors(self):
        statuses = [CharStatus.INCORRECT] * 5
        assert calculator.calculate_consistency(statuses) == 0.0


class TestStatsCalculatorErrorRatePerKey:
    def test_empty(self):
        assert calculator.calculate_error_rate_per_key([], "") == {}

    def test_no_errors(self):
        statuses = [CharStatus.CORRECT] * 3
        rates = calculator.calculate_error_rate_per_key(statuses, "abc")
        assert all(v == 0.0 for v in rates.values())

    def test_some_errors(self):
        target = "aabbc"
        statuses = [
            CharStatus.CORRECT,    # a
            CharStatus.INCORRECT,  # a
            CharStatus.CORRECT,    # b
            CharStatus.CORRECT,    # b
            CharStatus.CORRECT,    # c
        ]
        rates = calculator.calculate_error_rate_per_key(statuses, target)
        assert rates["A"] == 50.0
        assert rates["B"] == 0.0
        assert rates["C"] == 0.0


class TestStatsCalculatorNetWPM:
    def test_zero_elapsed(self):
        assert calculator.calculate_net_wpm(50, 0, 0) == 0.0

    def test_typical(self):
        net = calculator.calculate_net_wpm(100, 10, 60)
        assert round(net, 1) == 18.0

    def test_errors_exceed_correct(self):
        net = calculator.calculate_net_wpm(10, 30, 60)
        assert net == 0.0

    def test_no_errors(self):
        net = calculator.calculate_net_wpm(50, 0, 60)
        assert net == 10.0


class TestStatsCalculatorCalculateAll:
    def test_returns_all_keys(self):
        statuses = [CharStatus.CORRECT] * 10
        result = calculator.calculate_all(10, 10, 0, 60.0, statuses, "helloworld")
        assert "wpm" in result
        assert "cpm" in result
        assert "net_wpm" in result
        assert "accuracy" in result
        assert "errors" in result
        assert "correct" in result
        assert "total_typed" in result
        assert "consistency" in result
        assert "error_rates_per_key" in result

    def test_accuracy_perfect(self):
        statuses = [CharStatus.CORRECT] * 10
        result = calculator.calculate_all(10, 10, 0, 60.0, statuses, "helloworld")
        assert result["accuracy"] == 100.0

    def test_errors_reflected(self):
        target = "abc"
        statuses = [CharStatus.CORRECT, CharStatus.INCORRECT, CharStatus.CORRECT]
        result = calculator.calculate_all(2, 3, 1, 60.0, statuses, target)
        assert result["errors"] == 1
        assert result["correct"] == 2
        assert result["total_typed"] == 3
