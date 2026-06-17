from typing_trainer.storage.database import get_engine


class TestDatabase:
    def test_engine_singleton(self):
        e1 = get_engine()
        e2 = get_engine()
        assert e1 is e2

    def test_engine_url(self):
        engine = get_engine()
        assert engine.url.drivername == "sqlite"
        assert "typing_trainer.db" in str(engine.url)
