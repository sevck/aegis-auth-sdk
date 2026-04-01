<p align="center">
<a href="https://pypi.org/project/aegis-auth-sdk">
    <img src="https://img.shields.io/pypi/v/aegis-auth-sdk?color=%2334D058&label=pypi%20package" alt="Package version">
</a>
<a href="https://pypi.org/project/aegis-auth-sdk">
    <img src="https://img.shields.io/pypi/pyversions/aegis-auth-sdk.svg?color=%2334D058" alt="Supported Python versions">
</a>
</p>

<p align="center">
<a href="./README.en-us.md">English</a> | <a href="./README.md">简体中文</a>
</p>

# Aegis Auth SDK

## 🚀 Core Value: Making Authentication Simple and Secure

Aegis Auth SDK is a modern authentication toolkit for Web applications, built on the **WebAuthn (FIDO2) standard**. It enables developers to quickly implement **passwordless authentication**, fundamentally eliminating the security risks and usability issues associated with traditional passwords.

---

## 🌟 Key Features

### 1. Excellent Developer Experience
- **Out-of-the-box**: Install via `pip` with zero complex setup  
- **Highly abstracted**: WebAuthn complexity is fully encapsulated  
- **Fast integration**: Implement registration and login in minutes  

---

### 2. Secure & Compliant Passwordless Solution
- **Passwordless by design**: Eliminates password reuse, phishing, and credential stuffing  
- **Minimal sensitive data**: Only public keys stored server-side, no biometric raw data  
- **Anti-automation**: Challenge-response mechanism prevents brute-force and bot attacks  

---

### 3. Cross-platform & Biometric Support
- **Multi-platform compatibility**:
  - Windows Hello  
  - macOS Touch ID  
  - iOS / Android (Face ID / Fingerprint)  
- **Device binding**: Strong "User + Device" trust model  

---

### 4. Enterprise-grade User Management
- **Unified user view**: Credential management, device binding, status control  
- **Audit logs**: Full authentication traceability  

---

## 🛠 Quick Start

### Installation

```bash
pip install aegis-auth-sdk
```

### SDK Example

```python
from aegis_auth_sdk import AegisClient

client = AegisClient(
    base_url="https://your-server:8000",
    app_id="your_app_id",
    secret_key="your_secret_key"
)

# Get app info
app_info = client.get_app_info()
print(app_info)

# List users
result = client.get_users()
for user in result["users"]:
    print(f'{user["username"]} - Status: {"Enabled" if user["status"] else "Disabled"}')

# Enable / disable user
client.set_user_status("alice", False)

# Enable / disable app registration
client.set_app_register(False)

# Delete user
client.delete_user("alice")

# Query logs
logs = client.get_logs(log_type="auth_verify", page_size=5)
for entry in logs["items"]:
    print(f'[{entry["log_time"]}] {entry["username"]} from {entry["log_ip"]} - {entry["log_info"]}')
```

---

## 🌐 Integration Example

### Frontend Example

```javascript
export const fetchUserLoginOptions = (param) => {
    return request({
        url: '/api/user/login/options',
        headers: { 'Content-Type': 'application/json', 'Login-Name': param.username },
        method: 'post',
        data: param
    });
};

export const fetchUserLoginVerify = (username, asseResp) => {
    return request({
        url: '/api/user/login/verification',
        method: 'post',
        headers: { 'Content-Type': 'application/json', 'Login-Name': username },
        data: asseResp
    });
};

const resp = await fetchUserLoginOptions(param);
const asseResp = await startAuthentication(resp.data);
const verificationResp = await fetchUserLoginVerify(param.username, asseResp);

if (verificationResp.data.code === 200) {
    localStorage.setItem('Authorization', verificationResp.data.token_type + ' ' + verificationResp.data.access_token);
    router.push('/');
}
```

### Backend Example

```python
from aegis_auth_sdk import AegisClient
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import jwt, datetime

SECRET_KEY = "your-jwt-secret"
client = AegisClient(
    base_url="https://your-server:8000",
    app_id="your_app_id",
    secret_key="your_secret_key"
)

user = APIRouter()

@user.post("/login/options")
async def user_login_options(req: dict, request: Request):
    username = request.headers.get("Login-Name")
    resp = client.get_login_options(username)
    return JSONResponse(status_code=resp.status_code, content=resp.json())

@user.post("/login/verification")
async def user_login_verification(req: dict, request: Request):
    username = request.headers.get("Login-Name")
    resp = client.get_login_verify(username, req)
    if resp.json().get("verified", False):
        token = jwt.encode({
            "user": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }, SECRET_KEY, algorithm="HS256")
        return JSONResponse(content={"access_token": token, "token_type": "Bearer", "code": 200})
    return JSONResponse(status_code=200, content={"code": 500, "msg": resp.text})

@user.post("/register/options")
async def user_register_options(req: dict, request: Request):
    username = request.headers.get("Login-Name")
    resp = client.get_register_options(username)
    return JSONResponse(status_code=resp.status_code, content=resp.json())

@user.post("/register/verification")
async def user_register_verification(req: dict, request: Request):
    username = request.headers.get("Login-Name")
    resp = client.register_verify(username, req)
    return JSONResponse(status_code=resp.status_code, content=resp.json())
```

---

## ⚠️ Error Codes

| HTTP Status | Meaning        | Description |
|------------|---------------|-------------|
| 200        | OK            | Request successful |
| 400        | Bad Request   | Missing or invalid parameters |
| 401        | Unauthorized  | Invalid App ID / Secret or app disabled |
| 403        | Forbidden     | Registration disabled or WebAuthn verification failed |
| 404        | Not Found     | Resource not found |
| 500        | Server Error  | Internal server error |

---

## 📦 Error Response Format

```json
{ "error": "Error message" }
```

or:

```json
{ "detail": "Error message" }
```