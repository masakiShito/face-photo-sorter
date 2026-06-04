from pathlib import Path

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_INPUT_DIR = BASE_DIR / "photos" / "input"
DEFAULT_TARGET_DIR = BASE_DIR / "photos" / "target"
DEFAULT_OUTPUT_DIR = BASE_DIR / "photos" / "output"
DEFAULT_DEEPFACE_HOME = BASE_DIR / "data" / "deepface"

DEFAULT_THRESHOLD = 0.4
DEFAULT_MODEL_NAME = "VGG-Face"
DEFAULT_DETECTOR_BACKEND = "opencv"

MATCHED_DIR_NAME = "matched"
UNMATCHED_DIR_NAME = "unmatched"
UNKNOWN_DIR_NAME = "unknown"
