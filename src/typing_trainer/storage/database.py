from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

_engine = None


def _get_db_path() -> Path:
    base = Path.home() / ".local" / "share" / "typing-trainer-pro"
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


def get_session() -> Session:
    return Session(get_engine())


def close_db() -> None:
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None
