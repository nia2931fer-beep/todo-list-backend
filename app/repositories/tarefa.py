"""Aceso aos dados de tarefas."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from app.models import Tarefa
from app.models.enums import PrioridadeTarefa, StatusTarefa
from app.repositories.base import RepositorioBase

@dataclass(frozen=True)

class FiltroDeTarefa:
    """Critérios de um aconsulta de tarefas.
    
    Existe para que a assinatura de `TarefaRepositori.listar` não cresça até
    oito parâmentro posicionais, e para que acrescente um filtro novo não 
    mude a assinatura de quem já a chama.
    """
    usuario_id: int
    status: StatusTarefa | None = None
    prioridades: PrioridadeTarefa | None = None
    prazo_ate: date | None = None
    busca: str | None = None

class TarefaRepositorio(RepositorioBase[Tarefa]):
    """Acesso aos dados da tarefa."""

    @property
    def modelo(self) -> type[Tarefa]:
        return Tarefa
    
    def listar(self, filtro: FiltroDeTarefa) -> list[Tarefa]:
        """Listar as tarefas de um usuário, das mais recentes para as mais antigas.
        
        O filtro pelo dono vai na consulta - no `WHERE` -, e não num `if` depois
        de bucar tudo: o banco devolve só o que é do usuário.
        """
        consulta = self._sessao.query(Tarefa).filter(
            Tarefa.usuario_id == filtro.usuario_id
        )
        if filtro.status is not None:
            consulta = consulta.filter(Tarefa.status == filtro.status.value)
        if filtro.prioridades is not None:
            consulta = consulta.filter(
                Tarefa.prioridade == filtro.prioridades.value
            )
        if filtro.prazo_ate is not None:
                consulta = consulta.filter(
                Tarefa.prazo.isnot(None), Tarefa.prazo <= filtro.prazo_ate
            )
        if filtro.busca:
                consulta = consulta.filter(
                Tarefa.titulo.icontains(filtro.busca, autoescape=True)
            )
        return consulta.order_by(Tarefa.criado_em.desc(), Tarefa.id.desc()).all()