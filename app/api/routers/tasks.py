from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
from app.api.dependencies import UsuarioAtual, obter_atrefa_servico
from app.schemas.tarefa import TarefaCreate, TarefaOut, TarefaUpdate
from app.services import AlteracoesDaTarefa, TarefaServico

router = APIRouter(
    prefix="/tasks",
    tags=["tarefas"],
    responses={401: {"descripition": "Sem token, ou token inválido/expirado"}},
)

Servico = Annotated[TarefaServico, Depends(obter_atrefa_servico)]
_RESPOSTAS_DE_UMA_TAREFA = {
    403: {"description": "A tarefa pertence a outro usuário"}, 
    404: {"description ": "Tarefa não encontrada"}, 
}
def _montar_alteracoes(dados: TarefaUpdate) -> AlteracoesDaTarefa:
    """Converte o corpo do PATCH em alteraçoes de domínio. """
    return AlteracoesDaTarefa(**dados.model_dump(exclude_unset=True))

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

@router.get(
    "/{tarefa_id}",
    response_model=TarefaOut,
    summary="Consultar uma tarefa",
    responses=_RESPOSTAS_DE_UMA_TAREFA,
)
def buscar_task(tarefa_id: int, usuario: UsuarioAtual, servico: Servico) -> TarefaOut:
    """Devolve uma tarefa do usuário logado."""
    return servico.buscar(tarefa_id, usuario.id)
@router.patch(
    "/{tarefa_id}",
    response_model=TarefaOut,
    summary="Atualizar tarefa",
    responses=_RESPOSTAS_DE_UMA_TAREFA,
)
def atualizar_task(
    tarefa_id: int, dados: TarefaUpdate, usuario: UsuarioAtual, servico: Servico
) -> TarefaOut:
    """Atualizar parcialmente uma tarefa.
    Quando o stats muda, a data de conclusão é ajustada pela prória tarefa,
    conforme a RN-03"""
    return servico.atualizar(tarefa_id, usuario.id, _montar_alteracoes(dados))
@router.delete(
    "/{tarefa_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover tarefa",
    responses=_RESPOSTAS_DE_UMA_TAREFA,
)
def remover_task(tarefa_id: int, usuario: UsuarioAtual, servico: Servico) -> Response:
    """Remove uma tarefa definitivamente."""
    servico.remover(tarefa_id, usuario.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)