from __future__ import annotations
from datetime import date
from app.models import Tarefa
from app.models.enums import PrioridadeTarefa
from app.repositories import TarefaRepositorio

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
    
    def listar(self, usuario_id: int) -> list[Tarefa]:
        """Lista as tarefas do usuário autenticado."""
        return self._tarefa.listar(usuario_id)