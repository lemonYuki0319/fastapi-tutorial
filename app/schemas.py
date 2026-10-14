"""
Pydantic 数据校验模型
"""
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from datetime import datetime


class ResponseModel(BaseModel):
    """统一响应格式"""
    code: int = Field(default=200, description="状态码")
    message: str = Field(default="success", description="提示信息")
    data: Optional[dict | list] = Field(default=None, description="返回数据")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class UserCreate(BaseModel):
    """创建用户请求模型"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    status: str = Field(default="active", description="状态")
    remark: Optional[str] = Field(None, description="备注")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v not in ['active', 'inactive']:
            raise ValueError('status 必须是 active 或 inactive')
        return v


class UserUpdate(BaseModel):
    """更新用户请求模型"""
    username: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    status: Optional[str] = None
    remark: Optional[str] = None


class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: str
    email: str
    phone: Optional[str]
    status: str
    is_admin: bool
    remark: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    """创建商品请求模型"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: int = Field(..., ge=0, description="价格（分）")
    stock: int = Field(default=0, ge=0)
    status: str = Field(default="on_sale")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v not in ['on_sale', 'off_sale']:
            raise ValueError('status 必须是 on_sale 或 off_sale')
        return v


class ProductUpdate(BaseModel):
    """更新商品请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    price: Optional[int] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=0)
    status: Optional[str] = None


class ProductResponse(BaseModel):
    """商品响应模型"""
    id: int
    name: str
    description: Optional[str]
    price: int
    stock: int
    status: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
