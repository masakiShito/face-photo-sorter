from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

from app.config import DEFAULT_INPUT_DIR, DEFAULT_OUTPUT_DIR, DEFAULT_TARGET_DIR, DEFAULT_THRESHOLD
from app.models.scan_result import ScanResult
from app.services.face_service import FaceService
from app.services.file_service import copy_photo, prepare_output_dirs
from app.services.photo_service import find_photo_files
from app.utils.logger import get_logger

logger = get_logger(__name__)


def path_input(label: str, default_path: Path) -> Path:
    value = st.text_input(label, value=str(default_path))
    return Path(value).expanduser().resolve()


def result_to_row(result: ScanResult) -> dict[str, object]:
    return {
        "source": str(result.source_path),
        "status": result.status,
        "copied_to": str(result.copied_path) if result.copied_path else "",
        "best_distance": result.best_distance,
        "matched_sample": str(result.matched_sample) if result.matched_sample else "",
        "error": result.error or "",
    }


def run_scan(input_dir: Path, target_dir: Path, output_dir: Path, threshold: float) -> list[ScanResult]:
    logger.info("Scan started input=%s target=%s output=%s threshold=%s", input_dir, target_dir, output_dir, threshold)

    photo_files = find_photo_files(input_dir)
    output_dirs = prepare_output_dirs(output_dir)

    face_service = FaceService(threshold=threshold)
    target_samples = face_service.load_target_samples(target_dir)

    progress = st.progress(0)
    status_text = st.empty()
    summary_placeholder = st.empty()
    results: list[ScanResult] = []

    total = len(photo_files)
    for index, photo_path in enumerate(photo_files, start=1):
        status_text.write(f"処理中: {index} / {total} - {photo_path.name}")

        try:
            result = face_service.classify_photo(photo_path, target_samples)
            copied_path = copy_photo(photo_path, output_dirs[result.status])
            result = ScanResult(
                source_path=result.source_path,
                status=result.status,
                copied_path=copied_path,
                best_distance=result.best_distance,
                matched_sample=result.matched_sample,
                error=result.error,
            )
            logger.info("Classified %s -> %s", photo_path, result.status)
        except Exception as exc:
            logger.exception("Failed to process %s", photo_path)
            copied_path = None
            try:
                copied_path = copy_photo(photo_path, output_dirs["unknown"])
            except Exception as copy_exc:
                logger.exception("Failed to copy unknown photo %s: %s", photo_path, copy_exc)
            result = ScanResult(
                source_path=photo_path,
                status="unknown",
                copied_path=copied_path,
                error=f"処理失敗: {exc}",
            )

        results.append(result)
        progress.progress(index / total if total else 1.0)

        matched = sum(1 for item in results if item.status == "matched")
        unmatched = sum(1 for item in results if item.status == "unmatched")
        unknown = sum(1 for item in results if item.status == "unknown")
        errors = sum(1 for item in results if item.has_error)
        summary_placeholder.info(
            f"解析対象: {total} / matched: {matched} / unmatched: {unmatched} / unknown: {unknown} / エラー: {errors}"
        )

    status_text.write("処理完了")
    logger.info("Scan finished total=%s", total)
    return results


def main() -> None:
    st.set_page_config(page_title="Face Photo Sorter", page_icon="📷", layout="wide")
    st.title("Face Photo Sorter")
    st.caption("ローカルPC上で、対象人物が写っている可能性が高い写真を抽出してコピー分類します。")

    with st.sidebar:
        st.header("スキャン設定")
        input_dir = path_input("解析対象の写真フォルダ", DEFAULT_INPUT_DIR)
        target_dir = path_input("対象人物のサンプル写真フォルダ", DEFAULT_TARGET_DIR)
        output_dir = path_input("出力フォルダ", DEFAULT_OUTPUT_DIR)
        threshold = st.slider(
            "類似度判定のしきい値（DeepFace distance）",
            min_value=0.1,
            max_value=1.0,
            value=float(DEFAULT_THRESHOLD),
            step=0.01,
            help="距離が小さいほど似ています。この値以下を matched として扱います。",
        )
        start = st.button("スキャン開始", type="primary")

    st.write("### フォルダ")
    st.code(
        f"input:  {input_dir}\ntarget: {target_dir}\noutput: {output_dir}",
        language="txt",
    )

    if not start:
        st.info("左側の設定を確認し、「スキャン開始」を押してください。")
        return

    try:
        photo_files = find_photo_files(input_dir)
    except Exception as exc:
        st.error(f"解析対象フォルダを読み込めません: {exc}")
        logger.exception("Input directory validation failed")
        return

    try:
        target_files = find_photo_files(target_dir)
    except Exception as exc:
        st.error(f"サンプル写真フォルダを読み込めません: {exc}")
        logger.exception("Target directory validation failed")
        return

    if not photo_files:
        st.warning("解析対象フォルダに対応画像がありません。")
        return

    if not target_files:
        st.warning("対象人物のサンプル写真フォルダに対応画像がありません。")
        return

    st.write("### 進捗")
    results = run_scan(input_dir, target_dir, output_dir, threshold)

    matched = sum(1 for item in results if item.status == "matched")
    unmatched = sum(1 for item in results if item.status == "unmatched")
    unknown = sum(1 for item in results if item.status == "unknown")
    errors = sum(1 for item in results if item.has_error)

    st.write("### 結果サマリー")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("解析対象枚数", len(results))
    col2.metric("matched", matched)
    col3.metric("unmatched", unmatched)
    col4.metric("unknown", unknown)
    col5.metric("エラー", errors)

    st.write("### 最終結果一覧")
    st.dataframe(pd.DataFrame([result_to_row(result) for result in results]), use_container_width=True)


if __name__ == "__main__":
    main()
