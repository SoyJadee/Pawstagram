import re
from typing import Tuple, Dict, Any

try:
    from PIL import Image
except Exception:
    Image = None  # Pillow may not be available in some contexts

_danger_patterns = [
    re.compile(r"<\s*script.*?>.*?<\s*/\s*script\s*>",
               re.IGNORECASE | re.DOTALL),
    re.compile(r"on\w+\s*=\s*['\"]?[^'\"]+['\"]?", re.IGNORECASE),
    re.compile(r"javascript:\s*", re.IGNORECASE),
    re.compile(r"<\s*/?\s*iframe.*?>", re.IGNORECASE),
]


def sanitize_string(value: str, max_len=800) -> str:
    if not isinstance(value, str):
        return value
    cleaned = value
    for p in _danger_patterns:
        cleaned = p.sub(" ", cleaned)
    cleaned = cleaned.replace('<', '').replace('>', '')
    if len(cleaned) > max_len:
        cleaned = cleaned[:max_len]
    return cleaned.strip()


# Centralized image upload security settings
ALLOWED_IMAGE_CONTENT_TYPES = [
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/gif",
]

_FORMAT_TO_MIME = {
    "JPEG": "image/jpeg",
    "JPG": "image/jpeg",
    "PNG": "image/png",
    "WEBP": "image/webp",
    "GIF": "image/gif",
}

_FORMAT_TO_EXT = {
    "JPEG": ".jpg",
    "JPG": ".jpg",
    "PNG": ".png",
    "WEBP": ".webp",
    "GIF": ".gif",
}


def normalize_image_name(original_name: str, detected_format: str | None) -> str:
    """Return a filename with an extension that matches the detected image format.

    If detection fails, returns the original name.
    """
    if not detected_format:
        return original_name
    base = original_name.rsplit('.', 1)[0]
    ext = _FORMAT_TO_EXT.get(detected_format.upper())
    if not ext:
        return original_name
    # Keep base only alnum and safe chars
    safe_base = re.sub(r"[^A-Za-z0-9_\-]", "_", base) or "image"
    return f"{safe_base}{ext}"


def validate_uploaded_image(
    uploaded_file,
    *,
    max_bytes: int = 5 * 1024 * 1024,
    max_width: int = 8000,
    max_height: int = 8000,
    max_total_pixels: int = 20_000_000,
    allowed_content_types: list[str] | None = None,
) -> Tuple[bool, Dict[str, Any] | str]:
    """
    Validate an uploaded image using Pillow to prevent malicious files and huge images.

    Returns (True, info) on success where info includes: {format, width, height, mime}
    Returns (False, error_code) on failure. error_code in:
      - 'file_missing' | 'file_too_large' | 'invalid_type' | 'invalid_image'
      - 'image_too_large_dimensions' | 'image_too_many_pixels'
    """
    if uploaded_file is None:
        return False, "file_missing"

    # Size check first
    try:
        size = getattr(uploaded_file, "size", None)
        if size is not None and size > max_bytes:
            return False, "file_too_large"
    except Exception:
        # If size can't be determined, continue and rely on Pillow/open checks
        pass

    # Content-type quick check
    allowed = allowed_content_types or ALLOWED_IMAGE_CONTENT_TYPES
    ctype = getattr(uploaded_file, "content_type", None)
    if ctype and allowed and ctype not in allowed:
        return False, "invalid_type"

    # Deep validation with Pillow
    if Image is None:
        # Best-effort without Pillow
        return True, {"format": None, "width": None, "height": None, "mime": ctype}

    try:
        pos = None
        try:
            pos = uploaded_file.tell()
        except Exception:
            pos = None

        img = Image.open(uploaded_file)
        img.verify()  # Detects truncated/corrupt files and non-images

        # Need to reopen after verify to access size
        if pos is not None:
            uploaded_file.seek(pos)
        else:
            try:
                uploaded_file.seek(0)
            except Exception:
                pass
        img = Image.open(uploaded_file)
        width, height = img.size
        fmt = (img.format or "").upper() if hasattr(img, "format") else None

        if width > max_width or height > max_height:
            return False, "image_too_large_dimensions"
        if width * height > max_total_pixels:
            return False, "image_too_many_pixels"

        # Derive a canonical mime from detected format if possible
        mime = _FORMAT_TO_MIME.get(fmt, ctype)

        # Reset for subsequent consumers (e.g., storage upload)
        try:
            uploaded_file.seek(0)
        except Exception:
            pass

        return True, {"format": fmt, "width": width, "height": height, "mime": mime}
    except Exception:
        try:
            uploaded_file.seek(0)
        except Exception:
            pass
        return False, "invalid_image"
