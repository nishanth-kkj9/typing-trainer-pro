from enum import Enum


class CharStatus(Enum):
    UNTYPED   = 0
    CORRECT   = 1
    INCORRECT = 2


class TypingEngine:
    def __init__(self, target_text: str, case_sensitive: bool = True) -> None:
        self.target = target_text
        self.case_sensitive = case_sensitive
        self._error_positions: list[int] = []
        self._backspace_count: int = 0

    def compare(self, user_input: str) -> tuple[list[CharStatus], int]:
        statuses: list[CharStatus] = []
        self._backspace_count = 0
        self._error_positions = []

        for i, target_char in enumerate(self.target):
            if i < len(user_input):
                typed = user_input[i]
                if not self.case_sensitive:
                    match = typed.upper() == target_char.upper()
                else:
                    match = typed == target_char
                if match:
                    statuses.append(CharStatus.CORRECT)
                else:
                    statuses.append(CharStatus.INCORRECT)
                    self._error_positions.append(i)
            else:
                statuses.append(CharStatus.UNTYPED)

        cursor_pos = min(len(user_input), len(self.target))
        return statuses, cursor_pos

    def compare_with_backspace(self, user_input: str) -> tuple[list[CharStatus], int, int]:
        statuses, cursor_pos = self.compare(user_input)
        projected = self._simulate_backspace(user_input)
        self._backspace_count = len(user_input) - len(projected)
        return statuses, cursor_pos, self._backspace_count

    @staticmethod
    def _simulate_backspace(text: str) -> str:
        result = []
        for ch in text:
            if ch == '\b' or ch == '\x7f':
                if result:
                    result.pop()
            else:
                result.append(ch)
        return ''.join(result)

    def get_error_positions(self) -> list[int]:
        return self._error_positions.copy()

    def get_error_rate_per_key(self) -> dict:
        if not self.target:
            return {}
        rates = {}
        for pos in self._error_positions:
            ch = self.target[pos]
            key = ch.upper()
            rates[key] = rates.get(key, 0) + 1
        return rates

    def reset(self, target_text: str | None = None) -> None:
        if target_text:
            self.target = target_text
        self._error_positions = []
        self._backspace_count = 0
