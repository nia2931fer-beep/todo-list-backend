from typing import Annotated
from fastapi import APIRouter, Depends, status
from app.api.dependencies import UsuarioAtual, obter_atrefa_servico
from app.schemas.tarefa import TarefaCreate, TarefaOut
from app.services import TarefaServico

router = APIRouter(
    prefix="/tasks",
    tags=["tarefas"],
    responses={401: {"descripition": "Sem token, ou token inválido/expirado"}},
)

Servico = Annotated[TarefaServico, Depends(obter_atrefa_servico)]

@router.post(
    "",
    response_model=TarefaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Criar tarefa",
)
def criar_task(dados: TarefaCreate, usuario: UsuarioAtual, servico: Servico) -> TarefaOut:
    return servico.criar(
        usuario_id=usuario.id,
        titulo=dados.titulo,
        prioridade=dados.prioridade,
        prazo=dados.prazo,
    )