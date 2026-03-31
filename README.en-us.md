<p align="center">
<a href="https://pypi.org/project/aegis-auth-sdk">
    <img src="https://img.shields.io/pypi/v/aegis-auth-sdk?color=%2334D058&label=pypi%20package" alt="Package version">
</a>
<a href="https://pypi.org/project/aegis-auth-sdk">
    <img src="https://img.shields.io/pypi/pyversions/aegis-auth-sdk.svg?color=%2334D058" alt="Supported Python versions">
</a>
</p>

<p align="center">
<a href="./README.md">English</a> | <a href="./README.zh-cn.md">简体中文</a>
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

info = client.get_app_info()
print(info)

users = client.get_users()
for user in users["users"]:
    print(f'{user["username"]} - Status: {user["status"]}')

client.set_user_status("alice", False)
client.delete_user("alice")

logs = client.get_logs(page=1, page_size=10, log_type="auth_verify")
```

---

## 🌐 Integration Example

### Frontend Example

```javascript
// (Same as your original frontend example)
```

### Backend Example

```python
# (Same as your original backend example)
```

---

## ⚠️ Error Codes

| HTTP Status | Meaning        | Description |
|------------|---------------|-------------|
| 200        | OK            | Request successful |
| 400        | Bad Request   | Missing or invalid parameters |
| 401        | Unauthorized  | Invalid App ID / Secret or app disabled |
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