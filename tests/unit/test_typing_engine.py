from typing_trainer.core.typing_engine import CharStatus, TypingEngine


class TestCharStatus:
    def test_enum_values(self):
        assert CharStatus.UNTYPED.value == 0
        assert CharStatus.CORRECT.value == 1
        assert CharStatus.INCORRECT.value == 2

    def test_enum_members(self):
        assert len(CharStatus) == 3


class TestTypingEngine:
    def test_empty_target(self):
        engine = TypingEngine("")
        statuses, pos = engine.compare("")
        assert statuses == []
        assert pos == 0

    def test_all_correct(self):
        engine = TypingEngine("hello")
        statuses, pos = engine.compare("hello")
        assert all(s == CharStatus.CORRECT for s in statuses)
        assert pos == 5

    def test_all_incorrect(self):
        engine = TypingEngine("hello")
        statuses, pos = engine.compare("xxxxx")
        assert all(s == CharStatus.INCORRECT for s in statuses)
        assert pos == 5

    def test_mixed_input(self):
        engine = TypingEngine("hello")
        statuses, pos = engine.compare("hxllo")
        assert statuses[0] == CharStatus.CORRECT
        assert statuses[1] == CharStatus.INCORRECT
        assert statuses[2] == CharStatus.CORRECT
        assert statuses[3] == CharStatus.CORRECT
        assert statuses[4] == CharStatus.CORRECT
        assert pos == 5

    def test_partial_input(self):
        engine = TypingEngine("hello world")
        statuses, pos = engine.compare("hel")
        assert statuses[0] == CharStatus.CORRECT
        assert statuses[1] == CharStatus.CORRECT
        assert statuses[2] == CharStatus.CORRECT
        assert statuses[3] == CharStatus.UNTYPED
        assert pos == 3

    def test_no_input(self):
        engine = TypingEngine("hello")
        statuses, pos = engine.compare("")
        assert all(s == CharStatus.UNTYPED for s in statuses)
        assert pos == 0

    def test_input_exceeds_target(self):
        engine = TypingEngine("hi")
        statuses, pos = engine.compare("hxxxx")
        assert len(statuses) == 2
        assert statuses[0] == CharStatus.CORRECT
        assert statuses[1] == CharStatus.INCORRECT
        assert pos == 2

    def test_cursor_position_capped(self):
        engine = TypingEngine("abc")
        _, pos = engine.compare("abcdefg")
        assert pos == 3

    def test_unicode_support(self):
        engine = TypingEngine("café")
        statuses, pos = engine.compare("café")
        assert all(s == CharStatus.CORRECT for s in statuses)
        assert pos == 4

    def test_unicode_incorrect(self):
        engine = TypingEngine("café")
        statuses, pos = engine.compare("cafe")
        assert statuses[0] == CharStatus.CORRECT
        assert statuses[1] == CharStatus.CORRECT
        assert statuses[2] == CharStatus.CORRECT
        assert statuses[3] == CharStatus.INCORRECT
        assert pos == 4

    def test_empty_target_empty_input(self):
        engine = TypingEngine("")
        statuses, pos = engine.compare("")
        assert statuses == []
        assert pos == 0

    def test_single_char_target(self):
        engine = TypingEngine("a")
        statuses, pos = engine.compare("a")
        assert statuses == [CharStatus.CORRECT]
        assert pos == 1

    def test_repeated_calls(self):
        engine = TypingEngine("hello")
        s1, p1 = engine.compare("h")
        s2, p2 = engine.compare("he")
        s3, p3 = engine.compare("hel")
        assert p1 == 1
        assert p2 == 2
        assert p3 == 3
        assert s1[0] == CharStatus.CORRECT
        assert s2[1] == CharStatus.CORRECT
        assert s3[2] == CharStatus.CORRECT

    def test_case_sensitive_default(self):
        engine = TypingEngine("Hello")
        statuses, pos = engine.compare("hello")
        assert statuses[0] == CharStatus.INCORRECT
        assert pos == 5

    def test_case_insensitive(self):
        engine = TypingEngine("Hello", case_sensitive=False)
        statuses, pos = engine.compare("hello")
        assert all(s == CharStatus.CORRECT for s in statuses)
        assert pos == 5

    def test_case_insensitive_all_upper(self):
        engine = TypingEngine("hello", case_sensitive=False)
        statuses, pos = engine.compare("HELLO")
        assert all(s == CharStatus.CORRECT for s in statuses)

    def test_error_positions_tracked(self):
        engine = TypingEngine("hello world")
        engine.compare("hxllo wortd")
        positions = engine.get_error_positions()
        assert 1 in positions
        assert positions == [1, 9]

    def test_error_positions_empty_when_correct(self):
        engine = TypingEngine("hello")
        engine.compare("hello")
        assert engine.get_error_positions() == []

    def test_backspace_simulation(self):
        result = TypingEngine._simulate_backspace("hel\blo")
        assert result == "helo"

    def test_backspace_multiple(self):
        result = TypingEngine._simulate_backspace("wor\b\bld")
        assert result == "wld"

    def test_backspace_at_start(self):
        result = TypingEngine._simulate_backspace("\bhello")
        assert result == "hello"

    def test_compare_with_backspace(self):
        engine = TypingEngine("hello")
        statuses, pos, bsp_count = engine.compare_with_backspace("h\belloo")
        assert bsp_count >= 1
        assert pos == 5

    def test_reset_with_new_target(self):
        engine = TypingEngine("hello")
        engine.compare("xxxxx")
        engine.reset("world")
        statuses, pos = engine.compare("world")
        assert all(s == CharStatus.CORRECT for s in statuses)
        assert engine.target == "world"

    def test_get_error_rate_per_key(self):
        engine = TypingEngine("hello world")
        engine.compare("hxllo world")
        rates = engine.get_error_rate_per_key()
        assert "E" in rates
        assert rates["E"] == 1
