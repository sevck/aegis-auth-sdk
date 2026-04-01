#!/usr/bin/env python
# coding:utf-8

import json


class AegisResponse(object):
    """
    统一响应对象，兼容 requests.Response 常用接口。

    Attributes:
        status_code: HTTP 状态码
        text:        响应体原始文本
    """

    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text

    def json(self):
        """解析响应体为 JSON"""
        return json.loads(self.text)

    def __repr__(self):
        return "<AegisResponse [%d]>" % self.status_code
