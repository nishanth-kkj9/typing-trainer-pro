import pytest

from typing_trainer.services.stats_tracker import StatsTracker


@pytest.fixture
def target_text():
    return "the quick brown fox"


@pytest.fixture
def tracker(target_text):
    return StatsTracker(target_text)


class TestStatsTracker:
    def test_initial_state(self, tracker):
        assert tracker._elapsed_seconds == 0.0
        assert tracker._user_input == ""

    def test_update_time(self, tracker):
        tracker.update_time(30.0)
        assert tracker._elapsed_seconds == 30.0

    def test_update_input(self, tracker):
        tracker.update_input("the")
        assert tracker._user_input == "the"

    def test_combined_update(self, tracker):
        tracker.update("the", 15.0)
        assert tracker._user_input == "the"
        assert tracker._elapsed_seconds == 15.0

    def test_empty_input_stats(self, tracker):
        stats = None

        def capture(s):
            nonlocal stats
            stats = s

        tracker.stats_changed.connect(capture)
        tracker.update("", 0.0)
        assert stats is not None
        assert stats["wpm"] == 0.0
        assert stats["accuracy"] == 100.0
        assert stats["errors"] == 0
        assert stats["correct"] == 0
        assert stats["total_typed"] == 0

    def test_partial_correct_stats(self, tracker):
        stats = None

        def capture(s):
            nonlocal stats
            stats = s

        tracker.stats_changed.connect(capture)
        tracker.update("the", 10.0)
        assert stats is not None
        assert stats["correct"] == 3
        assert stats["total_typed"] == 3
        assert stats["errors"] == 0
        assert stats["accuracy"] == 100.0

    def test_partial_incorrect_stats(self, tracker):
        stats = None

        def capture(s):
            nonlocal stats
            stats = s

        tracker.stats_changed.connect(capture)
        tracker.update("xyz", 10.0)
        assert stats is not None
        assert stats["correct"] == 0
        assert stats["errors"] == 3
        assert stats["total_typed"] == 3
        assert stats["accuracy"] == 0.0

    def test_full_correct_run(self, tracker):
        stats = None

        def capture(s):
            nonlocal stats
            stats = s

        tracker.stats_changed.connect(capture)
        tracker.update("the quick brown fox", 60.0)
        assert stats is not None
        assert stats["correct"] == 19
        assert stats["errors"] == 0
        assert stats["total_typed"] == 19
        assert stats["accuracy"] == 100.0

    def test_recalculate_dedup(self, tracker):
        emissions = []

        def capture(s):
            emissions.append(s)

        tracker.stats_changed.connect(capture)
        tracker.update("the", 10.0)
        tracker.update("the", 10.0)
        assert len(emissions) == 1  # second call deduped

    def test_recalculate_emits_on_change(self, tracker):
        emissions = []

        def capture(s):
            emissions.append(s)

        tracker.stats_changed.connect(capture)
        tracker.update("the", 10.0)
        tracker.update("them", 10.0)
        assert len(emissions) == 2
        assert emissions[0] != emissions[1]

    def test_wpm_formula_integration(self, tracker):
        stats = None

        def capture(s):
            nonlocal stats
            stats = s

        tracker.stats_changed.connect(capture)
        tracker.update("the quick brown fox", 60.0)
        assert stats is not None
        expected_wpm = round((19 / 5.0) / (60.0 / 60.0), 1)
        assert stats["wpm"] == expected_wpm

    def test_constructor_with_different_text(self):
        t = StatsTracker("hello world")
        assert t.engine.target == "hello world"

    def test_signal_is_qobject_signal(self):
        assert hasattr(StatsTracker, "stats_changed")
