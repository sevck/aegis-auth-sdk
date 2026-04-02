# Aegis Auth SDK Integration Guide

WebAuthn passwordless authentication SDK — Installation, initialization, and method reference.

---

## Installation

```bash
pip install aegis-auth-sdk
```

Requirements: Python 2.7 or Python 3.6+, no third-party dependencies.

---

## Initialization

```python
from aegis_auth_sdk import AegisClient

client = AegisClient(
    base_url="https://your-server:8000",
    app_id="your_app_id",
    secret_key="your_secret_key"
)
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `base_url` | str | Yes | — | Aegis Auth server address |
| `app_id` | str | Yes | — | Application ID |
| `secret_key` | str | Yes | — | Application Secret Key |
| `verify_ssl` | bool | No | `False` | Whether to verify SSL certificates (set `False` for self-signed certs) |
| `timeout` | int | No | `10` | Request timeout in seconds |

---

## App Management Methods

These methods use `X-App-ID` + `X-Secret-Key` header authentication and return parsed JSON (dict).

### get_app_info()

Get basic information about the current application.

```python
info = client.get_app_info()
```

**Parameters:** None

**Returns:** `dict`

```json
{
  "app": "my-app",
  "app_id": "6e7fd30dad894d7d8ca2e73ea4f285cb",
  "domain": "example.com",
  "status": true,
  "allow_register": true,
  "allow_multi_device": false,
  "description": "Example app"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `app` | str | Application name |
| `app_id` | str | Application ID |
| `domain` | str | WebAuthn RP ID (domain) |
| `status` | bool | Application enabled status |
| `allow_register` | bool | Whether registration is allowed |
| `allow_multi_device` | bool | Whether multi-device registration is allowed |
| `description` | str | Application description |

---

### get_users()

Get all registered users under the application.

```python
result = client.get_users()
for user in result["users"]:
    print("%s - Status: %s" % (user["username"], "Enabled" if user["status"] else "Disabled"))
```

**Parameters:** None

**Returns:** `dict`

```json
{
  "total": 2,
  "users": [
    {
      "username": "alice",
      "status": true,
      "device_id": "base64url...",
      "register_time": "2026-01-15 10:30:00",
      "register_ip": "10.0.0.1",
      "login_time": "2026-03-30 14:20:00",
      "login_ip": "10.0.0.2"
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `total` | int | Total number of users |
| `users` | list | User list |
| `users[].username` | str | Username |
| `users[].status` | bool | User enabled status |
| `users[].device_id` | str | WebAuthn credential ID |
| `users[].register_time` | str | Registration time |
| `users[].register_ip` | str | Registration IP |
| `users[].login_time` | str/null | Last login time |
| `users[].login_ip` | str/null | Last login IP |

---

### set_user_status(username, status)

Enable or disable a user. Disabled users cannot authenticate via WebAuthn.

```python
client.set_user_status("alice", False)  # Disable
client.set_user_status("alice", True)   # Enable
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `username` | str | Yes | Username |
| `status` | bool | Yes | `True` = enable, `False` = disable |

**Returns:** `dict`

```json
{ "success": true, "status": false }
```

---

### delete_user(username)

Delete a user and all their device credentials. **This action is irreversible.**

```python
client.delete_user("alice")
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `username` | str | Yes | Username to delete |

**Returns:** `dict`

```json
{ "success": true }
```

---

### set_app_register(allow)

Enable or disable the application's registration function. When disabled, new users cannot register WebAuthn credentials.

```python
client.set_app_register(False)  # Disable registration
client.set_app_register(True)   # Enable registration
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `allow` | bool | Yes | `True` = allow registration, `False` = disable registration |

**Returns:** `dict`

```json
{ "success": true, "allow_register": false }
```

---

### set_app_multi_device(allow)

Enable or disable multi-device registration. When enabled, a single user can register WebAuthn credentials on multiple devices.

```python
client.set_app_multi_device(True)   # Enable multi-device
client.set_app_multi_device(False)  # Single-device only
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `allow` | bool | Yes | `True` = allow multi-device, `False` = single-device only |

**Returns:** `dict`

```json
{ "success": true, "allow_multi_device": true }
```

---

### get_logs(page, page_size, username, log_type)

Query WebAuthn operation logs under the application.

```python
logs = client.get_logs(log_type="auth_verify", page_size=5)
for entry in logs["items"]:
    print("[%s] %s from %s" % (entry["log_time"], entry["username"], entry["log_ip"]))
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | int | No | `1` | Page number |
| `page_size` | int | No | `20` | Items per page (max 100) |
| `username` | str | No | `None` | Filter by username |
| `log_type` | str | No | `None` | Filter by log type: `register_options` / `register_verify` / `auth_options` / `auth_verify` / `sdk_set_register` / `sdk_set_multi_device` |

**Returns:** `dict`

```json
{
  "total": 50,
  "page": 1,
  "page_size": 5,
  "items": [
    {
      "username": "alice",
      "device_id": null,
      "log_time": "2026-03-30 14:20:00",
      "log_ip": "10.0.0.2",
      "log_type": "auth_verify",
      "log_info": "{\"verified\": true}"
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `total` | int | Total log count |
| `page` | int | Current page |
| `page_size` | int | Items per page |
| `items[].username` | str | Username |
| `items[].device_id` | str/null | Device ID |
| `items[].log_time` | str | Log time |
| `items[].log_ip` | str | Client IP |
| `items[].log_type` | str | Log type |
| `items[].log_info` | str | Log details (JSON string) |

---

## WebAuthn Proxy Methods

These methods transparently proxy WebAuthn registration/authentication requests to the Aegis server. They return `AegisResponse` objects (not parsed JSON).

### AegisResponse

| Attribute / Method | Type | Description |
|--------------------|------|-------------|
| `.status_code` | int | HTTP status code |
| `.text` | str | Raw response body |
| `.json()` | dict | Parse response body as JSON |

---

### get_register_options(username)

Get WebAuthn registration options (challenge) for a user.

```python
resp = client.get_register_options("alice")
# resp.status_code, resp.json(), resp.text
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `username` | str | Yes | Username |

**Returns:** `AegisResponse` — body contains `PublicKeyCredentialCreationOptions`

---

### get_register_verify(username, credential)

Verify a WebAuthn registration credential.

```python
resp = client.get_register_verify("alice", credential_data)
print(resp.json())  # {"verified": true}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `username` | str | Yes | Username |
| `credential` | dict | Yes | Serialized credential from browser `navigator.credentials.create()` |

**Returns:** `AegisResponse`

```json
{ "verified": true }
```

---

### get_login_options(username)

Get WebAuthn authentication options (challenge) for a user.

```python
resp = client.get_login_options("alice")
# resp.status_code, resp.json(), resp.text
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `username` | str | Yes | Username |

**Returns:** `AegisResponse` — body contains `PublicKeyCredentialRequestOptions`

---

### get_login_verify(username, credential, origin)

Verify a WebAuthn authentication credential.

```python
resp = client.get_login_verify("alice", credential_data)
if resp.json().get("verified"):
    print("Authentication successful")
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `username` | str | Yes | Username |
| `credential` | dict | Yes | Serialized credential from browser `navigator.credentials.get()` |
| `origin` | str | No | Request origin for WebAuthn origin validation |

**Returns:** `AegisResponse`

```json
{ "verified": true }
```

---

## Error Handling

Management API methods raise `AegisError` on HTTP errors. WebAuthn proxy methods return `AegisResponse` with the error status code instead.

```python
from aegis_auth_sdk import AegisClient, AegisError

try:
    client.get_app_info()
except AegisError as e:
    print("Error %d: %s" % (e.status, e.message))
```

| Attribute | Type | Description |
|-----------|------|-------------|
| `e.status` | int | HTTP status code |
| `e.message` | str | Error message |

---

## Error Codes

| HTTP Status | Meaning | Description |
|-------------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Missing or invalid parameters |
| 401 | Unauthorized | Invalid App ID / Secret Key, or app disabled |
| 403 | Forbidden | Registration disabled, or WebAuthn verification failed |
| 404 | Not Found | Resource not found |
| 500 | Server Error | Internal server error |

Error response format:

```json
{ "error": "Error message" }
```
