"""Aceso aos dados de tarefas."""
from __future__ import annotations
from app.models import Tarefa
from app.repositories.base import RepositorioBase

class TarefaRepositorio(RepositorioBase[Tarefa]):
    """Acesso aos dados da tarefa."""

    @property
    def modelo(self) -> type[Tarefa]:
        return Tarefa