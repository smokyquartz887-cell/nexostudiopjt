"""Registro mínimo de eventos de segurança sem gravar credenciais ou payloads completos."""
import logging

logger = logging.getLogger("nexo.security")


def log_security_event(event, *, request=None, outcome="blocked", detail=""):
    ip = "unknown"
    username = "anonymous"
    if request is not None:
        ip = request.META.get("REMOTE_ADDR", "unknown")[:64]
        user = getattr(request, "user", None)
        if getattr(user, "is_authenticated", False):
            username = str(user.get_username())[:150]
    logger.warning("security_event=%s outcome=%s user=%s ip=%s detail=%s", event, outcome, username, ip, str(detail)[:200])
