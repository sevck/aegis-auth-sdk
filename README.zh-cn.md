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

## 🚀 核心价值：让身份认证回归简单与安全
Aegis Auth SDK 是一款面向现代 Web 应用的身份认证开发工具包，基于 **WebAuthn（FIDO2）标准**，帮助开发者快速构建**无密码（Passwordless）认证体系**，从根本上规避传统密码机制带来的安全风险与用户体验问题。

---

## 🌟 核心优势

### 1. 极致的开发体验
- **开箱即用**：支持 `pip` 一键SDK安装，无需复杂环境配置  
- **高度封装**: 优化底层交互细节，仅需少量代码即可完成接入  
- **快速集成**：分钟级完成用户注册与登录能力接入  

---

### 2. 安全合规的无密码方案
- **无密码**：无需用户输入密码，有效防御弱口令与密码泄露撞库攻击  
- **无敏感数据**：服务端仅存储公钥，不涉及生物特征原始数据，不存储任何敏感信息  
- **抗自动化攻击**：基于挑战-响应机制，天然抵御暴力破解与批量注册，可防止机器人攻击  

---

### 3. 跨平台支持
- **全平台兼容**：
  - Windows 10以上版本(Windows Hello)  
  - macOS Touch ID  
  - iOS / Android（Face ID / 指纹）  
- **设备级强绑定**：实现“用户 + 设备”双因子绑定，确保操作主体可信  

---

### 4. 企业级用户管理能力
- **统一用户视图**：支持用户列表、用户状态管理、应用注册管理等  
- **审计与日志**：完整认证日志，便于安全审计与追踪  

---

## 📦 环境要求

- **Python 2.7** 或 **Python 3.6+**
- 无第三方依赖，仅使用 Python 标准库

---

## 🛠 快速上手

### 安装

```bash
pip install aegis-auth-sdk
```

### SDK 示例

```python
from aegis_auth_sdk import AegisClient

client = AegisClient(
    base_url="https://your-server:8000",
    app_id="your_app_id",
    secret_key="your_secret_key"
)

# 获取应用信息
app_info = client.get_app_info()
print(app_info)

# 获取用户列表
result = client.get_users()
for user in result["users"]:
    print("%s  状态=%s  注册时间=%s  最后登录=%s" % (
        user["username"], "启用" if user["status"] else "禁用",
        user["register_time"], user["login_time"] or "从未"))

# 禁用/启用用户
client.set_user_status("alice", False)

# 禁用/启用应用注册
client.set_app_register(False)

# 启用/禁用多设备注册
client.set_app_multi_device(True)

# 删除用户
client.delete_user("alice")

# 查询日志
logs = client.get_logs(log_type="auth_verify", page_size=5)
for entry in logs["items"]:
    print("[%s] %s from %s - %s" % (
        entry["log_time"], entry["username"], entry["log_ip"], entry["log_info"]))
```

---

## 接入示例

### 前端示例

```javascript

export const fetchUserLoginOptions = (param) => {
    return request({
        url: '/api/user/login/options', // 你的服务后端API
        headers: {
            'Content-Type': 'application/json',
            'Login-Name': param.username,
        },
        method: 'post',
        data: param
    });
};

export const fetchUserLoginVerify = (username: string, asseResp: object) => {
    return request({
        url: '/api/user/login/verification', // 你的服务后端API
        method: 'post',
        headers: {
            'Content-Type': 'application/json',
            'Login-Name': username
        },
        data: asseResp
    });
};

const resp = await fetchUserLoginOptions(param);
const registrationOptions = resp.data;
const asseResp = await startAuthentication(registrationOptions);
const verificationResp = await fetchUserLoginVerify(param.username, asseResp);
const verificationJSON = verificationResp.data;

if (verificationJSON.code === 200) {
    ElMessage.success('登录成功');
    localStorage.setItem('username', param.username);
    localStorage.setItem(
        'Authorization',
        verificationJSON.token_type + ' ' + verificationJSON.access_token
    );

    router.push('/');

    if (checked.value) {
      localStorage.setItem('login-param', JSON.stringify(param));
    } else {
      localStorage.removeItem('login-param');
    }
  } else {
    ElMessage.error('登录失败');
  }
};


```

### 后端示例
```python
from aegis_auth_sdk import AegisClient

client = AegisClient(
    base_url="https://your-server:8000",
    app_id="your_app_id",
    secret_key="your_secret_key"
)


@user.post("/login/options", description="用户登录预请求")
async def user_login_options(req: dict, request: Request, db: Session = Depends(get_db)):
    try:
        headers = request.headers
        username = headers.get("Login-Name", None)
        # 获取登录options
        resp = client.get_login_options(username)

        return JSONResponse(status_code=resp.status_code, content=resp.json())
    except Exception as e:
        return JSONResponse(status_code=200, content={"code": 400, "msg": str(e)})


@user.post("/login/verification", description="用户登录验证")
async def user_login_verification(req: dict, request: Request, db: Session = Depends(get_db)):
    try:
        headers = request.headers
        username = headers.get("Login-Name", None)
        origin = headers.get("origin", None)
        if username is None or origin is None:
            return JSONResponse(status_code=200, content={"code": False, "msg": "Miss username or origin"})
        # 验证登录
        resp = client.get_login_verify(username, req)
        # 验证成功签发jwt token
        if resp.json().get("verified", False):
            token = jwt.encode({
                "user": username,
                "role": "admin",
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            }, SECRET_KEY, algorithm=algorithm).decode("utf-8")
            return JSONResponse(
              status_code=resp.status_code,
              content={"access_token": token, "token_type": "Bearer", "code": 200}
            )

        return JSONResponse(
          status_code=200,
          content={"code": 500, "username": username, "msg": resp.text}
        )
    except Exception as e:
        return HTTPException(status_code=200, detail={"code": 400, "msg": str(e)})


@user.post("/register/options", description="注册预请求")
async def user_register_options(req: dict, request: Request, db: Session = Depends(get_db)):
    try:
        headers = request.headers
        username = headers.get("Login-Name", None)
        # 获取注册options
        resp = client.get_register_options(username)
        return JSONResponse(status_code=resp.status_code, content=resp.json())
    except Exception as e:
        return JSONResponse(status_code=200, content={"code": 400, "msg": str(e)})

@user.post("/register/verification", description="注册验证")
async def user_register_verification(req: dict, request: Request, db: Session = Depends(get_db)):
    try:
        headers = request.headers
        username = headers.get("Login-Name", None)
        # 验证注册
        resp = client.get_register_verify(username, req)
        return JSONResponse(status_code=resp.status_code, content=resp.json())
    except Exception as e:
        return JSONResponse(status_code=200, content={"code": 400, "msg": str(e)})
```

## ⚠️ 错误码说明

| HTTP 状态码 | 含义       | 说明 |
|------------|------------|------|
| 200        | 成功       | 请求处理成功 |
| 400        | 请求错误   | 参数缺失或格式错误 |
| 401        | 认证失败   | App ID / Secret 错误或应用被禁用 |
| 403        | 禁止访问   | 应用已关闭注册，或 WebAuthn 验证未通过 |
| 404        | 未找到     | 资源不存在 |
| 500        | 服务器错误 | 服务端异常，请联系管理员 |

