"""Phase 1 OCR Engine: Fast, layout-aware OCR for images and scanned PDFs."""

from __future__ import annotations

import io
import logging
import threading
from typing import List, Tuple
from PIL import Image

logger = logging.getLogger(__name__)

try:
    from rapidocr_onnxruntime import RapidOCR
    _rapid_ocr = RapidOCR()
    HAS_RAPID_OCR = True
except Exception:
    logger.warning("RapidOCR unavailable; OCR extraction will return empty text.", exc_info=True)
    _rapid_ocr = None
    HAS_RAPID_OCR = False

# The RapidOCR/onnxruntime session is a shared module-level singleton; serialize
# calls so concurrent requests (e.g. behind a web server) don't race on it.
_ocr_lock = threading.Lock()


def extract_text_from_image_ocr(image_bytes: bytes, structured_mode: bool = False, min_confidence: float = 0.3) -> str:
    """Extract layout-preserved text from an image (PNG/JPG) using local OCR engine.

    Returns a clean, line-grouped text representation preserving horizontal spacing.
    """
    if not HAS_RAPID_OCR or _rapid_ocr is None:
        return ""

    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode != "RGB":
            img = img.convert("RGB")
        
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        
        with _ocr_lock:
            result, _ = _rapid_ocr(buf.getvalue())
        if not result:
            return ""

        lines: List[Tuple[float, float, str]] = []
        for box, text, conf in result:
            conf_val = float(conf) if conf is not None else 0.0
            if conf_val > min_confidence and text and str(text).strip():
                y0 = min(pt[1] for pt in box)
                x0 = min(pt[0] for pt in box)
                lines.append((y0, x0, str(text).strip()))

        lines.sort(key=lambda item: (round(item[0] / 15), item[1]))

        grouped_lines: List[str] = []
        current_y_group = -1
        current_line_parts: List[str] = []

        for y0, x0, text in lines:
            group = round(y0 / 15)
            if structured_mode:
                text_formatted = f"[X:{int(x0)}] {text}"
            else:
                text_formatted = text
                
            if group != current_y_group:
                if current_line_parts:
                    grouped_lines.append("    ".join(current_line_parts))
                current_y_group = group
                current_line_parts = [text_formatted]
            else:
                current_line_parts.append(text_formatted)

        if current_line_parts:
            grouped_lines.append("    ".join(current_line_parts))

        return "\n".join(grouped_lines)
    except Exception:
        return ""
