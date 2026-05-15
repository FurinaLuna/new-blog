import re
import os


def strip_html_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def sanitize_filename(filename: str) -> str:
    basename = os.path.basename(filename)
    cleaned = re.sub(r"[^\w.\-]", "_", basename)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    if not cleaned or cleaned.startswith("."):
        cleaned = f"file_{cleaned}"
    return cleaned


def validate_slug(slug: str) -> str:
    if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug):
        raise ValueError("slug格式无效，只允许小写字母、数字和连字符")
    return slug


def truncate_text(text: str, max_length: int) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length]
