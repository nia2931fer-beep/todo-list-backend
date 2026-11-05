"""Provedores de dependência: montam os objetos que as rotas usam.
 
Concentrar a montagem aqui tem um efeito prático: a rota declara que precisa
de um `UsuarioServico` e não sabe quantas peças existem por trás dele. Se
amanhã o serviço passar a receber um colaborador novo, muda este módulo — e
nenhuma rota.
"""

from typing import Annotated
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.core.config import obter_configuracao
from app.core.exceptions import NaoAutenticado
from app.core.security import HashBcrypt, HashDeSenha, TokenJWT
from app.db.database import obter_sessao
from app.models import usuario
from app.repositories import UsuarioRepositorio
from app.services import UsuarioServico
 
_esquema_bearer = HTTPBearer(auto_error=False, description="Token recebido no login")
 
def obter_hasher() -> HashDeSenha:
    """Implementação de hash usada pela aplicação.
 
    Declarada como dependência — e não instanciada direto no serviço — para
    poder ser substituída nos testes por uma implementação instantânea.
    """
    return HashBcrypt()

def obter_tokens() -> TokenJWT:
    """Emissor/leitor de tokens, com o segredo e a validadeda configuração."""
    config = obter_configuracao()
    return TokenJWT(config.segredo_jwt(), config.jwt_expira_minutos)
 
def obter_usuario_servico(
    sessao: Session = Depends(obter_sessao),     # o FastAPI chama obter_sessao antes
    hasher: HashDeSenha = Depends(obter_hasher),  # e obter_hasher, e entrega os dois aqui
    tokens: TokenJWT = Depends(obter_tokens)
) -> UsuarioServico:
    """Serviço de usuários, com repositório e hasher já injetados."""
    # Monta as peças, uma dentro da outra.
    return UsuarioServico(UsuarioRepositorio(sessao), hasher, tokens)

def obter_usuario_atual(
        credenciais: Annotated[
            HTTPAuthorizationCredentials | None, Depends(_esquema_bearer)
        ],
        servico: Annotated[UsuarioServico, Depends(obter_usuario_servico)],
) -> Usuario:
    """Identifica quem está fazendo a requisição, a partir do token."""
    if credenciais is None:
        raise NaoAutenticado()
    return servico.usuario_do_token(credenciais.credentials)
UsuarioAtual = Annotated[Usuario, Depends(obter_usuario_atual)]