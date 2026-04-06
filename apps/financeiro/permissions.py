from rest_framework.permissions import BasePermission


class PodeVerResumoFinanceiroGlobal(BasePermission):
    """
    RF04 / finance_spec: colaborador não acessa o resumo financeiro global da empresa.
    """

    message = "Sem permissão para visualizar o resumo financeiro."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, "is_superuser", False):
            return True
        role = getattr(user, "role", None)
        return role in ("admin", "gestor")
