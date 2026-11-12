from datetime import date
from pydantic import Field
from app.models.enums import PrioridadeTarefa, StatusTarefa
from app.schemas.base import DataHoraUTC, EsquemaDeEntrada, EsquemaDeSaida

class TarefaCreate(EsquemaDeEntrada):
    """Dados recebidos"""

    titulo: str = Field(min_length=1, max_length=200)
    prioridade: PrioridadeTarefa = PrioridadeTarefa.MEDIA
    prazo: date | None = None

class TarefaUpdate(EsquemaDeEntrada):
    """Campos que podem ser alterados. Todos opcionais (Atualização parcial)."""

    titulo: str | None = Field(default=None, min_length=1, max_length=200)
    prioridade: PrioridadeTarefa | None = None
    prazo: date | None = None

class TarefaOut(EsquemaDeSaida):

    id: int
    usuario_id: int
    titulo: str
    status: StatusTarefa
    prioridade: PrioridadeTarefa
    prazo: date | None
    criado_em: DataHoraUTC
    atualizado_em: DataHoraUTC
    concluido_em: DataHoraUTC | None