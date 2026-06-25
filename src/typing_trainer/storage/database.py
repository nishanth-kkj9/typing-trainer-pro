from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine, select

from typing_trainer.storage.models import User

_engine = None


def _get_db_path() -> Path:
    base = Path.home() / ".local" / "typing-trainer-pro"
    base.mkdir(parents=True, exist_ok=True)
    return base / "typing_trainer.db"


def get_engine():
    global _engine
    if _engine is None:
        db_path = _get_db_path()
        _engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            echo=False,
        )
    return _engine


def init_db() -> None:
    SQLModel.metadata.create_all(get_engine())
    _ensure_default_user()


def _ensure_default_user() -> None:
    """Create a default user if none exists."""
    with Session(get_engine()) as session:
        existing = session.exec(select(User).limit(1)).first()
        if not existing:
            default_user = User(name="Default User")
            session.add(default_user)
            session.commit()
            session.refresh(default_user)


def get_default_user_id() -> int | None:
    """Get the ID of the default user."""
    with Session(get_engine()) as session:
        user = session.exec(select(User).limit(1)).first()
        return user.id if user else None


def get_session() -> Session:
    return Session(get_engine())


def close_db() -> None:
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None
