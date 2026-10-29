"""Helpers de autorização para operações com recursos pertencentes a um negócio."""
from django.shortcuts import get_object_or_404


def get_business_or_404(*, user, business_id):
    """Retorna apenas um negócio pertencente ao usuário autenticado."""
    if not getattr(user, "is_authenticated", False):
        # Evita revelar se o identificador existe para usuários anônimos.
        from django.http import Http404
        raise Http404
    from studio.models import Business
    return get_object_or_404(Business, pk=business_id, owner=user)


def get_owned_object_or_404(queryset, *, business, object_id):
    """Busca um objeto dentro do negócio autorizado, prevenindo IDOR."""
    return get_object_or_404(queryset, pk=object_id, business=business)
