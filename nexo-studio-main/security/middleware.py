"""Cabeçalhos defensivos complementares para respostas HTTP."""
class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not response.has_header("X-Content-Type-Options"):
            response["X-Content-Type-Options"] = "nosniff"
        if not response.has_header("Referrer-Policy"):
            response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if not response.has_header("Permissions-Policy"):
            response["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        # CSP estrita exige retirar scripts inline existentes; por ora, não impor uma
        # política que quebre a interface. A documentação descreve a evolução necessária.
        return response
