import shutil
from pathlib import Path

from app.config import MATCHED_DIR_NAME, UNKNOWN_DIR_NAME, UNMATCHED_DIR_NAME
from app.models.scan_result import ScanStatus


def prepare_output_dirs(output_dir: Path) -> dict[ScanStatus, Path]:
    dirs: dict[ScanStatus, Path] = {
        "matched": output_dir / MATCHED_DIR_NAME,
        "unmatched": output_dir / UNMATCHED_DIR_NAME,
        "unknown": output_dir / UNKNOWN_DIR_NAME,
    }

    for directory in dirs.values():
        directory.mkdir(parents=True, exist_ok=True)

    return dirs


def get_unique_destination_path(destination_dir: Path, source_path: Path) -> Path:
    candidate = destination_dir / source_path.name
    if not candidate.exists():
        return candidate

    stem = source_path.stem
    suffix = source_path.suffix
    counter = 1

    while True:
        candidate = destination_dir / f"{stem}_{counter:03d}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def copy_photo(source_path: Path, destination_dir: Path) -> Path:
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination_path = get_unique_destination_path(destination_dir, source_path)
    shutil.copy2(source_path, destination_path)
    return destination_path
