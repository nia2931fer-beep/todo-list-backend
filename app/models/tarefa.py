"""Entidade Tarefa: dados e regras de uma tarefa.
"""
from __future__ import annotations
from datetime import date, datetime
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, validates
from app.core.datas import agora_utc
from app.core.exceptions import TituloObrigatorio, ValorInvalido
from app.db.database import Base
from app.models.enums import PrioridadeTarefa, StatusTarefa

class Tarefa(Base):
    """Tarefa pertence a um usuário."""
    __tablename__ = "tarefas"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(
        Integer, ForeignKey("usuarios.id"), nullable=False, index=True
    )
    titulo = Column(String(200), nullable=False)

    _status = Column("status", String(20), nullable=False)
    prioridade = Column(String(20), nullable=False)
    prazo = Column(Date, nullable=True)
    criado_em = Column(DateTime(timezone=True), nullable=False, default=agora_utc)
    atualizado_em = Column(
        DateTime(timezone=True), nullable=False, default=agora_utc, onupdate=agora_utc
    )
    _concluido_em = Column("concluido_em", DateTime(timezone=True), nullable=True)
    usuario = relationship(
        "Usuario",
        back_populates="tarefas"
    )

    def __init__(
            self,
            *,
            usuario_id: int,
            titulo: str,
            prioridade: PrioridadeTarefa | str = PrioridadeTarefa.MEDIA,
            prazo: date | None = None, 
    ) -> None:
        """Criar uma tarefa sempre pendente e sem data de conclusão (RN-02).
        
        """
        self.usuario_id = usuario_id
        self.titulo = titulo
        self.prioridade = prioridade
        self.prazo = prazo
        self._status = StatusTarefa.PENDENTE.value
        self._concluido_em = None

    #---------------------------------------------------------------------
    @hybrid_property
    def status(self) -> StatusTarefa:
        """Status atual, como membo do enum. Somente leitura.
        """
        return StatusTarefa(self._status)
    @status.expression
    def status(cls): # noqa: N805 - assinatura exigida pelo SQLALchemy
        """Versão da propriedade usada dentro de consultar SQL."""
        return cls._status
    
    @property
    def concluido_em(self) -> datetime | None:
        """Momento da conclusão, ou `None` se a tarefa está pendente.
        Somente leitura: quem define este valor é a própria tarefa.
        """
        return self._concluido_em
    #------------------------------------------------------------------
    def concluir(self, agora: datetime | None = None) -> None:
        """Concluir a tarefa e registrar o momento. """
        if self.status is StatusTarefa.CONCLUIDA:
            return
        self._status = StatusTarefa.CONCLUIDA.value
        self._concluido_em = agora or agora_utc()

    def reabrir(self) -> None:
        """Devolve a tarefa para pendente e apaga a data de conclusão. """
        if self.status is StatusTarefa.PENDENTE:
            return
        self._status = StatusTarefa.PENDENTE.value
        self._concluido_em = None

    def definir_status(
            self, novo_status: StatusTarefa | str, agora: datetime | None = None
    ) -> None:
        """Aplica o status informado pela operaçao correspondente. """
        status = StatusTarefa(novo_status)
        if status is StatusTarefa.CONCLUIDA:
            self.concluir(agora)
        else:
            self.reabrir()

    def pertence_a(self, usuario_id: int) -> bool:
        """Informa se a tarefa é de um determinado usuário."""
        return self.usuario_id == usuario_id
    
    #----------------------------------------------------

    @validates("titulo")
    def _validar_titulo(self, _campo: str, valor: str) -> str:
        """Recusa título vazio, aqui e em qualquer ponto do programa."""
        if valor is None or not valor.strip():
            raise TituloObrigatorio()
        return valor.strip()

    
    @validates("prioridades")
    def _validar_prioridade(self, _campo: str, valor: object) -> str:
        """Aceita o enum ou o texto correspondente, e grava sempre o texto."""
        try:
            return PrioridadeTarefa(valor).value
        except ValueError as erro:
            permitidos = ", ".join(p.value for p in PrioridadeTarefa)
            raise ValorInvalido(
                f"Prioridade inválida. Valores aceitos: {permitidos}."
            ) from erro
    def __repr__(self) -> str:
        return (
            f"<Tarefas id={self.id} titulos={self.titulo!r}"
            f"status={self._status!r}>"
        )