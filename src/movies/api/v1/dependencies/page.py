from __future__ import annotations


class Page:
    def __init__(self, page_size: int = 50, page_number: int = 1):
        self.size = page_size if page_size <= 50 else 50
        self.number = page_number if page_number >= 1 else 1
