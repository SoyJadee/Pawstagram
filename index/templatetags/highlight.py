from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape
import re

register = template.Library()

@register.filter
def highlight(text, query):
    """
    Resalta todas las ocurrencias de cada palabra en `query` dentro de `text`.
    - Soporta múltiples palabras separadas por espacios.
    - Evita romper HTML: no modifica el contenido de las etiquetas.
    - Devuelve HTML seguro (marca el resultado como safe).
    """
    if not text or not query:
        return text

    # Palabras únicas y no vacías
    words = [w for w in re.split(r"\s+", str(query).strip()) if w]
    if not words:
        return text

    # Construir patrón (escapado) para todas las palabras
    pattern = "|".join(re.escape(w) for w in words)
    regex = re.compile(rf"({pattern})", re.IGNORECASE)

    def _highlight_segment(segment: str) -> str:
        # Escapar el texto para evitar inyección HTML y luego insertar spans/marks
        escaped = escape(segment)
        return regex.sub(r'<mark class="highlight">\1</mark>', escaped)

    source = str(text)
    if "<" in source and ">" in source:
        # Partir por etiquetas HTML y aplicar resaltado solo en el texto plano
        parts = re.split(r"(<[^>]+>)", source)
        result = []
        for part in parts:
            if part.startswith("<") and part.endswith(">"):
                # Dejar etiquetas tal cual
                result.append(part)
            else:
                result.append(_highlight_segment(part))
        return mark_safe("".join(result))
    else:
        # Texto plano
        return mark_safe(_highlight_segment(source))
