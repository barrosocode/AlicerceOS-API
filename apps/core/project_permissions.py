from django.core.exceptions import ValidationError


def assert_usuario_pode_definir_status_ativo(usuario) -> None:
    """Apenas Admin ou Gestor (ou superusuário) podem colocar o projeto em Ativo (Módulo 2)."""
    if usuario is None or not getattr(usuario, "is_authenticated", False):
        raise ValidationError("Autenticação necessária para alterar o status do projeto.")
    if getattr(usuario, "is_superuser", False):
        return
    role = getattr(usuario, "role", None)
    if role not in ("admin", "gestor"):
        raise ValidationError("Apenas Admin ou Gestor podem alterar o status do projeto para Ativo.")
