"""
TypingEngine
------------
Handles real-time comparison of user input against target text.
Designed to be lightweight — create once per session, call compare()
repeatedly rather than re-instantiating on every keystroke.
"""

from enum import Enum
from typing import List, Tuple


class CharStatus(Enum):
    UNTYPED   = 0
    CORRECT   = 1
    INCORRECT = 2


class TypingEngine:
    """Compare user input to a target string character-by-character."""

    def __init__(self, target_text: str) -> None:
        self.target = target_text

    def compare(self, user_input: str) -> Tuple[List[CharStatus], int]:
        """
        Return (statuses, cursor_pos) where:
          • statuses[i] reflects whether target[i] was typed correctly.
          • cursor_pos is the index of the next character to type,
            capped at len(target) so callers never need a bounds-check.
        """
        statuses: List[CharStatus] = []
        for i, target_char in enumerate(self.target):
            if i < len(user_input):
                status = CharStatus.CORRECT if user_input[i] == target_char else CharStatus.INCORRECT
                statuses.append(status)
            else:
                statuses.append(CharStatus.UNTYPED)

        cursor_pos = min(len(user_input), len(self.target))
        return statuses, cursor_pos
