"""Infraestrutura de banco: engine, fabrica de sessão e a classe Base do ORM."""
from __future__ import annotations
from collections.abc import Generator
from typing import Any
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.config import obter_configuracao
def _opcoes_do_engine(url: str) -> dict[str, Any]:
    """O SQLALchemy precisa de opções diferentes para SQLite e PostgreSQL.
    """
    if url.startswith("sqlite"):
        return {
            "connect_args": {"check_same_thread": False},
        }
    return {"pool_pre_ping": True}
_url = obter_configuracao().url_banco
engine = create_engine(_url, echo=False, **_opcoes_do_engine(_url))
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()
def criar_tabelas() -> None:
    """Criar as tabelas do banco de dados, caso não existam.
    """
    from app import models   #noqa: F401 (registra os modelos no metadata)
    Base.metadata.create_all(bind=engine)
def obter_sessao() -> Generator[Session, None, None]:
    """Fornece uma sessão de banco de dados para uso em contexto `with`ou como dependência do FastAPI.
    """
    sessao = SessionLocal()
    try:
        yield sessao
    finally:
        sessao.close()