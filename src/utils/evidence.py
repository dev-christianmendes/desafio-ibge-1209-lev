from pathlib import Path

from src.config import settings


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_screenshot(
    page,
    filename: str,
    directory: Path = settings.EVIDENCIAS_DIR,
) -> Path:
    ensure_dir(directory)
    path = directory / filename
    page.screenshot(path=str(path), full_page=True)
    return path
