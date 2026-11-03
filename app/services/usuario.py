"""Operações de cadastro de usuários."""
 
from __future__ import annotations
from dataclasses import dataclass
from app.core.exceptions import CredenciaisInvalidas, EmailJaCadastrado
from app.core.security import HashDeSenha, TokensEmitido, TokenJWT
from app.models import Usuario
from app.repositories import UsuarioRepositorio
 
@dataclass(frozen=True)
class Sessao:
    """Resultado de um login bem-sucedido: quem entrou e o token emitido."""
    usuario: Usuario
    token: TokensEmitido

class UsuarioServico:
    """Operações de cadastro de usuários."""
 
    def __init__(
            self,
            repositorio: UsuarioRepositorio,
            hasher: HashDeSenha,
            tokens: TokenJWT | None = None,
            ) -> None:
        # O serviço não cria as próprias peças: ele as recebe (injeção de dependência).
            self._repositorio = repositorio
            self._hasher = hasher
            self._tokens = tokens
 
    def cadastrar(self, nome: str, email: str, senha: str) -> Usuario:
        """Cadastra um usuário com a senha protegida por hash.
        
        Raises:
            EmailJaCadastrado: se o e-mail já estiver em uso (RN-01).
        """
        if self._repositorio.email_existente(email):
            raise EmailJaCadastrado()
        
        usuario = Usuario(nome=nome, email=email)           # 1) cria o usuário
        usuario.definir_senha(senha, self._hasher)  # RN-05  # 2) a senha vira hash
        return self._repositorio.salvar(usuario)            # 3) manda gravar
    def autenticar(self, email: str, senha: str) -> Usuario:
         """Confere as credenciais e devolve o usuário corretamente."""
         usuario = self._repositorio.buscar_por_email(email)
         if usuario is None or not usuario.senha_confere(senha, self._hasher):
              raise CredenciaisInvalidas()
         return usuario
    def entrar(self, email: str, senha: str) -> Sessao:
         """Autentica e emite o token de acesso."""
         usuario = self.autenticar(email, senha)
         return Sessao(usuario=usuario, token=self._exigir_tokens().emitir(usuario.id))
    
    def _exigir_tokens(self) -> TokenJWT:
         if self._tokens is None:
              raise RuntimeError("UsuarioServico foi montado sem emissor de tokens.")
         return self._tokens