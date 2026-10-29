"""Controles complementares para endpoints públicos."""
from django.core.cache import cache
from django.http import JsonResponse

CHAT_LIMIT = 30
CHAT_WINDOW_SECONDS = 60


def client_ip(request):
    """Usa REMOTE_ADDR; não confia cegamente em X-Forwarded-For enviado pelo cliente."""
    return request.META.get("REMOTE_ADDR", "unknown")[:64]


def enforce_rate_limit(request, *, scope="chat", limit=CHAT_LIMIT, window=CHAT_WINDOW_SECONDS):
    """Limitação simples por IP e janela fixa, via cache configurado no Django.

    Em produção, configure um cache compartilhado e um rate limiter de borda/WAF.
    """
    key = f"security:rate:{scope}:{client_ip(request)}"
    try:
        count = cache.get(key)
        if count is None:
            cache.add(key, 1, timeout=window)
            count = cache.get(key, 1)
        else:
            count = cache.incr(key)
    except (ValueError, TypeError):
        cache.set(key, 1, timeout=window)
        count = 1
    if count > limit:
        response = JsonResponse({"erro": "Limite de requisições excedido. Aguarde um minuto e tente novamente."}, status=429)
        response["Retry-After"] = str(window)
        return response
    return None
