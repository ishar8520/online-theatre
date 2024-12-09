from __future__ import annotations

import logging
import os


def setup_logging(*, filename: str | os.PathLike[str] | None = None) -> None:
    logging.basicConfig(filename=filename, level=logging.DEBUG)
