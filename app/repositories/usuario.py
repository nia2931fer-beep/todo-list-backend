"""Acesso aos dados de usuário."""
 
from __future__ import annotations
 
from app.models import Usuario
from app.repositories.base import RepositorioBase
 
 
class UsuarioRepositorio(RepositorioBase[Usuario]):
    """Acesso aos dados de usuário."""
 
    @property
    def modelo(self) -> type[Usuario]:
        # Cumpre o contrato da classe base: diz qual modelo este repositório usa.
        return Usuario
 
    def buscar_por_email(self, email: str) -> Usuario | None:
        """Busca pelo e-mail, normalizado como o modelo normaliza ao gravar.
 
        Sem a normalização, um cadastro feito com `"Ana@Exemplo.com"` não seria
        encontrado por uma busca com `"ana@exemplo.com"`.
        """
        return (
            self._sessao.query(Usuario)
            .filter(Usuario.email == Usuario.normalizar_email(email))
            .first()  # primeiro resultado, ou None se não achar
        )
    
    def email_existente(self, email: str) -> bool:
        """Informa se já há usuário cadastrado com este e-mail (RN-01)."""
        return self.buscar_por_email(email) is not None