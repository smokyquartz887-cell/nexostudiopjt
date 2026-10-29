"""Validações reutilizáveis para dados recebidos pela aplicação."""
import json
from django.core.exceptions import ValidationError

MAX_JSON_BODY_BYTES = 8 * 1024
MAX_CHAT_QUESTION_LENGTH = 500


def parse_json_object(raw_body):
    """Decodifica JSON limitado e exige um objeto/dicionário na raiz."""
    if len(raw_body) > MAX_JSON_BODY_BYTES:
        raise ValidationError("O corpo da requisição excede o limite permitido.")
    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValidationError("JSON inválido.") from exc
    if not isinstance(payload, dict):
        raise ValidationError("O JSON deve ser um objeto com campos nomeados.")
    return payload


def clean_chat_question(value):
    """Valida a pergunta sem truncar silenciosamente a entrada do usuário."""
    if not isinstance(value, str):
        raise ValidationError("O campo pergunta deve ser texto.")
    question = value.strip()
    if len(question) < 2:
        raise ValidationError("Digite uma pergunta com pelo menos 2 caracteres.")
    if len(question) > MAX_CHAT_QUESTION_LENGTH:
        raise ValidationError("A pergunta deve ter no máximo 500 caracteres.")
    if any(ord(char) < 32 and char not in "\t\n\r" for char in question):
        raise ValidationError("A pergunta contém caracteres de controle inválidos.")
    return question
