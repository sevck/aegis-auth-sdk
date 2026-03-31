<p align="center">
<a href="https://github.com/sevck/aegis-auth-sdk/actions">
    <img src="https://github.com/sevck/aegis-auth-sdk/actions/workflows/test.yml/badge.svg" alt="Test">
</a>
<a href="https://coverage-badge.samuelcolvin.workers.dev/redirect/sevck/aegis-auth-sdk">
    <img src="https://coverage-badge.samuelcolvin.workers.dev/sevck/aegis-auth-sdk.svg" alt="Coverage">
</a>
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

## 🚀 核心价值：让身份认证回归简单与安全
Aegis Auth SDK 是一款面向现代 Web 应用的身份认证开发工具包，基于 **WebAuthn（FIDO2）标准**，帮助开发者快速构建**无密码（Passwordless）认证体系**，从根本上规避传统密码机制带来的安全风险与用户体验问题。

---

## 🌟 核心优势

### 1. 极致的开发体验
- **开箱即用**：支持 `pip` 一键安装，无需复杂环境配置  
- **高度封装**：屏蔽 WebAuthn 底层交互细节，仅需少量代码即可完成接入  
- **快速集成**：分钟级完成用户注册与登录能力接入  

---

### 2. 安全合规的无密码方案
- **彻底去密码化**：无需用户记忆或输入密码，有效防御撞库与钓鱼攻击  
- **敏感数据最小化**：服务端仅存储公钥，不涉及生物特征原始数据  
- **抗自动化攻击**：基于挑战-响应机制，天然抵御暴力破解与批量注册  

---

### 3. 跨平台与生物识别支持
- **全平台兼容**：
  - Windows Hello  
  - macOS Touch ID  
  - iOS / Android（Face ID / 指纹）  
- **设备级强绑定**：实现“用户 + 设备”双因子绑定，确保操作主体可信  

---

### 4. 企业级用户管理能力
- **统一用户视图**：支持凭证管理、设备解绑、状态控制等  
- **审计与日志**：完整认证日志，便于安全审计与追踪  
- **SSO 友好**：支持快速对接企业统一身份认证体系（如 yiducloud.cn）  

---

## 🛠 快速上手

### SDK 示例

```python
from aegis_auth_sdk import AegisClient

client = AegisClient(
    base_url="https://your-server:8000",
    app_id="your_app_id",
    secret_key="your_secret_key"
)

# 获取应用信息
info = client.get_app_info()
print(info)

# 获取用户列表
users = client.get_users()
for user in users["users"]:
    print(f'{user["username"]} - 状态: {user["status"]}')

# 禁用用户
client.set_user_status("alice", False)

# 删除用户
client.delete_user("alice")

# 查询日志
logs = client.get_logs(page=1, page_size=10, log_type="auth_verify")
```

---

## 接入示例

### 前端示例

```javascript
const API_BASE = "https://your-server:8000/api";
const APP_ID   = "your_app_id";

// ── 用户注册 ──
async function registerUser(username) {
  // 1. 获取注册选项
  const resp = await fetch(`${API_BASE}/registration/${APP_ID}/${username}/options`, { method: "POST" });
  const options = await resp.json();

  // 2. 处理 challenge 和 user.id（Base64URL → ArrayBuffer）
  options.challenge = base64urlToBuffer(options.challenge);
  options.user.id   = base64urlToBuffer(options.user.id);

  // 3. 调用浏览器 WebAuthn API
  const credential = await navigator.credentials.create({ publicKey: options });

  // 4. 序列化并发送验证
  const body = {
    id:    credential.id,
    rawId: bufferToBase64url(credential.rawId),
    type:  credential.type,
    response: {
      clientDataJSON:    bufferToBase64url(credential.response.clientDataJSON),
      attestationObject: bufferToBase64url(credential.response.attestationObject),
    }
  };

  const verifyResp = await fetch(
    `${API_BASE}/registration/${APP_ID}/${username}/verification`,
    { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }
  );
  return verifyResp.json(); // { verified: true }
}

// ── 用户认证 ──
async function authenticateUser(username) {
  // 1. 获取认证选项
  const resp = await fetch(`${API_BASE}/authentication/${APP_ID}/${username}/options`, { method: "POST" });
  const options = await resp.json();

  // 2. 处理 challenge（Base64URL → ArrayBuffer）
  options.challenge = base64urlToBuffer(options.challenge);
  if (options.allowCredentials) {
    options.allowCredentials = options.allowCredentials.map(c => ({
      ...c, id: base64urlToBuffer(c.id)
    }));
  }

  // 3. 调用浏览器 WebAuthn API
  const credential = await navigator.credentials.get({ publicKey: options });

  // 4. 序列化并发送验证
  const body = {
    id:    credential.id,
    rawId: bufferToBase64url(credential.rawId),
    type:  credential.type,
    response: {
      clientDataJSON:    bufferToBase64url(credential.response.clientDataJSON),
      authenticatorData: bufferToBase64url(credential.response.authenticatorData),
      signature:         bufferToBase64url(credential.response.signature),
      userHandle:        credential.response.userHandle
                           ? bufferToBase64url(credential.response.userHandle) : null,
    }
  };

  const verifyResp = await fetch(
    `${API_BASE}/authentication/${APP_ID}/${username}/verification`,
    { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }
  );
  return verifyResp.json(); // { verified: true }
}

// ── Base64URL 工具函数 ──
function base64urlToBuffer(b64url) {
  const base64 = b64url.replace(/-/g, "+").replace(/_/g, "/");
  const padded = base64.padEnd(Math.ceil(base64.length / 4) * 4, "=");
  const binary = atob(padded);
  const bytes  = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
  return bytes.buffer;
}

function bufferToBase64url(buffer) {
  const bytes  = new Uint8Array(buffer);
  let binary = "";
  for (let i = 0; i < bytes.byteLength; i++) binary += String.fromCharCode(bytes[i]);
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=/g, "");
}

```

### 后端示例
```python
from aegis_auth_sdk import AegisClient

client = AegisClient(
    base_url="https://your-server:8000",
    app_id="6e7fd30dad894d7d8ca2e73ea4f285cb",
    secret_key="your_secret_key_here"
)

# 查看应用信息
print(client.get_app_info())

# 列出所有用户
result = client.get_users()
for user in result["users"]:
    print(f'  {user["username"]:<20} 状态={"启用" if user["status"] else "禁用"}  '
          f'注册时间={user["register_time"]}  最后登录={user["login_time"] or "从未"}')

# 禁用可疑用户
client.set_user_status("suspicious_user", False)

# 查询认证日志
logs = client.get_logs(log_type="auth_verify", page_size=5)
for entry in logs["items"]:
    print(f'  [{entry["log_time"]}] {entry["username"]} from {entry["log_ip"]} - {entry["log_info"]}')
```

## ⚠️ 错误码说明

| HTTP 状态码 | 含义       | 说明 |
|------------|------------|------|
| 200        | 成功       | 请求处理成功 |
| 400        | 请求错误   | 参数缺失或格式错误 |
| 401        | 认证失败   | App ID / Secret 错误或应用被禁用 |
| 404        | 未找到     | 资源不存在 |
| 500        | 服务器错误 | 服务端异常，请联系管理员 |

---

## 📦 错误响应格式

```json
{ "error": "错误描述信息" }
```

或：

```json
{ "detail": "错误描述信息" }
```
