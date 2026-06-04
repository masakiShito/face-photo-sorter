from pathlib import Path

from app.config import SUPPORTED_EXTENSIONS


def find_photo_files(input_dir: Path) -> list[Path]:
    """Return supported image files under input_dir recursively."""
    if not input_dir.exists() or not input_dir.is_dir():
        raise FileNotFoundError(f"写真フォルダが見つかりません: {input_dir}")

    photos = [
        path
        for path in input_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    return sorted(photos)
