"""Endpoints de usuário: cadastro.
 
A rota traduz HTTP em uma chamada de serviço e devolve o resultado. Não há
consulta ao banco, `if` de regra de negócio nem `raise HTTPException`: os erros 
se negócio sobem como exceções de domínio e são convertidos  em código de status
por `main.py`.
"""
 
from typing import Annotated
from fastapi import APIRouter, Depends, status
from app.api.dependencies import obter_usuario_servico
from app.schemas.usuario import SessaoOut, UsuarioCreate, UsuarioLogin, UsuarioOut
from app.services import UsuarioServico
 
# Todas as rotas deste arquivo começam com /usuarios; a tag as agrupa no /docs.
router = APIRouter(prefix="/usuarios", tags=["Usuários"])
 
 
@router.post(
    "",
    response_model=UsuarioOut,               # filtra o que sai (a senha nunca aparece)
    status_code=status.HTTP_201_CREATED,     # 201 = "criado"
    summary="Cadastrar usuário",
    responses={409: {"description": "E-mail já cadastrado"}},
)
def cadastrar_usuario(
    dados: UsuarioCreate,  # o FastAPI lê e valida o JSON do corpo
    servico: Annotated[UsuarioServico, Depends(obter_usuario_servico)],  # serviço já montado
) -> UsuarioOut:
    """Cadastra um novo usuário com a senha armazenada como hash."""
    return servico.cadastrar(dados.nome, dados.email, dados.senha)
 
@router.post(
    "/login",
    response_model=SessaoOut,
    summary="Entrar (receber o token de acesso)",
    responses={401: {"description": "E-mail ou senha incorreta"}},
)
def entrar(
    dados: UsuarioLogin,
    servico:
    Annotated[UsuarioServico, Depends(obter_usuario_servico)],
) -> SessaoOut:
    """Confere e-mail e senha e devolve o token de acesso e o usuário.
    
    
    O token é a prova de identidade das próximas requisiçoes: guarde o 
    `accessToken` e envie-o no cabeçalho `Authorization: Bearer <AccessTokens>`.
    """
    sessao = servico.entrar(dados.email, dados.senha)
    return SessaoOut(
        access_tokens=sessao.token.valor,
        expira_em=sessao.token.expira_em,
        usuario=UsuarioOut.model_validate(sessao.usuario),
    )