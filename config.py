"""Tunable extraction parameters, previously hardcoded inline in parser.py."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ExtractionConfig:
    """Knobs for a DocumentParser run. Override per-instance instead of editing source."""

    # The single page cap: ingestion reads (and chunks/merges across) up to this
    # many pages. A document with more pages than this is flagged truncated —
    # there used to be two separate, disconnected limits here (a smaller one
    # actually used for ingestion, a larger one only used for the truncation
    # flag), which meant a document could silently lose pages while still being
    # reported as "not truncated." One limit now, so the flag is honest.
    max_pages: int = 15
    chunk_max_tokens: int = 3000
    pdf_render_dpi: int = 150
    max_image_dim: int = 1536
    ocr_min_confidence: float = 0.3
    # Chunks are processed sequentially by default (1) — safe, deterministic order.
    # Raise this to fan LLM calls for independent chunks out over threads; chunks are
    # I/O-bound network calls, so a plain ThreadPoolExecutor is enough (no asyncio needed).
    max_concurrent_chunks: int = 1

    def __post_init__(self):
        if self.max_pages <= 0:
            raise ValueError(f"max_pages must be positive, got {self.max_pages}")
        if self.chunk_max_tokens <= 0:
            raise ValueError(f"chunk_max_tokens must be positive, got {self.chunk_max_tokens}")
        if self.pdf_render_dpi <= 0:
            raise ValueError(f"pdf_render_dpi must be positive, got {self.pdf_render_dpi}")
        if self.max_image_dim <= 0:
            raise ValueError(f"max_image_dim must be positive, got {self.max_image_dim}")
        if not 0.0 <= self.ocr_min_confidence <= 1.0:
            raise ValueError(f"ocr_min_confidence must be between 0 and 1, got {self.ocr_min_confidence}")
        if self.max_concurrent_chunks <= 0:
            raise ValueError(f"max_concurrent_chunks must be positive, got {self.max_concurrent_chunks}")
