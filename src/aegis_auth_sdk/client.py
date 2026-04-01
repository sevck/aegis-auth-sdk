#!/usr/bin/env python
# coding:utf-8

import json
import ssl
import urllib.request
import urllib.parse
import urllib.error
from typing import Any, Optional

from .exceptions import AegisError
from .response import AegisResponse


class AegisClient:
    """
    Aegis Auth 客户端。

    提供两类能力：
    1. 应用管理 API — 使用 X-App-ID + X-Secret-Key 认证
    2. WebAuthn 代理 — 转发注册/认证请求到 Aegis 服务端

    Args:
        base_url:    Aegis Auth 服务地址，如 ``https://your-server:8000``
        app_id:      应用 ID（在管理平台创建服务后获取）
        secret_key:  应用密钥（创建服务时生成）
        verify_ssl:  是否验证 SSL 证书（自签名证书请设为 False）
        timeout:     请求超时时间（秒）
    """

    def __init__(
        self,
        base_url: str,
        app_id: str,
        secret_key: str,
        verify_ssl: bool = False,
        timeout: int = 10,
    ):
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

    def _request(
        self,
        method: str,
        path: str,
        body: Optional[dict] = None,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        auth: bool = True,
    ) -> Any:
        """发送请求并返回解析后的 JSON（用于管理 API）"""
        url = f"{self.base_url}{path}"

        if params:
            filtered = {k: str(v) for k, v in params.items() if v is not None}
            if filtered:
                url += "?" + urllib.parse.urlencode(filtered)

        req_headers = {"Content-Type": "application/json"}
        if auth:
            req_headers["X-App-ID"] = self.app_id
            req_headers["X-Secret-Key"] = self.secret_key
        if headers:
            req_headers.update(headers)

        data = json.dumps(body).encode("utf-8") if body else None
        req = urllib.request.Request(url, data=data, headers=req_headers, method=method)

        try:
            resp = urllib.request.urlopen(req, timeout=self.timeout, context=self._ssl_ctx)
            return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            try:
                detail = json.loads(e.read().decode("utf-8"))
                msg = detail.get("error") or detail.get("detail") or str(detail)
            except Exception:
                msg = e.reason
            raise AegisError(e.code, msg) from None

    def _raw_request(
        self,
        method: str,
        path: str,
        body: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> AegisResponse:
        """发送请求并返回 AegisResponse（用于 WebAuthn 代理）"""
        url = f"{self.base_url}{path}"

        req_headers = {"Content-Type": "application/json"}
        if headers:
            req_headers.update(headers)

        data = json.dumps(body).encode("utf-8") if body else None
        req = urllib.request.Request(url, data=data, headers=req_headers, method=method)

        try:
            resp = urllib.request.urlopen(req, timeout=self.timeout, context=self._ssl_ctx)
            text = resp.read().decode("utf-8")
            return AegisResponse(resp.status, text)
        except urllib.error.HTTPError as e:
            text = e.read().decode("utf-8")
            return AegisResponse(e.code, text)

    # ── 应用管理 API ─────────────────────────────────────────

    def get_app_info(self) -> dict:
        """
        获取应用基本信息。

        Returns:
            包含 app, app_id, domain, status, allow_register, description 的字典
        """
        return self._request("GET", "/api/app/info")

    def get_users(self) -> dict:
        """
        获取应用下所有已注册用户。

        Returns:
            ``{"total": int, "users": [{"username": str, "status": bool, ...}]}``
        """
        return self._request("GET", "/api/app/users")

    def delete_user(self, username: str) -> dict:
        """
        删除指定用户及其所有设备凭证（不可逆）。

        Args:
            username: 要删除的用户名
        """
        return self._request("POST", "/api/app/users/delete", body={"username": username})

    def set_user_status(self, username: str, status: bool) -> dict:
        """
        启用或禁用指定用户。

        Args:
            username: 用户名
            status:   True=启用, False=禁用
        """
        return self._request(
            "POST", "/api/app/users/status",
            body={"username": username, "status": status},
        )

    def set_app_register(self, allow: bool) -> dict:
        """
        启用或禁用应用注册功能。

        禁用后新用户将无法在此应用上注册 WebAuthn 凭证。

        Args:
            allow: True=允许注册, False=禁止注册
        """
        return self._request(
            "POST", "/api/app/register",
            body={"allow_register": allow},
        )

    def get_logs(
        self,
        page: int = 1,
        page_size: int = 20,
        username: Optional[str] = None,
        log_type: Optional[str] = None,
    ) -> dict:
        """
        查询应用下的操作日志。

        Args:
            page:      页码（默认 1）
            page_size: 每页条数（默认 20，最大 100）
            username:  按用户名筛选
            log_type:  日志类型（register_options / register_verify /
                       auth_options / auth_verify）
        """
        return self._request(
            "GET", "/api/app/logs",
            params={"page": page, "page_size": page_size,
                    "username": username, "log_type": log_type},
        )

    # ── WebAuthn 代理 ────────────────────────────────────────

    def get_register_options(self, username: str) -> AegisResponse:
        """
        获取用户注册选项（WebAuthn 代理）。

        将请求代理到 Aegis 服务端的注册 options 接口，
        返回的数据可直接传给前端 ``navigator.credentials.create()``。

        Args:
            username: 用户名

        Returns:
            AegisResponse，可通过 .status_code / .json() / .text 使用
        """
        return self._raw_request(
            "POST",
            f"/api/registration/{self.app_id}/{username}/options",
        )

    def register_verify(self, username: str, credential: dict) -> AegisResponse:
        """
        验证用户注册（WebAuthn 代理）。

        将前端返回的凭证数据发送到 Aegis 服务端进行验证。

        Args:
            username:   用户名
            credential: 前端 navigator.credentials.create() 序列化后的凭证对象

        Returns:
            AegisResponse，验证成功时 .json() 返回 {"verified": true}
        """
        return self._raw_request(
            "POST",
            f"/api/registration/{self.app_id}/{username}/verification",
            body=credential,
        )

    def get_login_options(self, username: str) -> AegisResponse:
        """
        获取用户认证选项（WebAuthn 代理）。

        将请求代理到 Aegis 服务端的认证 options 接口，
        返回的数据可直接传给前端 ``navigator.credentials.get()``。

        Args:
            username: 用户名

        Returns:
            AegisResponse，可通过 .status_code / .json() / .text 使用
        """
        return self._raw_request(
            "POST",
            f"/api/authentication/{self.app_id}/{username}/options",
        )

    def get_login_verify(
        self, username: str, credential: dict, origin: Optional[str] = None
    ) -> AegisResponse:
        """
        验证用户认证（WebAuthn 代理）。

        将前端返回的凭证数据发送到 Aegis 服务端进行验证。

        Args:
            username:   用户名
            credential: 前端 navigator.credentials.get() 序列化后的凭证对象
            origin:     请求来源（可选），用于 WebAuthn origin 校验

        Returns:
            AegisResponse，验证成功时 .json() 返回 {"verified": true}
        """
        extra_headers = {}
        if origin:
            extra_headers["origin"] = origin
        return self._raw_request(
            "POST",
            f"/api/authentication/{self.app_id}/{username}/verification",
            body=credential,
            headers=extra_headers if extra_headers else None,
        )
