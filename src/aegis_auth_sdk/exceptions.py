#!/usr/bin/env python
# coding:utf-8


class AegisError(Exception):
    """Aegis API 错误"""

    def __init__(self, status, message):
        self.status = status
        self.message = message
        super(AegisError, self).__init__("[%d] %s" % (status, message))
