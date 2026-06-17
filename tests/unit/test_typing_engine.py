from typing_trainer.core.typing_engine import TypingEngine, CharStatus


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
        assert statuses[0] == CharStatus.CORRECT  # h
        assert statuses[1] == CharStatus.INCORRECT  # x vs e
        assert statuses[2] == CharStatus.CORRECT  # l
        assert statuses[3] == CharStatus.CORRECT  # l
        assert statuses[4] == CharStatus.CORRECT  # o
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
        assert len(statuses) == 2  # only 2 chars in target
        assert statuses[0] == CharStatus.CORRECT
        assert statuses[1] == CharStatus.INCORRECT  # i vs x mismatch
        assert pos == 2  # capped at len(target)

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
        assert statuses[3] == CharStatus.INCORRECT  # e vs é
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
