#!/usr/bin/env python
# coding:utf-8


class AegisError(Exception):
    """Aegis API 错误"""

    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(f"[{status}] {message}")
