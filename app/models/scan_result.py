from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional

ScanStatus = Literal["matched", "unmatched", "unknown"]


@dataclass(frozen=True)
class ScanResult:
    source_path: Path
    status: ScanStatus
    copied_path: Optional[Path] = None
    best_distance: Optional[float] = None
    matched_sample: Optional[Path] = None
    error: Optional[str] = None

    @property
    def has_error(self) -> bool:
        return self.error is not None
