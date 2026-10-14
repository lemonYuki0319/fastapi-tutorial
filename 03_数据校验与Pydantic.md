# 03 - 数据校验与 Pydantic

> 🎯 **学习目标**：掌握 Pydantic 模型定义、自动校验、自定义校验器

---

## 一、Pydantic 简介

### 1.1 什么是 Pydantic？

Pydantic 是 Python 数据校验库，使用 Python 类型注解进行数据校验和序列化。

**核心功能**：
- ✅ 自动类型转换
- ✅ 数据校验
- ✅ 错误提示
- ✅ 序列化/反序列化

### 1.2 为什么使用 Pydantic？

```python
# 传统方式：手动校验
def create_user(username, email, age):
    if not username:
        return {"error": "用户名不能为空"}
    if len(username) < 2 or len(username) > 50:
        return {"error": "用户名长度必须在2-50之间"}
    if not email or "@" not in email:
        return {"error": "邮箱格式错误"}
    if age is not None and (age < 0 or age > 150):
        return {"error": "年龄必须在0-150之间"}
    # ... 创建用户

# Pydantic 方式：自动校验
class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    age: Optional[int] = Field(None, ge=0, le=150)

def create_user(user: UserCreate):
    # 自动完成所有校验，直接使用数据
    pass
```

---

## 二、基本模型定义

### 2.1 简单模型

```python
from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    """用户模型"""
    id: int                    # 必填，int 类型
    username: str              # 必填，str 类型
    email: str                 # 必填，str 类型
    phone: Optional[str] = None  # 可选，默认 None
    is_active: bool = True     # 可选，默认 True
```

### 2.2 使用 Field 添加校验

```python
from pydantic import BaseModel, Field
from typing import Optional

class Product(BaseModel):
    """商品模型（带字段校验）"""
    name: str = Field(
        ...,                          # ... 表示必填
        min_length=1,                 # 最小长度
        max_length=100,               # 最大长度
        description="商品名称"         # 字段描述
    )
    
    price: float = Field(
        ...,
        gt=0,                         # 大于 0
        description="商品价格"
    )
    
    stock: int = Field(
        default=0,                    # 默认值
        ge=0,                         # 大于等于 0
        description="库存数量"
    )
    
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="商品描述"
    )
    
    category: str = Field(
        default="未分类",
        description="商品分类"
    )
```

### 2.3 Field 校验参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `...` | 必填字段 | `Field(...)` |
| `default` | 默认值 | `Field(default=0)` |
| `min_length` | 字符串最小长度 | `Field(min_length=2)` |
| `max_length` | 字符串最大长度 | `Field(max_length=50)` |
| `gt` | 大于 | `Field(gt=0)` |
| `ge` | 大于等于 | `Field(ge=0)` |
| `lt` | 小于 | `Field(lt=100)` |
| `le` | 小于等于 | `Field(le=100)` |
| `description` | 字段描述 | `Field(description="用户名")` |
| `example` | 示例值 | `Field(example="test")` |

---

## 三、特殊类型校验

### 3.1 邮箱校验

```python
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    """创建用户模型"""
    username: str
    email: EmailStr  # 自动校验邮箱格式
```

**测试**：
```python
# 有效邮箱
UserCreate(username="test", email="test@example.com")  # ✅ 成功

# 无效邮箱
UserCreate(username="test", email="invalid-email")  # ❌ 抛出异常
```

### 3.2 枚举类型

```python
from enum import Enum
from pydantic import BaseModel

class UserStatus(str, Enum):
    """用户状态枚举"""
    active = "active"
    inactive = "inactive"
    banned = "banned"


class ProductStatus(str, Enum):
    """商品状态枚举"""
    on_sale = "on_sale"
    off_sale = "off_sale"


class User(BaseModel):
    username: str
    status: UserStatus = UserStatus.active


class Product(BaseModel):
    name: str
    status: ProductStatus = ProductStatus.on_sale
```

### 3.3 列表和字典

```python
from pydantic import BaseModel
from typing import List, Dict, Optional

class Order(BaseModel):
    """订单模型"""
    order_id: str
    product_ids: List[int]           # 整数列表
    tags: List[str] = []             # 字符串列表，默认空列表
    metadata: Optional[Dict[str, str]] = None  # 字典类型
```

### 3.4 嵌套模型

```python
from pydantic import BaseModel
from typing import List

class Address(BaseModel):
    """地址模型"""
    province: str
    city: str
    detail: str


class User(BaseModel):
    """用户模型（嵌套地址）"""
    username: str
    email: str
    addresses: List[Address] = []  # 地址列表
```

**请求示例**：
```json
{
    "username": "testuser",
    "email": "test@example.com",
    "addresses": [
        {
            "province": "北京市",
            "city": "北京市",
            "detail": "朝阳区xxx街道"
        }
    ]
}
```

---

## 四、自定义校验器

### 4.1 field_validator（字段校验器）

```python
from pydantic import BaseModel, field_validator
import re

class UserCreate(BaseModel):
    """创建用户模型（自定义校验）"""
    username: str
    password: str
    phone: str
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """校验用户名：只允许字母、数字、下划线"""
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('用户名只能包含字母、数字、下划线')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """校验密码：至少8位，包含字母和数字"""
        if len(v) < 8:
            raise ValueError('密码长度不能少于8位')
        if not re.search(r'[a-zA-Z]', v):
            raise ValueError('密码必须包含字母')
        if not re.search(r'[0-9]', v):
            raise ValueError('密码必须包含数字')
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """校验手机号：中国大陆手机号"""
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式错误')
        return v
```

### 4.2 model_validator（模型校验器）

```python
from pydantic import BaseModel, model_validator
from typing import Optional

class RegisterUser(BaseModel):
    """注册用户模型（多字段联合校验）"""
    password: str
    confirm_password: str
    email: Optional[str] = None
    phone: Optional[str] = None
    
    @model_validator(mode='after')
    def validate_passwords_match(self):
        """校验两次密码是否一致"""
        if self.password != self.confirm_password:
            raise ValueError('两次密码输入不一致')
        return self
    
    @model_validator(mode='after')
    def validate_contact(self):
        """校验至少提供一种联系方式"""
        if not self.email and not self.phone:
            raise ValueError('邮箱和手机号至少填写一个')
        return self
```

---

## 五、请求模型与响应模型

### 5.1 分离请求和响应模型

```python
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

# 请求模型：创建用户
class UserCreate(BaseModel):
    """创建用户请求模型"""
    username: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    phone: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123",
                "phone": "13800138000"
            }
        }


# 请求模型：更新用户
class UserUpdate(BaseModel):
    """更新用户请求模型（所有字段可选）"""
    username: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "newusername",
                "phone": "13900139000"
            }
        }


# 响应模型：用户信息
class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: str
    email: str
    phone: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True  # 支持从 ORM 对象转换
```

### 5.2 隐藏敏感字段

```python
from pydantic import BaseModel

class UserInDB(BaseModel):
    """数据库中的用户模型"""
    id: int
    username: str
    email: str
    password: str      # 敏感字段
    salt: str          # 敏感字段


class UserResponse(BaseModel):
    """返回给前端的用户模型（隐藏敏感字段）"""
    id: int
    username: str
    email: str
    # 不包含 password 和 salt


# 使用示例
def get_user(user_id: int):
    user_db = get_user_from_db(user_id)  # 返回 UserInDB
    return UserResponse.model_validate(user_db)  # 自动过滤敏感字段
```

---

## 六、在 FastAPI 中使用

### 6.1 完整示例

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from datetime import datetime

app = FastAPI()

# 模拟数据库
fake_db = {}
user_id_counter = 1


# 定义模型
class UserCreate(BaseModel):
    """创建用户请求模型"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError('用户名只能包含字母和数字')
        return v


class UserUpdate(BaseModel):
    """更新用户请求模型"""
    username: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: str
    email: str
    phone: Optional[str]
    created_at: datetime


# 创建用户
@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate):
    """创建用户"""
    global user_id_counter
    
    # 检查用户名是否已存在
    for u in fake_db.values():
        if u['username'] == user.username:
            raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 创建用户
    user_data = {
        "id": user_id_counter,
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "created_at": datetime.now()
    }
    fake_db[user_id_counter] = user_data
    user_id_counter += 1
    
    return user_data


# 查询用户
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    """查询用户"""
    if user_id not in fake_db:
        raise HTTPException(status_code=404, detail="用户不存在")
    return fake_db[user_id]


# 更新用户
@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate):
    """更新用户"""
    if user_id not in fake_db:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 只更新传入的字段
    update_data = user.model_dump(exclude_unset=True)
    fake_db[user_id].update(update_data)
    
    return fake_db[user_id]
```

---

## 七、测试示例

### 7.1 正常请求测试

```bash
# 创建用户（正常数据）
curl -X POST "http://127.0.0.1:8000/users" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "phone": "13800138000"
  }'
```

### 7.2 参数校验测试

```bash
# 用户名过短
curl -X POST "http://127.0.0.1:8000/users" \
  -H "Content-Type: application/json" \
  -d '{"username": "a", "email": "test@example.com"}'
# 预期：422 错误

# 邮箱格式错误
curl -X POST "http://127.0.0.1:8000/users" \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "email": "invalid-email"}'
# 预期：422 错误

# 用户名包含特殊字符
curl -X POST "http://127.0.0.1:8000/users" \
  -H "Content-Type: application/json" \
  -d '{"username": "test@user", "email": "test@example.com"}'
# 预期：422 错误

# 缺少必填字段
curl -X POST "http://127.0.0.1:8000/users" \
  -H "Content-Type: application/json" \
  -d '{"username": "test"}'
# 预期：422 错误
```

### 7.3 更新测试

```bash
# 部分更新
curl -X PUT "http://127.0.0.1:8000/users/1" \
  -H "Content-Type: application/json" \
  -d '{"phone": "13900139000"}'

# 完整更新
curl -X PUT "http://127.0.0.1:8000/users/1" \
  -H "Content-Type: application/json" \
  -d '{"username": "newname", "email": "new@example.com", "phone": "13900139000"}'
```

---

## 八、测试要点

### 8.1 字段校验测试

| 测试项 | 测试值 | 预期结果 |
|--------|-------|---------|
| 必填字段缺失 | `{}` | 422 错误 |
| 字段类型错误 | `{"age": "abc"}` | 422 错误 |
| 字符串长度不足 | `{"username": "a"}` | 422 错误 |
| 字符串长度超限 | `{"username": "a"*51}` | 422 错误 |
| 数值范围错误 | `{"age": -1}` | 422 错误 |
| 邮箱格式错误 | `{"email": "invalid"}` | 422 错误 |

### 8.2 自定义校验测试

| 测试项 | 测试值 | 预期结果 |
|--------|-------|---------|
| 用户名特殊字符 | `test@user` | 422 错误 |
| 密码过短 | `1234567` | 422 错误 |
| 密码无字母 | `12345678` | 422 错误 |
| 密码无数字 | `password` | 422 错误 |
| 手机号格式错误 | `12345678901` | 422 错误 |

---

## 九、常见问题

### Q1: 如何查看校验错误详情？

FastAPI 会自动返回详细的校验错误信息：

```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "String should have at least 2 characters",
      "type": "string_too_short"
    }
  ]
}
```

### Q2: 如何自定义错误消息？

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    username: str = Field(
        ..., 
        min_length=2, 
        max_length=50,
        json_schema_extra={"error_messages": {
            "too_short": "用户名太短了，至少2个字符",
            "too_long": "用户名太长了，最多50个字符"
        }}
    )
```

### Q3: 如何处理嵌套模型的校验？

嵌套模型会自动递归校验，无需额外处理。

---

**下一章**：[04_路径操作配置.md](./04_路径操作配置.md) →
