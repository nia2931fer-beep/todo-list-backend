"""SEurança: funções de hash de senha e verificação de hash.
"""

from __future__ import annotations
from abc import ABC, abstractclassmethod
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from app.core.exceptions import TokensInvalidos
#  O bcrypt só considera os primeirs 72 BYTES a senha (e a versão 5 recusa
# senhas maiores). EM UTF-8 um caractere acentuado acupa 2 bytes, então o limite 
# é conferido em bytes, não em caracteres = ver `shemas.usuarioCreate`.
LIMITE_BYTES_SENHA = 72

class HashDeSenha(ABC):
    """Contrato de implementação de hash de senha. A aplicação só usa a interface, não
    """
    @abstractclassmethod
    def gerar(self, senha: str) -> str:
        """Devolve o hash da senha informada."""
    @abstractclassmethod
    def verificar(self, senha:str, hash_armazenado: str) -> bool:
        "Confere se a senha correstonde ao hash gravado."
class HashBcrypt(HashDeSenha):
    """Implementação de hash de senha usando o algoritimo bcrypt.
    """
    def gerar(self, senha: str) -> str:
        return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("ascii")
    def verificar(self, senha:str, hash_armazenado: str) -> bool:
        senha_bytes = senha.encode("utf-8")
        if len(senha_bytes) > LIMITE_BYTES_SENHA:
            # Nenhuma senha cadastrada passa desse tamanho; responder "não confere"
            # é mais seguro do que deixar o bcrypt lançar um erro inesperado.
            return False
        return bcrypt.checkpw(senha_bytes, hash_armazenado.encode("ascii"))
@dataclass(frozen=True)
class TokensEmitido:
    """Um token de acesso recém-criado e o momento em que deixa de valer."""
    valor: str
    expira_em: datetime

class TokenJWT:
    """Emite e confere tokens JWT assinados com HS256.
    """
    ALGORITIMO = "HS256"
    def __init__(self, segredo : str, expira_minuto: int) -> None:
        self._segredo = segredo
        self._validade = timedelta(minutes=expira_minuto)
    def emitir(self, usuário_id: int, agora: datetime | None = None) -> TokensEmitido:
        """Criar um token válido pelo tempo configurado."""
        expira_em = (agora or datetime.now(timezone.utc)) + self._validade
        conteudo = {"sub": str(usuário_id), "exp": expira_em}
        valor = jwt.encode(conteudo, self._segredo, algorithm=self.ALGORITIMO)
        return TokensEmitido(valor=valor, expira_em=expira_em)
    def ler(self, tokn: str) -> int:
        """Confere assinatura e validade e devolve o id do usuário.
        Raises:
            TokensInvalido: token expirado, adulterado ou malformado.
            """
        try:
            conteudo = jwt.decode(
                token,
                self._segredo,
                algorithms=[self.ALGORITIMO],
                options={"require": ["sub", "exp"]},
            )
            return int(conteudo["sub"])
        except jwt.ExpiredSignatureError as erro:
            raise TokensInvalidos("Sessão expirada. Entre novamente.") from erro
        except (jwt.InvalidTokenError, ValueError) as erro:
            raise TokensInvalidos() from erro