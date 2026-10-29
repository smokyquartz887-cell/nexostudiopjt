"""Validação de uploads de imagem por tamanho, formato e assinatura do conteúdo."""
from django import forms

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP", "GIF"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


def validate_image_upload(upload, *, max_size, label="imagem"):
    if not upload:
        return upload
    # Em edição, o ModelForm pode fornecer um FieldFile já salvo, não um novo upload.
    # Esse arquivo não precisa ser validado novamente como entrada recebida.
    if not hasattr(upload, "content_type"):
        return upload
    if upload.size > max_size:
        raise forms.ValidationError(f"O arquivo de {label} excede o limite permitido.")
    if getattr(upload, "content_type", "") not in ALLOWED_MIME_TYPES:
        raise forms.ValidationError("Formato não permitido. Envie JPG, PNG, WEBP ou GIF; SVG não é aceito por segurança.")
    try:
        from PIL import Image, UnidentifiedImageError
        upload.seek(0)
        image = Image.open(upload)
        if image.format not in ALLOWED_FORMATS:
            raise forms.ValidationError("O conteúdo do arquivo não corresponde a um formato de imagem permitido.")
        image.verify()
        upload.seek(0)
    except forms.ValidationError:
        upload.seek(0)
        raise
    except Exception as exc:
        upload.seek(0)
        raise forms.ValidationError("O arquivo não parece ser uma imagem válida.") from exc
    return upload
