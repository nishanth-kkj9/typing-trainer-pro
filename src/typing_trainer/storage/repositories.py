
from sqlmodel import select

from typing_trainer.storage.database import get_session
from typing_trainer.storage.models import KeyStat, TrainingSession, User


class UserRepository:
    def create(self, name: str) -> User:
        with get_session() as session:
            user = User(name=name)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def get(self, user_id: int) -> User | None:
        with get_session() as session:
            return session.get(User, user_id)

    def get_all(self) -> list[User]:
        with get_session() as session:
            return list(session.exec(select(User)).all())

    def delete(self, user_id: int) -> bool:
        with get_session() as session:
            user = session.get(User, user_id)
            if user:
                session.delete(user)
                session.commit()
                return True
            return False


class TrainingSessionRepository:
    def create(self, session_data: TrainingSession) -> TrainingSession:
        with get_session() as session:
            session.add(session_data)
            session.commit()
            session.refresh(session_data)
            return session_data

    def get_by_user(self, user_id: int, limit: int = 20) -> list[TrainingSession]:
        with get_session() as session:
            stmt = (
                select(TrainingSession)
                .where(TrainingSession.user_id == user_id)
                .order_by(TrainingSession.started_at.desc())
                .limit(limit)
            )
            return list(session.exec(stmt).all())

    def get_best_wpm(self, user_id: int) -> float:
        with get_session() as session:
            stmt = (
                select(TrainingSession.wpm)
                .where(TrainingSession.user_id == user_id)
                .order_by(TrainingSession.wpm.desc())
                .limit(1)
            )
            result = session.exec(stmt).first()
            return result or 0.0

    def get_total_xp(self, user_id: int) -> int:
        with get_session() as session:
            stmt = select(TrainingSession.xp_earned).where(
                TrainingSession.user_id == user_id
            )
            return sum(session.exec(stmt).all())


class KeyStatRepository:
    def bulk_create(self, stats: list[KeyStat]) -> None:
        with get_session() as session:
            for stat in stats:
                session.add(stat)
            session.commit()

    def get_weak_keys(self, user_id: int, limit: int = 5) -> list[KeyStat]:
        with get_session() as session:
            stmt = (
                select(KeyStat)
                .join(TrainingSession)
                .where(TrainingSession.user_id == user_id)
                .order_by(KeyStat.error_count.desc())
                .limit(limit)
            )
            return list(session.exec(stmt).all())
