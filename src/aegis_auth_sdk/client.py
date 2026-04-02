#!/usr/bin/env python
# coding:utf-8

import json
import ssl

try:
    # Python 3
    import urllib.request as urllib_request
    import urllib.parse as urllib_parse
    import urllib.error as urllib_error
except ImportError:
    # Python 2
    import urllib2 as urllib_request
    import urllib as urllib_parse
    urllib_error = urllib_request

from .exceptions import AegisError
from .response import AegisResponse


class AegisClient(object):
    """
    Aegis Auth 客户端。

    提供两类能力：
    1. 应用管理 API — 使用 X-App-ID + X-Secret-Key 认证
    2. WebAuthn 代理 — 转发注册/认证请求到 Aegis 服务端

    :param base_url:    Aegis Auth 服务地址，如 ``https://your-server:8000``
    :param app_id:      应用 ID（在管理平台创建服务后获取）
    :param secret_key:  应用密钥（创建服务时生成）
    :param verify_ssl:  是否验证 SSL 证书（自签名证书请设为 False）
    :param timeout:     请求超时时间（秒）
    """

    def __init__(self, base_url, app_id, secret_key, verify_ssl=False, timeout=10):
        self.base_url = base_url.rstrip("/")
        self.app_id = app_id
        self.secret_key = secret_key
        self.timeout = timeout

        if verify_ssl:
            self._ssl_ctx = None
        else:
            self._ssl_ctx = ssl.create_default_context()
            self._ssl_ctx.check_hostname = False
            self._ssl_ctx.verify_mode = ssl.CERT_NONE

    # ── 内部请求方法 ─────────────────────────────────────────

    def _request(self, method, path, body=None, params=None, headers=None, auth=True):
        """发送请求并返回解析后的 JSON（用于管理 API）"""
        url = self.base_url + path

        if params:
            filtered = dict((k, str(v)) for k, v in params.items() if v is not None)
            if filtered:
                url += "?" + urllib_parse.urlencode(filtered)

        req_headers = {"Content-Type": "application/json"}
        if auth:
            req_headers["X-App-ID"] = self.app_id
            req_headers["X-Secret-Key"] = self.secret_key
        if headers:
            req_headers.update(headers)

        data = json.dumps(body).encode("utf-8") if body else None
        req = urllib_request.Request(url, data=data, headers=req_headers)
        req.get_method = lambda: method

        try:
            resp = urllib_request.urlopen(req, timeout=self.timeout, context=self._ssl_ctx)
            return json.loads(resp.read().decode("utf-8"))
        except urllib_error.HTTPError as e:
            try:
                detail = json.loads(e.read().decode("utf-8"))
                msg = detail.get("error") or detail.get("detail") or str(detail)
            except Exception:
                msg = str(e.reason) if hasattr(e, "reason") else str(e)
            raise AegisError(e.code, msg)

    def _raw_request(self, method, path, body=None, headers=None):
        """发送请求并返回 AegisResponse（用于 WebAuthn 代理）"""
        url = self.base_url + path

        req_headers = {"Content-Type": "application/json"}
        if headers:
            req_headers.update(headers)

        data = json.dumps(body).encode("utf-8") if body else None
        req = urllib_request.Request(url, data=data, headers=req_headers)
        req.get_method = lambda: method

        try:
            resp = urllib_request.urlopen(req, timeout=self.timeout, context=self._ssl_ctx)
            text = resp.read().decode("utf-8")
            code = resp.getcode()
            return AegisResponse(code, text)
        except urllib_error.HTTPError as e:
            text = e.read().decode("utf-8")
            return AegisResponse(e.code, text)

    # ── 应用管理 API ─────────────────────────────────────────

    def get_app_info(self):
        """
        获取应用基本信息。

        :returns: 包含 app, app_id, domain, status, allow_register, description 的字典
        """
        return self._request("GET", "/api/app/info")

    def get_users(self):
        """
        获取应用下所有已注册用户。

        :returns: ``{"total": int, "users": [...]}``
        """
        return self._request("GET", "/api/app/users")

    def delete_user(self, username):
        """
        删除指定用户及其所有设备凭证（不可逆）。

        :param username: 要删除的用户名
        """
        return self._request("POST", "/api/app/users/delete", body={"username": username})

    def set_user_status(self, username, status):
        """
        启用或禁用指定用户。

        :param username: 用户名
        :param status:   True=启用, False=禁用
        """
        return self._request(
            "POST", "/api/app/users/status",
            body={"username": username, "status": status},
        )

    def set_app_register(self, allow):
        """
        启用或禁用应用注册功能。

        禁用后新用户将无法在此应用上注册 WebAuthn 凭证。

        :param allow: True=允许注册, False=禁止注册
        """
        return self._request(
            "POST", "/api/app/register",
            body={"allow_register": allow},
        )

    def set_app_multi_device(self, allow):
        """
        启用或禁用应用多设备注册功能。

        启用后同一用户可在多个设备上注册 WebAuthn 凭证。

        :param allow: True=允许多设备注册, False=禁止多设备注册
        """
        return self._request(
            "POST", "/api/app/multi_device",
            body={"allow_multi_device": allow},
        )

    def get_logs(self, page=1, page_size=20, username=None, log_type=None):
        """
        查询应用下的操作日志。

        :param page:      页码（默认 1）
        :param page_size: 每页条数（默认 20，最大 100）
        :param username:  按用户名筛选
        :param log_type:  日志类型（register_options / register_verify /
                          auth_options / auth_verify）
        """
        return self._request(
            "GET", "/api/app/logs",
            params={"page": page, "page_size": page_size,
                    "username": username, "log_type": log_type},
        )

    # ── WebAuthn 代理 ────────────────────────────────────────

    def get_register_options(self, username):
        """
        获取用户注册选项（WebAuthn 代理）。

        :param username: 用户名
        :returns: AegisResponse
        """
        return self._raw_request(
            "POST",
            "/api/registration/%s/%s/options" % (self.app_id, username),
        )

    def register_verify(self, username, credential):
        """
        验证用户注册（WebAuthn 代理）。

        :param username:   用户名
        :param credential: 前端序列化后的凭证对象
        :returns: AegisResponse
        """
        return self._raw_request(
            "POST",
            "/api/registration/%s/%s/verification" % (self.app_id, username),
            body=credential,
        )

    def get_login_options(self, username):
        """
        获取用户认证选项（WebAuthn 代理）。

        :param username: 用户名
        :returns: AegisResponse
        """
        return self._raw_request(
            "POST",
            "/api/authentication/%s/%s/options" % (self.app_id, username),
        )

    def get_login_verify(self, username, credential, origin=None):
        """
        验证用户认证（WebAuthn 代理）。

        :param username:   用户名
        :param credential: 前端序列化后的凭证对象
        :param origin:     请求来源（可选），用于 WebAuthn origin 校验
        :returns: AegisResponse
        """
        extra_headers = {}
        if origin:
            extra_headers["origin"] = origin
        return self._raw_request(
            "POST",
            "/api/authentication/%s/%s/verification" % (self.app_id, username),
            body=credential,
            headers=extra_headers if extra_headers else None,
        )
