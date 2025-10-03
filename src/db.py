from __future__ import annotations

import datetime
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.data_model import DeletableMixin
from src.settings import Settings


def _get_db_session(schema: str) -> Session:
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=create_engine(
            Settings.database.pg_dsn.unicode_string(),
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        ).execution_options(schema_translate_map={None: schema}),
    )()


def get_shared_db_session() -> Iterator[Session]:
    s = _get_db_session(schema=Settings.database.shared_schema)
    try:
        yield s
        s.commit()
    except:  # noqa
        s.rollback()
        raise
    finally:
        s.close()


@contextmanager
def new_db_session(schema: str) -> Iterator[Session]:
    s = _get_db_session(schema)
    try:
        yield s
        s.commit()
    except:  # noqa
        s.rollback()
        raise
    finally:
        s.close()


def tag_to_be_deleted(deletable: DeletableMixin) -> None:
    deletable.deleted_at = datetime.datetime.now()


def delete(deletable: DeletableMixin, session: Session) -> None:
    tag_to_be_deleted(deletable)
    session.add(deletable)
    session.commit()
