from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
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

@router.get(
    "",
    response_model=list[TarefaOut],
    summary="Listar as tarefas do usuário",
)
def listar_task(usuario: UsuarioAtual, servico: Servico, response: Response) -> list[TarefaOut]:
    """Listar as tarefas do usuário logado, das mais recentes para as mais antigas.
    """
    tarefas = servico.listar(usuario.id)
    response.headers["x-Total-Count"] = str(len(tarefas))
    return tarefas