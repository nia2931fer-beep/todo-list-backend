from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Any
from app.core.exceptions import AcessoNaoEncontrado, TarefaNaoEncontrada
from app.models import Tarefa
from app.models.enums import PrioridadeTarefa, StatusTarefa
from app.repositories import FiltroDeTarefa, TarefaRepositorio

NAO_INFORMADO: Any = object()
@dataclass(frozen=True)
class AlteracoesDaTarefa:
    """Campos que um PATCH pediu para alterar."""
    titulo: Any = NAO_INFORMADO
    status: Any = NAO_INFORMADO
    prioridade: Any = NAO_INFORMADO
    prazo: Any = NAO_INFORMADO
    
    def informado(self, campo: str) -> bool:
        """Informa se o cliente enviou este campo."""
        return getattr(self, campo) is not NAO_INFORMADO
    
class TarefaServico:
    """Operações sobre as tarefas do usuário autenticado.
    """
    def __init__(self, tarefa: TarefaRepositorio) -> None:
        self._tarefa = tarefa
    def criar(
            self,
        usuario_id: int,
        titulo: str,
        prioridade: PrioridadeTarefa,
        prazo: date | None,
    ) -> Tarefa:
        """Criar uma tarefa para o usuário autenticado.
        """
        tarefa = Tarefa(
            usuario_id=usuario_id,
            titulo=titulo,
            prioridade=prioridade,
            prazo=prazo,
        )
        return self._tarefa.salvar(tarefa)
    
    def listar(self, filtro: FiltroDeTarefa) -> list[Tarefa]:
        """Lista as tarefas do usuário autenticado."""
        return self._tarefa.listar(filtro)
    
    def buscar(self, tarefa_id: int, usuario_id: int) -> Tarefa:
        """Devolve uma tarefa do usuário.         """
        tarefa = self._tarefa.buscar_por_id(tarefa_id)
        if tarefa is None:
            raise TarefaNaoEncontrada()
        if not tarefa.pertence_a(usuario_id):
            raise AcessoNaoEncontrado()
        return tarefa
    
    def atualizar(
            self, tarefa_id: int, usuario_id: int, alteracoes: AlteracoesDaTarefa
    ) -> Tarefa:
        """Aplica as alterações informadas e devolve a tarefa atualizada. """
        tarefa = self .buscar(tarefa_id, usuario_id)
        if alteracoes.informado("titulo"):
            tarefa.titulo = alteracoes.titulo
        if alteracoes.informado("prioridade"):
            tarefa.prioridade = alteracoes.prioridade
        if alteracoes.informado("prazo"):
            tarefa.prazo = alteracoes.prazo
        if alteracoes.informado("status"):
            tarefa.definir_status(StatusTarefa(alteracoes.status))
        return self._tarefa.salvar(tarefa)
    def remover(self, tarefa_id: int, usuario_id: int) -> None:
        """Remover a tarefa definitivamente."""
        self._tarefa.remover(self.buscar(tarefa_id, usuario_id))