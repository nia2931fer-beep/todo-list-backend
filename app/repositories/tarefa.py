"""Aceso aos dados de tarefas."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from sqlalchemy import case
from app.models import Tarefa
from app.models.enums import CampoOrdenacao, Ordem, PrioridadeTarefa, StatusTarefa
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
    ordenar_por: CampoOrdenacao = CampoOrdenacao.CRIADO_EM
    ordem: Ordem = Ordem.DESC
    limite: int = 100
    deslocamento: int = 0

@dataclass(frozen=True)
class PaginaDeTarefas:
     """Uma página de listagem e o yotal de tarefas que atendem ao filtro. """
     tarefas: list[Tarefa]
     total: int

class TarefaRepositorio(RepositorioBase[Tarefa]):
    """Acesso aos dados da tarefa."""
    _ORDEM_POR_PRIORIDADE = case(
         PrioridadeTarefa.mapa_de_pesos(), value=Tarefa.prioridade, else_=99
    )

    @property
    def modelo(self) -> type[Tarefa]:
        return Tarefa
    def _coluna_de_ordenacao(self, campo: CampoOrdenacao):
        """Devolve aexpreção SQL corresponde ao campo de orientação."""
        colunas = {
            CampoOrdenacao.CRIADO_EM: Tarefa.criado_em,
            CampoOrdenacao.PRAZO: Tarefa.prazo,
            CampoOrdenacao.PRIORIDADE: self._ORDEM_POR_PRIORIDADE,
         }
        return colunas[campo]
    
    def listar(self, filtro: FiltroDeTarefa) -> PaginaDeTarefas:
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
        total = consulta.order_by(None).count()

        coluna = self._coluna_de_ordenacao(filtro.ordenar_por)
        ordenacao = [coluna.desc() if filtro.ordem is Ordem.DESC else coluna.asc()]
        if filtro.ordenar_por is CampoOrdenacao.PRAZO:
             ordenacao.insert(0, case((Tarefa.prazo.is_(None), 1), else_=0))
        ordenacao.append(Tarefa.id.desc())

        tarefas = (
             consulta.order_by(*ordenacao)
             .offset(filtro.deslocamento)
             .limit(filtro.limite)
             .all()
        )
        return PaginaDeTarefas(tarefas=tarefas, total=total)