
from typing_trainer.core.typing_engine import CharStatus


class StatsCalculator:
    @staticmethod
    def calculate_wpm(correct_chars: int, elapsed_seconds: float) -> float:
        if elapsed_seconds <= 0:
            return 0.0
        return (correct_chars / 5.0) / (elapsed_seconds / 60.0)

    @staticmethod
    def calculate_cpm(correct_chars: int, elapsed_seconds: float) -> float:
        if elapsed_seconds <= 0:
            return 0.0
        return correct_chars / (elapsed_seconds / 60.0)

    @staticmethod
    def calculate_accuracy(correct_chars: int, total_typed: int) -> float:
        if total_typed == 0:
            return 100.0
        return (correct_chars / total_typed) * 100.0

    @staticmethod
    def count_errors(statuses: list[CharStatus]) -> int:
        return sum(1 for s in statuses if s == CharStatus.INCORRECT)

    @staticmethod
    def count_correct(statuses: list[CharStatus]) -> int:
        return sum(1 for s in statuses if s == CharStatus.CORRECT)

    @staticmethod
    def calculate_consistency(statuses: list[CharStatus]) -> float:
        total = len(statuses)
        if total == 0:
            return 100.0
        chunks = []
        current = 0
        for s in statuses:
            if s == CharStatus.CORRECT:
                current += 1
            else:
                if current > 0:
                    chunks.append(current)
                current = 0
        if current > 0:
            chunks.append(current)
        if not chunks:
            return 0.0
        avg_chunk = sum(chunks) / len(chunks)
        max_possible = total
        return (avg_chunk / max_possible) * 100 if max_possible > 0 else 100.0

    @staticmethod
    def calculate_error_rate_per_key(statuses: list[CharStatus], target: str) -> dict[str, float]:
        if not target or len(statuses) != len(target):
            return {}
        key_errors: dict[str, int] = {}
        key_total: dict[str, int] = {}
        for i, ch in enumerate(target):
            key = ch.upper()
            key_total[key] = key_total.get(key, 0) + 1
            if i < len(statuses) and statuses[i] == CharStatus.INCORRECT:
                key_errors[key] = key_errors.get(key, 0) + 1
        rates = {}
        for key in key_total:
            total = key_total[key]
            errors = key_errors.get(key, 0)
            rates[key] = round((errors / total) * 100, 1)
        return rates

    @staticmethod
    def calculate_net_wpm(correct_chars: int, errors: int, elapsed_seconds: float) -> float:
        if elapsed_seconds <= 0:
            return 0.0
        net = correct_chars - errors
        if net < 0:
            net = 0
        return (net / 5.0) / (elapsed_seconds / 60.0)

    @staticmethod
    def calculate_all(correct_chars: int, total_typed: int,
                      errors: int, elapsed_seconds: float,
                      statuses: list[CharStatus], target: str) -> dict:
        return {
            "wpm": round(StatsCalculator.calculate_wpm(correct_chars, elapsed_seconds), 1),
            "cpm": round(StatsCalculator.calculate_cpm(correct_chars, elapsed_seconds), 1),
            "net_wpm": round(StatsCalculator.calculate_net_wpm(correct_chars, errors, elapsed_seconds), 1),
            "accuracy": round(StatsCalculator.calculate_accuracy(correct_chars, total_typed), 1),
            "errors": errors,
            "correct": correct_chars,
            "total_typed": total_typed,
            "consistency": round(StatsCalculator.calculate_consistency(statuses), 1),
            "error_rates_per_key": StatsCalculator.calculate_error_rate_per_key(statuses, target),
        }
