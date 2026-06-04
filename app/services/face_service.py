import os
from pathlib import Path
from typing import Optional

from app.config import DEFAULT_DEEPFACE_HOME, DEFAULT_DETECTOR_BACKEND, DEFAULT_MODEL_NAME
from app.models.scan_result import ScanResult
from app.services.photo_service import find_photo_files
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_deepface():
    os.environ.setdefault("DEEPFACE_HOME", str(DEFAULT_DEEPFACE_HOME))
    DEFAULT_DEEPFACE_HOME.mkdir(parents=True, exist_ok=True)

    # On some macOS TensorFlow builds, touching tf.keras before DeepFace import
    # avoids a delayed tensorflow.keras module registration failure.
    import tensorflow as tf

    _ = tf.keras
    from tensorflow.keras.models import Sequential  # noqa: F401
    from deepface import DeepFace

    return DeepFace


class FaceService:
    def __init__(
        self,
        threshold: float,
        model_name: str = DEFAULT_MODEL_NAME,
        detector_backend: str = DEFAULT_DETECTOR_BACKEND,
    ) -> None:
        self.threshold = threshold
        self.model_name = model_name
        self.detector_backend = detector_backend

    def load_target_samples(self, target_dir: Path) -> list[Path]:
        deepface = get_deepface()
        samples = find_photo_files(target_dir)
        valid_samples: list[Path] = []

        for sample in samples:
            try:
                faces = deepface.extract_faces(
                    img_path=str(sample),
                    detector_backend=self.detector_backend,
                    enforce_detection=True,
                )
                if faces:
                    valid_samples.append(sample)
                    logger.info("Target sample loaded: %s", sample)
                else:
                    logger.warning("No face in target sample: %s", sample)
            except Exception as exc:
                logger.warning("Failed to load target sample %s: %s", sample, exc)

        return valid_samples

    def classify_photo(self, photo_path: Path, target_samples: list[Path]) -> ScanResult:
        deepface = get_deepface()
        if not target_samples:
            return ScanResult(
                source_path=photo_path,
                status="unknown",
                error="有効な対象人物サンプル写真がありません。",
            )

        try:
            faces = deepface.extract_faces(
                img_path=str(photo_path),
                detector_backend=self.detector_backend,
                enforce_detection=True,
            )
            if not faces:
                return ScanResult(source_path=photo_path, status="unknown", error="顔を検出できません。")
        except Exception as exc:
            logger.warning("Face detection failed %s: %s", photo_path, exc)
            return ScanResult(source_path=photo_path, status="unknown", error=f"顔検出失敗: {exc}")

        best_distance: Optional[float] = None
        best_sample: Optional[Path] = None
        compare_errors: list[str] = []

        for sample in target_samples:
            try:
                result = deepface.verify(
                    img1_path=str(sample),
                    img2_path=str(photo_path),
                    model_name=self.model_name,
                    detector_backend=self.detector_backend,
                    enforce_detection=False,
                )
                distance = float(result["distance"])
                if best_distance is None or distance < best_distance:
                    best_distance = distance
                    best_sample = sample
            except Exception as exc:
                compare_errors.append(f"{sample.name}: {exc}")
                logger.warning("Verify failed sample=%s photo=%s error=%s", sample, photo_path, exc)

        if best_distance is None:
            return ScanResult(
                source_path=photo_path,
                status="unknown",
                error="照合できませんでした。 " + " / ".join(compare_errors),
            )

        if best_distance <= self.threshold:
            return ScanResult(
                source_path=photo_path,
                status="matched",
                best_distance=best_distance,
                matched_sample=best_sample,
            )

        return ScanResult(
            source_path=photo_path,
            status="unmatched",
            best_distance=best_distance,
            matched_sample=best_sample,
        )
