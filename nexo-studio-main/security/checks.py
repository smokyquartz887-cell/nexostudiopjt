"""Checks de configuração executados pelo sistema de verificações do Django."""
import os
from django.conf import settings
from django.core.checks import Error, Warning, register

@register()
def nexo_security_configuration(app_configs, **kwargs):
    issues = []
    if settings.DEBUG:
        issues.append(Warning("DEBUG está ativado; use DEBUG=False fora do desenvolvimento.", id="nexo_security.W001"))
    if settings.SECRET_KEY.startswith("dev-only-") or len(settings.SECRET_KEY) < 40:
        issue = Error if not settings.DEBUG else Warning
        issues.append(issue("SECRET_KEY ausente/fraca. Configure uma chave aleatória via variável de ambiente.", id="nexo_security.E001" if not settings.DEBUG else "nexo_security.W003"))
    if "*" in settings.ALLOWED_HOSTS:
        issues.append(Warning("ALLOWED_HOSTS permite qualquer host; restrinja em ambientes publicados.", id="nexo_security.W002"))
    if not settings.DEBUG and not os.environ.get("NEXO_ALLOWED_HOSTS"):
        issues.append(Error("Defina NEXO_ALLOWED_HOSTS no ambiente publicado.", id="nexo_security.E002"))
    return issues
