import re
from django import forms

class XSSCleanMixin:
    """Mixin reutilizable para sanitizar entradas de texto y mitigar XSS básico.
    - Elimina tags <script>, atributos on*, esquemas javascript: y algunas etiquetas embebidas.
    - Quita ángulos restantes para evitar markup residual.
    - Limita longitudes exageradas.
    """
    _danger_patterns = [
        re.compile(r"<\s*script.*?>.*?<\s*/\s*script\s*>", re.IGNORECASE | re.DOTALL),
        re.compile(r"on\w+\s*=\s*['\"]?[^'\"]+['\"]?", re.IGNORECASE),
        re.compile(r"javascript:\s*", re.IGNORECASE),
        re.compile(r"<\s*/?\s*iframe.*?>", re.IGNORECASE),
        re.compile(r"<\s*/?\s*img.*?>", re.IGNORECASE),
        re.compile(r"<\s*/?\s*object.*?>", re.IGNORECASE),
        re.compile(r"<\s*/?\s*embed.*?>", re.IGNORECASE),
        re.compile(r"<\s*/?\s*link.*?>", re.IGNORECASE),
        re.compile(r"<\s*/?\s*style.*?>.*?<\s*/\s*style\s*>", re.IGNORECASE | re.DOTALL),
    ]

    MAX_LEN = 800

    def _strip_xss(self, value: str):
        if not isinstance(value, str):
            return value
        cleaned = value
        for pat in self._danger_patterns:
            cleaned = pat.sub(" ", cleaned)
        if '<' in cleaned or '>' in cleaned:
            cleaned = cleaned.replace('<', '').replace('>', '')
        if len(cleaned) > self.MAX_LEN:
            cleaned = cleaned[: self.MAX_LEN]
        return cleaned.strip()

    def clean(self):
        data = super().clean()
        for k, v in list(data.items()):
            if isinstance(v, str):
                data[k] = self._strip_xss(v)
        return data
